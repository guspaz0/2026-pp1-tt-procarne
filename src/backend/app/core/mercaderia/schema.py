"""Schemas (DTOs) de la mercadería."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class MercaderiaIn(BaseModel):
    """DTO de entrada para crear una mercadería."""

    codigo: str = Field(..., description="Código AFIP del producto")
    descripcion: str = Field(..., description="Descripción del producto")
    unidad_medida: Optional[str] = Field(None, description="Unidad de medida (KG, UN, etc.)")
    requiere_trazabilidad: bool = Field(False, description="¿Requiere trazabilidad?")
    requiere_numero_tropa: bool = Field(False, description="¿Requiere número de tropa?")


class MercaderiaOut(BaseModel):
    """DTO de salida de una mercadería."""

    id: int
    codigo: str
    descripcion: str
    unidad_medida: Optional[str]
    requiere_trazabilidad: bool
    requiere_numero_tropa: bool

    model_config = {"from_attributes": True}
