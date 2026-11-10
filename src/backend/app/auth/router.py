"""Router de autenticación de ROCCA (BFF → InsForge).

Endpoints (todos bajo ``/api/auth``):
- ``POST /api/auth/login``    → login por email+contraseña, fija cookies HttpOnly.
- ``POST /api/auth/signup``   → alta de usuario (con API key admin), fija cookies.
- ``POST /api/auth/refresh``  → renueva la sesión con el refresh token.
- ``POST /api/auth/logout``   → cierra sesión en InsForge y limpia cookies.
- ``GET  /api/auth/me``       → datos del usuario autenticado (ruta protegida).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from starlette.status import HTTP_401_UNAUTHORIZED

from auth import schemas
from auth.dependencies import require_user
from auth.service import AuthError, AuthService


def crear_router(get_auth_service) -> APIRouter:
    """Crea el router de autenticación.

    :param get_auth_service: callable que devuelve el ``AuthService`` (Depends).
    """
    router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

    @router.post("/login", response_model=schemas.SessionOut)
    async def login(payload: schemas.LoginRequest, response: Response, auth: AuthService = Depends(get_auth_service)):
        from fastapi import HTTPException
        try:
            return await auth.login(payload.email, payload.password, response)
        except AuthError as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    @router.post("/signup", response_model=schemas.SessionOut, status_code=201)
    async def signup(payload: schemas.SignupRequest, response: Response, auth: AuthService = Depends(get_auth_service)):
        try:
            return await auth.signup(
                payload.email,
                payload.password,
                response,
                name=payload.name,
                metadata=payload.user_metadata,
            )
        except AuthError as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    @router.post("/refresh", response_model=schemas.SessionOut)
    async def refresh(request: Request, response: Response, auth: AuthService = Depends(get_auth_service)):
        from auth.service import COOKIE_REFRESH
        token = request.cookies.get(COOKIE_REFRESH) or ""
        try:
            return await auth.refresh(token, response)
        except AuthError as e:
            from fastapi import HTTPException
            raise HTTPException(status_code=e.status_code, detail=e.detail)

    @router.post("/logout")
    async def logout(request: Request, response: Response, auth: AuthService = Depends(get_auth_service)):
        from auth.service import COOKIE_REFRESH
        token = request.cookies.get(COOKIE_REFRESH)
        return await auth.logout(response, refresh_token=token)

    @router.get("/me")
    async def me(user: schemas.UserOut = Depends(require_user)):
        """Datos del usuario autenticado (ruta protegida)."""
        return user

    return router
