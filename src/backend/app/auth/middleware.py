"""Middleware de autenticación de ROCCA (InsForge como IdP).

Lee el token de acceso de la cookie ``access_token``, lo valida contra
InsForge (``GET /api/auth/get-session``) y adjunta el usuario autenticado a
``request.state``. Las rutas públicas (login, signup, refresh, logout, health)
pasan sin autenticación.

Diseño:
- **Validación centralizada**: cada petición a ruta protegida valida el token
  contra InsForge (una llamada de red por petición). Se puede optimizar luego
  con verificación local de JWT (JWKS) si InsForge expone las claves de firma.
- **Distingue** credenciales inválidas/vencidas (401) de fallos de red con
  InsForge (503).
"""

from __future__ import annotations

from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from auth.service import COOKIE_ACCESS, AuthError, AuthService


# Rutas públicas (no requieren autenticación).
PUBLIC_PATHS = {
    "/api/auth/login",
    "/api/auth/signup",
    "/api/auth/refresh",
    "/api/auth/logout",
    "/api/health",
    "/docs",
    "/docs/oauth2-redirect",
    "/openapi.json",
    "/redoc",
}

# Prefijos que también son públicos (SPA / assets).
PUBLIC_PREFIXES = (
    "/",  # El fallback SPA (index.html y assets) no pasa por validación.
)


def _is_public(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return True
    # El fallback SPA sirve index.html y assets (no son peticiones API).
    if not path.startswith("/api/"):
        return True
    return False


class InsForgeAuthMiddleware(BaseHTTPMiddleware):
    """Middleware de autenticación por cookie (token de InsForge)."""

    def __init__(self, app, auth_service: AuthService) -> None:
        super().__init__(app)
        self._auth = auth_service

    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        request.state.user = None
        request.state.access_token = None

        # Rutas públicas: pasan sin validar.
        if _is_public(request.url.path):
            return await call_next(request)

        token = request.cookies.get(COOKIE_ACCESS)
        if not token:
            return JSONResponse(
                {"detail": "Authentication required"},
                status_code=HTTP_401_UNAUTHORIZED,
            )

        # Valida el token contra InsForge.
        try:
            session = await self._auth.validate_access_token(token)
        except AuthError as e:
            if e.status_code == HTTP_503_SERVICE_UNAVAILABLE:
                return JSONResponse(
                    {"detail": "No se pudo validar la sesión (InsForge no disponible)"},
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                )
            return JSONResponse(
                {"detail": "Sesión inválida o vencida"},
                status_code=HTTP_401_UNAUTHORIZED,
            )

        if session is None:
            return JSONResponse(
                {"detail": "Sesión inválida o vencida"},
                status_code=HTTP_401_UNAUTHORIZED,
            )

        request.state.access_token = token
        request.state.user = session
        return await call_next(request)
