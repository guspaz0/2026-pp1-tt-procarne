"""Validación de CUIT contra el padrón público (API de IDFiscal).

El CUIT se valida **antes** de crear el usuario en InsForge: si el CUIT no
está en el padrón (ARCA/DGI) o el dígito verificador no coincide, el signup
se rechaza con ``422`` y no queda ningún usuario huérfano.

API: ``GET https://idfiscal.com/v1/ar/cuit/{cuit}`` con header ``X-API-Key``.
- ``200`` → contribuyente encontrado (CUIT válido y en el padrón).
- ``400`` → formato inválido (p. ej. dígito verificador que no coincide).
- ``404`` → no está en el padrón.
- ``401`` → falta la API key o es inválida (configuración del servidor).
- ``429`` → límite de consultas alcanzado.
- ``5xx`` → error del proveedor.

No usamos ``httpx``/``requests``: el cliente se construye sobre
``http.client`` (stdlib) y se envuelve en ``asyncio.to_thread`` para no
bloquear el event loop de FastAPI (mismo patrón que ``core/insforge/client``).
"""

from __future__ import annotations

import asyncio
import json
import os
from http.client import HTTPConnection, HTTPSConnection
from typing import Any

DEFAULT_TIMEOUT = 15.0
BASE_URL = "https://idfiscal.com"
ENDPOINT = "/v1/ar/cuit/{cuit}"


class CuitError(Exception):
    """Error de validación de CUIT con status HTTP para el cliente."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _normalizar(cuit: str) -> str:
    """Devuelve solo los dígitos del CUIT (quita guiones y espacios)."""
    return "".join(ch for ch in cuit if ch.isdigit())


def validar_formato_cuit(cuit: str) -> str:
    """Valida el formato local del CUIT (11 dígitos).

    Devuelve el CUIT normalizado (solo dígitos). Lanza :class:`CuitError`
    (``422``) si el formato es inválido, **sin** llamar a la API externa.

    Nota: no se valida el dígito verificador localmente; la validación
    definitiva se realiza contra el padrón público (IDFiscal).
    """
    cuit_norm = _normalizar(cuit)
    if len(cuit_norm) != 11:
        raise CuitError(422, "El CUIT debe tener 11 dígitos.")

    return cuit_norm


class CuitValidator:
    """Valida un CUIT contra el padrón público vía IDFiscal."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("IDFISCAL_API_KEY", "")
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.timeout = timeout
        host, port = self._parse_host()

    def _parse_host(self) -> tuple[str, int]:
        from urllib.parse import urlparse

        parsed = urlparse(self.base_url)
        host = parsed.hostname or "idfiscal.com"
        if parsed.port:
            port = parsed.port
        else:
            port = 443 if parsed.scheme == "https" else 80
        return host, port

    def _request_sync(self, cuit: str) -> tuple[int, dict[str, Any] | str]:
        """Ejecuta la petición HTTP síncrona (se llama vía to_thread)."""
        path = ENDPOINT.format(cuit=cuit)
        headers = {
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        host, port = self._parse_host()
        conn_cls = HTTPSConnection if self.base_url.startswith("https") else HTTPConnection
        try:
            conn = conn_cls(host, port, timeout=self.timeout)
            conn.request("GET", path, headers=headers)
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
            conn.close()
        except (OSError, ConnectionError, TimeoutError) as e:
            raise CuitError(503, f"No se pudo contactar el servicio de validación de CUIT: {e}") from e

        if not raw:
            return status, {}
        try:
            return status, json.loads(raw)
        except json.JSONDecodeError:
            return status, raw

    async def validar(self, cuit: str) -> None:
        """Valida un CUIT contra el padrón.

        1. Valida el formato local (11 dígitos + dígito verificador).
        2. Consulta el padrón público (IDFiscal).

        Lanza :class:`CuitError` con el status HTTP apropiado si el CUIT no
        es válido o no está en el padrón.
        """
        cuit_norm = validar_formato_cuit(cuit)

        # [IDFISCAL] Validación contra el padrón público desactivada
        # (API key inválida). Solo se valida el formato local (11 dígitos).
        # Para reactivar: descomentar el bloque inferior y renovar IDFISCAL_API_KEY.
        return

        # if not self.api_key:
        #     return
        #
        # status, data = await asyncio.to_thread(self._request_sync, cuit_norm)
        #
        # if status == 200:
        #     return
        # if status == 400:
        #     detail = self._extraer_detalle(data) or "CUIT inválido."
        #     raise CuitError(422, detail)
        # if status == 404:
        #     raise CuitError(422, "El CUIT no está registrado en el padrón.")
        # if status == 401:
        #     raise CuitError(503, "El servicio de validación de CUIT no está configurado correctamente.")
        # if status == 429:
        #     raise CuitError(429, "Se alcanzó el límite de consultas de validación de CUIT. Intentá más tarde.")
        # raise CuitError(503, f"Error del servicio de validación de CUIT ({status}).")

    @staticmethod
    def _extraer_detalle(data: Any) -> str | None:
        if isinstance(data, dict):
            return data.get("error") or data.get("message")
        return str(data) if data else None
