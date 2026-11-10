"""Servicio de autenticación ROCCA (InsForge como IdP).

Responsabilidades:
- Login: valida email/password contra InsForge y fija cookies HttpOnly.
- Signup: crea el usuario en InsForge (con API key administrativa) y fija cookies.
- Refresh: renueva el access token usando el refresh token.
- Logout: borra las cookies y notifica a InsForge.
- Validación: verifica el access token contra InsForge para el middleware.

Las cookies son **HttpOnly** (el frontend no puede leerlas) y el frontend
nunca ve los tokens: solo habla con FastAPI y el navegador envía las cookies
automáticamente.

Referencia: https://docs.insforge.dev/sdks/rest/auth
"""

from __future__ import annotations

from typing import Any

from fastapi import Response
from fastapi import status as http_status

from core.insforge.client import InsforgeClient, InsforgeError, InsforgeSession

# Nombres de cookies (HttpOnly).
COOKIE_ACCESS = "rocca_access_token"
COOKIE_REFRESH = "rocca_refresh_token"
COOKIE_MAX_AGE = 7 * 24 * 3600  # 7 días (el access token expira antes; el refresh lo renueva).


class AuthError(Exception):
    """Error de autenticación con status HTTP para el cliente."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class AuthService:
    """Orquesta la autenticación contra InsForge."""

    def __init__(self, client: InsforgeClient, cookie_secure: bool = True) -> None:
        self._client = client
        self._cookie_secure = cookie_secure

    # ------------------------------------------------------------------ #
    # Helpers de cookies
    # ------------------------------------------------------------------ #

    def _set_cookies(self, response: Response, session: InsforgeSession) -> None:
        """Fija las cookies HttpOnly en la respuesta."""
        response.set_cookie(
            COOKIE_ACCESS,
            session.access_token,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            secure=self._cookie_secure,
            samesite="lax",
            path="/",
        )
        if session.refresh_token:
            response.set_cookie(
                COOKIE_REFRESH,
                session.refresh_token,
                max_age=COOKIE_MAX_AGE,
                httponly=True,
                secure=self._cookie_secure,
                samesite="lax",
                path="/api/auth/refresh",
            )

    def _clear_cookies(self, response: Response) -> None:
        """Borra las cookies de sesión."""
        response.delete_cookie(COOKIE_ACCESS, path="/")
        response.delete_cookie(COOKIE_REFRESH, path="/api/auth/refresh")

    # ------------------------------------------------------------------ #
    # Operaciones
    # ------------------------------------------------------------------ #

    async def login(
        self, email: str, password: str, response: Response
    ) -> dict[str, Any]:
        """Login con email + password.

        ``POST /api/auth/sessions?client_type=server``
        """
        try:
            session = await self._client.sign_in_with_password(email, password)
        except InsforgeError as e:
            if e.status_code == 0:
                raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo contactar InsForge")
            if e.status_code == 401:
                raise AuthError(http_status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
            if e.status_code == 403:
                raise AuthError(http_status.HTTP_403_FORBIDDEN, "Verificá tu email antes de iniciar sesión")
            raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "Error de autenticación")

        if not session.access_token:
            raise AuthError(http_status.HTTP_401_UNAUTHORIZED, "No se pudo obtener el token de sesión")

        self._set_cookies(response, session)
        return self._session_payload(session)

    async def signup(
        self,
        email: str,
        password: str,
        response: Response,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Alta de usuario en InsForge.

        ``POST /api/auth/users?client_type=server``

        Si ``requireEmailVerification`` es true, InsForge no devuelve tokens
        y el usuario debe verificar su email antes de poder loguearse.
        """
        try:
            session = await self._client.create_user(
                email, password, name=name, metadata=metadata
            )
        except InsforgeError as e:
            if e.status_code == 0:
                raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo contactar InsForge")
            if e.status_code == 409:
                raise AuthError(http_status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese email")
            if e.status_code in (400, 422):
                raise AuthError(http_status.HTTP_400_BAD_REQUEST, e.detail)
            raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo crear el usuario")

        # Si InsForge requiere verificación de email, no hay tokens.
        if not session.access_token:
            return {
                "access_token": "",
                "refresh_token": None,
                "user": session.user,
                "require_email_verification": True,
            }

        self._set_cookies(response, session)
        return self._session_payload(session)

    async def refresh(self, refresh_token: str, response: Response) -> dict[str, Any]:
        """Renueva el access token.

        ``POST /api/auth/refresh?client_type=server``
        """
        try:
            session = await self._client.refresh_session(refresh_token)
        except InsforgeError as e:
            if e.status_code == 0:
                raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo contactar InsForge")
            if e.status_code in (400, 401):
                raise AuthError(http_status.HTTP_401_UNAUTHORIZED, "Sesión expirada, iniciá sesión de nuevo")
            raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo renovar la sesión")

        if not session.access_token:
            raise AuthError(http_status.HTTP_401_UNAUTHORIZED, "No se pudo obtener el token renovado")

        self._set_cookies(response, session)
        return self._session_payload(session)

    async def logout(self, response: Response, refresh_token: str | None = None) -> None:
        """Cierra la sesión: borra cookies y notifica a InsForge."""
        # Mejor esfuerzo: avisar a InsForge (no bloquea el logout local).
        if refresh_token:
            try:
                await self._client.sign_out(refresh_token)
            except InsforgeError:
                pass
        self._clear_cookies(response)

    async def validate_access_token(self, access_token: str) -> dict[str, Any] | None:
        """Verifica el access token contra InsForge.

        ``GET /api/auth/sessions/current``

        Devuelve el usuario si el token es válido; ``None`` si no.
        Lanza ``AuthError(503)`` si InsForge no está disponible.
        """
        try:
            data = await self._client.get_current_session(access_token)
        except InsforgeError as e:
            if e.status_code == 0:
                raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "No se pudo contactar InsForge")
            if e.status_code in (400, 401):
                return None  # Token inválido o expirado.
            raise AuthError(http_status.HTTP_503_SERVICE_UNAVAILABLE, "Error al validar la sesión")

        user = data.get("user")
        if not user:
            return None
        return user

    # ------------------------------------------------------------------ #
    # Payload
    # ------------------------------------------------------------------ #

    @staticmethod
    def _session_payload(session: InsforgeSession) -> dict[str, Any]:
        """Construye el payload de respuesta (snake_case para el frontend)."""
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "user": session.user,
        }
