"""Schemas (DTOs) de la mercadería."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class MercaderiaIn(BaseModel):
    """Datos de entrada para crear una mercadería en el catálogo."""

    codigo_afip: str
    descripcion: str
    requiere_numero_tropa: bool = False


class MercaderiaOut(BaseModel):
    """DTO de salida de la mercadería."""

    id: int
    codigo_afip: str
    descripcion: str
    requiere_numero_tropa: bool
