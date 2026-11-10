"""Cliente de storage de InsForge (bucket S3-compatible).

Implementa el flujo REST de InsForge para subir, descargar y borrar
archivos en un bucket privado:

1. Upload:
   - ``POST /api/storage/buckets/{bucket}/upload-strategy`` → obtiene URL
   - Si ``method=direct``: PUT binario a ``uploadUrl``
   - Si ``method=presigned``: POST multipart a ``uploadUrl`` + confirm

2. Download:
   - ``GET /api/storage/buckets/{bucket}/download-strategy/objects/{key}``
   → URL directa o presigned

3. Delete:
   - ``DELETE /api/storage/buckets/{bucket}/objects/{key}``

Referencia: https://docs.insforge.dev/llms.txt
"""

from __future__ import annotations

import asyncio
import json
import os
from http.client import HTTPConnection, HTTPSConnection
from typing import Any
from urllib.parse import urlparse

from core.insforge.client import InsforgeError

DEFAULT_TIMEOUT = 30.0  # Uploads pueden ser lentos (10 MB)


class InsforgeStorage:
    """Cliente asíncrono para el storage de InsForge."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        bucket: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = (base_url or os.environ.get("INSFORGE_URL", "https://localhost:3000")).rstrip("/")
        self.api_key = api_key or os.environ.get("INSFORGE_API_KEY", "")
        self.bucket = bucket or os.environ.get("INSFORGE_BUCKET", "rocca-documentos")
        self.timeout = timeout
        self._parsed = urlparse(self.base_url)

    # ------------------------------------------------------------------ #
    # HTTP core (síncrono, se llama vía to_thread)
    # ------------------------------------------------------------------ #

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_body: bytes | None = None,
    ) -> tuple[int, bytes]:
        """Ejecuta una petición HTTP síncrona."""
        hdrs = {
            "Accept": "application/json",
        }
        if self.api_key:
            hdrs["Authorization"] = f"Bearer {self.api_key}"
        if json_body is not None:
            hdrs["Content-Type"] = "application/json"
        if headers:
            hdrs.update(headers)

        body = raw_body
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")

        conn_cls = HTTPSConnection if self._parsed.scheme == "https" else HTTPConnection
        try:
            conn = conn_cls(
                self._parsed.hostname,
                self._parsed.port or (443 if self._parsed.scheme == "https" else 80),
                timeout=self.timeout,
            )
            conn.request(method, path, body=body, headers=hdrs)
            resp = conn.getresponse()
            raw = resp.read()
            status = resp.status
            conn.close()
        except (OSError, ConnectionError, TimeoutError) as e:
            raise InsforgeError(0, f"No se pudo contactar InsForge Storage: {e}") from e

        return status, raw

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        raw_body: bytes | None = None,
    ) -> tuple[int, dict[str, Any] | list[Any] | str]:
        status, raw = self._request(
            method, path, json_body=json_body, headers=headers, raw_body=raw_body
        )
        if not raw:
            return status, {}
        text = raw.decode("utf-8", errors="replace")
        try:
            return status, json.loads(text)
        except json.JSONDecodeError:
            return status, text

    # ------------------------------------------------------------------ #
    # API pública (async)
    # ------------------------------------------------------------------ #

    async def upload(
        self,
        filename: str,
        content_type: str,
        size: int,
        data: bytes,
    ) -> str:
        """Sube un archivo al bucket. Devuelve el storage_key.

        Flujo:
        1. POST upload-strategy → obtiene uploadUrl + method
        2. Si direct: PUT a uploadUrl
           Si presigned: POST multipart a uploadUrl + confirm-upload
        """
        # Paso 1: obtener estrategia de upload
        status, resp = await asyncio.to_thread(
            self._request_json,
            "POST",
            f"/api/storage/buckets/{self.bucket}/upload-strategy",
            json_body={
                "filename": filename,
                "contentType": content_type,
                "size": size,
            },
        )
        if status not in (200, 201):
            raise InsforgeError(status, f"upload-strategy falló: {resp}")

        strategy = resp if isinstance(resp, dict) else {}
        upload_url = strategy.get("uploadUrl", "")
        method = strategy.get("method", "direct")
        storage_key = strategy.get("key", "")
        fields = strategy.get("fields", {})

        if not upload_url:
            raise InsforgeError(500, "InsForge no devolvió uploadUrl")

        # Paso 2: subir el archivo
        if method == "presigned":
            await asyncio.to_thread(
                self._upload_presigned, upload_url, fields, filename, content_type, data
            )
            # Paso 3: confirmar
            confirm_path = strategy.get("confirmUrl", "")
            if confirm_path:
                status, resp = await asyncio.to_thread(
                    self._request_json, "POST", confirm_path, json_body={}
                )
                if status not in (200, 201, 204):
                    raise InsforgeError(status, f"confirm-upload falló: {resp}")
        else:
            # method=direct: PUT binario
            status, raw = await asyncio.to_thread(
                self._request,
                "PUT",
                upload_url,
                raw_body=data,
                headers={"Content-Type": content_type},
            )
            if status not in (200, 201, 204):
                raise InsforgeError(status, f"Upload directo falló: {raw[:200].decode(errors='replace')}")

        # Si InsForge no devolvió key, construimos una
        if not storage_key:
            import uuid
            ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
            storage_key = f"uploads/{uuid.uuid4()}.{ext}"

        return storage_key

    def _upload_presigned(
        self,
        upload_url: str,
        fields: dict[str, str],
        filename: str,
        content_type: str,
        data: bytes,
    ) -> None:
        """Sube un archivo usando un presigned URL con fields (multipart)."""
        import uuid as _uuid

        boundary = f"----InsForgeBoundary{_uuid.uuid4().hex}"
        lines: list[bytes] = []

        # Fields
        for key, value in fields.items():
            lines.append(f"--{boundary}\r\n".encode())
            lines.append(
                f'Content-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()
            )

        # File
        lines.append(f"--{boundary}\r\n".encode())
        lines.append(
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
        )
        lines.append(f"Content-Type: {content_type}\r\n\r\n".encode())
        lines.append(data)
        lines.append(b"\r\n")
        lines.append(f"--{boundary}--\r\n".encode())

        body = b"".join(lines)
        parsed = urlparse(upload_url)
        conn_cls = HTTPSConnection if parsed.scheme == "https" else HTTPConnection
        try:
            conn = conn_cls(
                parsed.hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                timeout=self.timeout,
            )
            path = parsed.path + ("?" + parsed.query if parsed.query else "")
            conn.request(
                "POST",
                path,
                body=body,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            )
            resp = conn.getresponse()
            resp.read()
            if resp.status not in (200, 201, 204):
                raise InsforgeError(resp.status, f"Presigned upload falló: {resp.status}")
            conn.close()
        except (OSError, ConnectionError, TimeoutError) as e:
            raise InsforgeError(0, f"Error en presigned upload: {e}") from e

    async def download_url(self, storage_key: str) -> str:
        """Obtiene una URL (directa o presigned) para descargar un archivo."""
        status, resp = await asyncio.to_thread(
            self._request_json,
            "GET",
            f"/api/storage/buckets/{self.bucket}/download-strategy/objects/{storage_key}",
        )
        if status != 200:
            raise InsforgeError(status, f"download-strategy falló: {resp}")

        if isinstance(resp, dict):
            return resp.get("url", "")
        return str(resp)

    async def delete(self, storage_key: str) -> None:
        """Borra un objeto del bucket."""
        status, resp = await asyncio.to_thread(
            self._request_json,
            "DELETE",
            f"/api/storage/buckets/{self.bucket}/objects/{storage_key}",
        )
        if status not in (200, 204):
            raise InsforgeError(status, f"Delete falló: {resp}")
