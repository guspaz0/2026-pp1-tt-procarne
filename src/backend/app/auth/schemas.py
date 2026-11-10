"""Schemas (DTOs) de la API de autenticación de ROCCA."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credenciales para el login."""

    email: str = Field(..., description="Email")
    password: str = Field(..., min_length=8, description="Contraseña")


class SignupRequest(BaseModel):
    """Datos para el alta de usuario."""

    email: str = Field(..., description="Email")
    password: str = Field(..., min_length=8, description="Contraseña")
    name: Optional[str] = Field(None, description="Nombre del usuario")
    # Metadatos de usuario que se guardan en InsForge ``user_metadata``
    # (p. ej. persona_id). InsForge los expone en el JWT.
    user_metadata: Optional[dict[str, Any]] = Field(
        None, description="Metadatos adicionales (persona_id, etc.)"
    )


class RefreshRequest(BaseModel):
    """Refresh token (aunque viene por cookie, se acepta en el body opcional)."""

    refresh_token: Optional[str] = Field(None, description="Refresh token")


class SessionOut(BaseModel):
    """Resultado de login/signup/refresh.

    Refleja el modelo de respuesta de InsForge (camelCase en el usuario).
    """

    access_token: str
    refresh_token: Optional[str] = None
    user: dict[str, Any] = {}


class UserOut(BaseModel):
    """Usuario autenticado (desde request.state.user)."""

    id: Optional[str]
    email: Optional[str]
    user_metadata: dict[str, Any] = {}
