"""Schemas (DTOs) de la persona."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class DomicilioOut(BaseModel):
    """DTO de salida de un domicilio estructurado."""

    id: int
    calle: str
    numero: Optional[str]
    localidad: str
    provincia: str
    codigo_postal: Optional[str]

    model_config = {"from_attributes": True}


class PersonaIn(BaseModel):
    """DTO de entrada para crear una persona."""

    tipo: str = Field(..., description="FISICA o JURIDICA")
    tipo_documento: str = Field(..., description="DNI, CUIT, etc.")
    identificador: str = Field(..., description="Número de documento")
    nombre: str = Field(..., description="Nombre o razón social")
    email: Optional[str] = Field(None, description="Correo electrónico de contacto")


class PersonaOut(BaseModel):
    """DTO de salida de una persona."""

    id: int
    tipo: str
    tipo_documento: str
    identificador: str
    nombre: str
    email: Optional[str] = Field(None, description="Correo electrónico de contacto")
    domicilio: Optional[DomicilioOut] = Field(None, description="Domicilio (estructurado)")
    creado_en: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _mapear_domicilio(cls, data):
        """Mapea ``domicilio_rel`` (relación ORM) a ``domicilio`` para el DTO."""
        if isinstance(data, dict):
            if data.get("domicilio") is None and data.get("domicilio_rel") is not None:
                data["domicilio"] = data["domicilio_rel"]
            return data
        # Objeto ORM: expone ``domicilio_rel``; Pydantic lo serializa vía from_attributes.
        try:
            if getattr(data, "domicilio", None) is None and getattr(data, "domicilio_rel", None) is not None:
                data.domicilio = data.domicilio_rel
        except Exception:
            pass
        return data
