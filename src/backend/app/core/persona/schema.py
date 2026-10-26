"""Schemas (DTOs) de la persona."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PersonaIn(BaseModel):
    """DTO de entrada para crear una persona."""

    tipo: str = Field(..., description="FISICA o JURIDICA")
    tipo_documento: str = Field(..., description="DNI, CUIT, etc.")
    identificador: str = Field(..., description="Número de documento")
    nombre: str = Field(..., description="Nombre o razón social")
    domicilio: Optional[str] = Field(None, description="Domicilio")


class PersonaOut(BaseModel):
    """DTO de salida de una persona."""

    id: int
    tipo: str
    tipo_documento: str
    identificador: str
    nombre: str
    domicilio: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}
