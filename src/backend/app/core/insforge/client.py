"""Cliente HTTP mínimo para InsForge (IdP + base de datos).

InsForge es un backend similar a Supabase:
- ``/api/auth/*``  → autenticación (registro, login, refresh, logout, get-session).
- ``/api/database/records/*`` → API REST sobre tablas PostgreSQL con RLS.

No usamos ``httpx`` ni ``requests`` (no están disponibles en este entorno):
el cliente se construye sobre ``http.client`` (stdlib) y se envuelve en
``asyncio.to_thread`` para no bloquear el event loop de FastAPI.

Referencia: https://docs.insforge.dev/sdks/rest/auth

**client_type=server**: FastAPI es un BFF (Backend-for-Frontend). Usamos
``client_type=server`` para que InsForge devuelva el ``refreshToken`` en el
cuerpo JSON (no en cookie httpOnly), y así el BFF pueda guardarlo en su
propia cookie HttpOnly para el frontend.

**Auth headers**:
- Auth endpoints (login/signup/refresh/logout): sin auth (públicos) o con
  ``Authorization: Bearer <jwt>`` para operaciones autenticadas.
- Database records: ``Authorization: Bearer <jwt>`` (RLS por usuario).
- Admin endpoints: ``Authorization: Bearer <api_key>`` (``ik_...``).
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from http.client import HTTPConnection, HTTPSConnection
from typing import Any
from urllib.parse import urlparse

DEFAULT_TIMEOUT = 15.0
CLIENT_TYPE = "server"  # BFF: recibimos refreshToken en el body.


class InsforgeError(Exception):
    """Error de comunicación o de respuesta de InsForge."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"InsForge {status_code}: {detail}")


@dataclass
class InsforgeSession:
    """Sesión de InsForge (tokens + usuario)."""

    access_token: str
    refresh_token: str | None = None
    csrf_token: str | None = None
    user: dict[str, Any] = field(default_factory=dict)


class InsforgeClient:
    """Cliente asíncrono para InsForge (auth + database records)."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = (base_url or os.environ.get("INSFORGE_URL", "https://localhost:3000")).rstrip("/")
        self.api_key = api_key or os.environ.get("INSFORGE_API_KEY", "")
        self.timeout = timeout
        self._parsed = urlparse(self.base_url)

    # ------------------------------------------------------------------ #
    # HTTP core
    # ------------------------------------------------------------------ #

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        user_token: str | None = None,
        admin: bool = False,
        extra_headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, Any] | list[Any] | str]:
        """Ejecuta una petición HTTP síncrona (se llama vía to_thread)."""
        query = ""
        if params:
            query = "?" + "&".join(f"{k}={v}" for k, v in params.items())

        url = f"{path}{query}"
        body = json.dumps(json_body).encode("utf-8") if json_body else None

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        elif admin and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if extra_headers:
            headers.update(extra_headers)

        conn_cls = HTTPSConnection if self._parsed.scheme == "https" else HTTPConnection
        try:
            conn = conn_cls(self._parsed.hostname, self._parsed.port or (443 if self._parsed.scheme == "https" else 80), timeout=self.timeout)
            conn.request(method, url, body=body, headers=headers)
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
            conn.close()
        except (OSError, ConnectionError, TimeoutError) as e:
            raise InsforgeError(0, f"No se pudo contactar InsForge: {e}") from e

        if not raw:
            return status, {}
        try:
            return status, json.loads(raw)
        except json.JSONDecodeError:
            return status, raw

    async def _request_async(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        user_token: str | None = None,
        admin: bool = False,
        extra_headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, Any] | list[Any] | str]:
        return await asyncio.to_thread(
            self._request,
            method,
            path,
            json_body=json_body,
            params=params,
            user_token=user_token,
            admin=admin,
            extra_headers=extra_headers,
        )

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        user_token: str | None = None,
        admin: bool = False,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        status, data = await self._request_async(
            method,
            path,
            json_body=json_body,
            params=params,
            user_token=user_token,
            admin=admin,
            extra_headers=extra_headers,
        )
        if status >= 400:
            detail = data if isinstance(data, str) else self._extract_error(data)
            raise InsforgeError(status, detail)
        return data if isinstance(data, dict) else {"data": data}

    @staticmethod
    def _extract_error(data: Any) -> str:
        """Extrae el mensaje de error de una respuesta de InsForge.

        InsForge devuelve: {"error": "USER_EXISTS", "message": "...", "statusCode": 409, "nextActions": "..."}
        """
        if isinstance(data, dict):
            return data.get("message") or data.get("error") or json.dumps(data)
        return str(data)

    # ------------------------------------------------------------------ #
    # Auth endpoints
    # https://docs.insforge.dev/sdks/rest/auth
    # ------------------------------------------------------------------ #

    async def sign_in_with_password(self, email: str, password: str) -> InsforgeSession:
        """Login con email + password.

        ``POST /api/auth/sessions?client_type=server``
        Body: ``{"method": "password", "email": "...", "password": "..."}``

        Response (server): ``{"user": {...}, "accessToken": "...", "refreshToken": "...", "requireEmailVerification": false}``
        """
        data = await self._request_json(
            "POST",
            "/api/auth/sessions",
            json_body={"method": "password", "email": email, "password": password},
            params={"client_type": CLIENT_TYPE},
        )
        return self._parse_session(data)

    async def create_user(
        self,
        email: str,
        password: str,
        *,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InsforgeSession:
        """Registro de usuario.

        ``POST /api/auth/users?client_type=server``
        Body: ``{"email": "...", "password": "...", "name": "..."}``

        Response (server): ``{"user": {...}, "accessToken": "...", "refreshToken": "...", "requireEmailVerification": false}``
        """
        body: dict[str, Any] = {"email": email, "password": password}
        if name:
            body["name"] = name
        if metadata:
            body["user_metadata"] = metadata

        data = await self._request_json(
            "POST",
            "/api/auth/users",
            json_body=body,
            params={"client_type": CLIENT_TYPE},
            admin=True,
        )
        return self._parse_session(data)

    async def refresh_session(self, refresh_token: str) -> InsforgeSession:
        """Refresca el access token.

        ``POST /api/auth/refresh?client_type=server``
        Body: ``{"refreshToken": "..."}``
        """
        data = await self._request_json(
            "POST",
            "/api/auth/refresh",
            json_body={"refreshToken": refresh_token},
            params={"client_type": CLIENT_TYPE},
        )
        return self._parse_session(data)

    async def sign_out(self, refresh_token: str | None = None) -> None:
        """Logout: borra la sesión.

        ``POST /api/auth/logout``

        Para server: enviamos el refreshToken en el body.
        """
        body = {"refreshToken": refresh_token} if refresh_token else None
        await self._request_json(
            "POST",
            "/api/auth/logout",
            json_body=body,
            params={"client_type": CLIENT_TYPE},
        )

    async def get_current_session(self, access_token: str) -> dict[str, Any]:
        """Obtiene el usuario de la sesión actual.

        ``GET /api/auth/sessions/current``
        Header: ``Authorization: Bearer <access_token>``

        Response: ``{"user": {...}, "accessToken": "...", ...}``
        """
        data = await self._request_json(
            "GET",
            "/api/auth/sessions/current",
            user_token=access_token,
        )
        return data

    # ------------------------------------------------------------------ #
    # Database records (RLS por usuario)
    # ------------------------------------------------------------------ #

    async def get_records(
        self,
        table: str,
        *,
        user_token: str,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Lista registros de una tabla con RLS del usuario."""
        params: dict[str, str] = {"client_type": CLIENT_TYPE}
        if filters:
            params["filter"] = json.dumps(filters)
        if order_by:
            params["order"] = order_by
        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)

        data = await self._request_json(
            "GET",
            f"/api/database/records/{table}",
            params=params,
            user_token=user_token,
        )
        return data.get("data", data.get("records", []))

    async def create_record(
        self,
        table: str,
        data: dict[str, Any],
        *,
        user_token: str,
    ) -> dict[str, Any]:
        """Crea un registro en la tabla (RLS del usuario)."""
        result = await self._request_json(
            "POST",
            f"/api/database/records/{table}",
            json_body=data,
            params={"client_type": CLIENT_TYPE},
            user_token=user_token,
        )
        return result.get("data", result)

    async def update_record(
        self,
        table: str,
        record_id: str,
        data: dict[str, Any],
        *,
        user_token: str,
    ) -> dict[str, Any]:
        """Actualiza un registro (RLS del usuario)."""
        result = await self._request_json(
            "PATCH",
            f"/api/database/records/{table}/{record_id}",
            json_body=data,
            params={"client_type": CLIENT_TYPE},
            user_token=user_token,
        )
        return result.get("data", result)

    async def delete_record(
        self,
        table: str,
        record_id: str,
        *,
        user_token: str,
    ) -> None:
        """Elimina un registro (RLS del usuario)."""
        await self._request_json(
            "DELETE",
            f"/api/database/records/{table}/{record_id}",
            params={"client_type": CLIENT_TYPE},
            user_token=user_token,
        )

    # ------------------------------------------------------------------ #
    # Parsing
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_session(data: dict[str, Any]) -> InsforgeSession:
        """Extrae tokens y usuario de la respuesta de auth de InsForge.

        InsForge devuelve (camelCase):
        {
          "user": { "id": "...", "email": "...", "emailVerified": false, ... },
          "accessToken": "eyJ...",
          "refreshToken": "eyJ...",          # solo client_type != web
          "csrfToken": "abc123...",          # solo client_type == web
          "requireEmailVerification": false
        }
        """
        return InsforgeSession(
            access_token=data.get("accessToken", ""),
            refresh_token=data.get("refreshToken"),
            csrf_token=data.get("csrfToken"),
            user=data.get("user") or {},
        )

    async def close(self) -> None:
        """Cierre (sin estado persistente en http.client)."""
        return None
