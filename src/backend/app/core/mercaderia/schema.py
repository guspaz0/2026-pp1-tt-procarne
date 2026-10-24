"""Schemas (DTOs) de la mercadería."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class MercaderiaIn(BaseModel):
    """Datos de entrada para crear una mercadería en el catálogo."""

    codigo: str
    descripcion: str
    unidad_medida: Optional[str] = None
    requiere_trazabilidad: bool = False
    requiere_numero_tropa: bool = False


class MercaderiaOut(BaseModel):
    """DTO de salida de la mercadería."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    descripcion: str
    unidad_medida: Optional[str] = None
    requiere_trazabilidad: bool
    requiere_numero_tropa: bool
