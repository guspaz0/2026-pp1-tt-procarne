"""DTOs (schemas Pydantic) de ``DomicilioOperativo``."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DomicilioOperativoIn(BaseModel):
    """DTO de entrada para crear un domicilio operativo."""

    direccion: str = Field(..., description="Dirección")
    localidad: Optional[str] = Field(None, description="Localidad")
    provincia: Optional[str] = Field(None, description="Provincia")
    codigo_postal: Optional[str] = Field(None, description="Código postal")
    es_principal: bool = Field(False, description="¿Es el domicilio principal?")


class DomicilioOperativoOut(BaseModel):
    """DTO de salida de un domicilio operativo."""

    id: int
    operador_id: int
    tipo: str
    direccion: str
    localidad: Optional[str]
    provincia: Optional[str]
    codigo_postal: Optional[str]
    es_principal: bool

    model_config = {"from_attributes": True}
