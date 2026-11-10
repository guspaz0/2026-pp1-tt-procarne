"""Dependencias de FastAPI para la autenticación.

Expone el usuario autenticado (resuelto por el middleware) a los routers.
Los routers usan ``Depends(get_current_user)`` para obtener el contexto del
usuario sin leer ``request.state`` directamente.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED

from auth.schemas import UserOut


def get_current_user(request: Request) -> UserOut:
    """Devuelve el usuario autenticado (resuelto por el middleware).

    En rutas protegidas el middleware ya garantizó que ``request.state.user``
    exista; en rutas públicas devuelve un ``UserOut`` vacío.
    """
    raw = request.state.user
    if not raw:
        return UserOut(id=None, email=None, user_metadata={})
    return UserOut(
        id=str(raw.get("id")) if raw.get("id") is not None else None,
        email=raw.get("email"),
        user_metadata=raw.get("user_metadata") or {},
    )


def require_user(request: Request) -> UserOut:
    """Como ``get_current_user`` pero exige autenticación (401 si no hay)."""
    raw = request.state.user
    if not raw:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return UserOut(
        id=str(raw.get("id")) if raw.get("id") is not None else None,
        email=raw.get("email"),
        user_metadata=raw.get("user_metadata") or {},
    )


def get_user_token(request: Request) -> str:
    """Devuelve el token de acceso de InsForge del usuario (para reenviar a la DB con RLS)."""
    token = getattr(request.state, "access_token", None)
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return token
