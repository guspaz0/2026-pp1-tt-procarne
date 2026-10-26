"""Schemas (DTOs) del operador de la cadena cárnica."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OperadorIn(BaseModel):
    """DTO de entrada para crear un operador."""

    persona_id: int = Field(..., description="ID de la persona asociada")


class OperadorOut(BaseModel):
    """DTO de salida de un operador."""

    id: int
    persona_id: int
    creado_en: datetime

    model_config = {"from_attributes": True}
