"""DTOs (schemas Pydantic) de ``Habilitacion``."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HabilitacionIn(BaseModel):
    """DTO de entrada para crear una habilitación."""

    actividad: str = Field(..., description="Actividad habilitada")
    fecha_vencimiento: Optional[datetime] = Field(None, description="Fecha de vencimiento")


class HabilitacionOut(BaseModel):
    """DTO de salida de una habilitación."""

    id: int
    operador_id: int
    actividad: str
    estado: str
    fecha_habilitacion: Optional[datetime]
    fecha_vencimiento: Optional[datetime]

    model_config = {"from_attributes": True}
