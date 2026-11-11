"""DTOs (schemas Pydantic) de ``Inscripcion``."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InscripcionIn(BaseModel):
    """DTO de entrada para crear una inscripción."""

    tipo: str = Field("PRINCIPAL", description="Tipo de inscripción (PRINCIPAL, SECUNDARIA)")
    numero_inscripcion: Optional[str] = Field(None, description="Número de inscripción")


class InscripcionOut(BaseModel):
    """DTO de salida de una inscripción."""

    id: int
    operador_id: int
    tipo: str
    fecha_inscripcion: Optional[datetime]
    numero_inscripcion: Optional[str]

    model_config = {"from_attributes": True}
