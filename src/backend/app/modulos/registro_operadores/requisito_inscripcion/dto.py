"""DTOs (schemas Pydantic) de ``RequisitoInscripcion``."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RequisitoInscripcionIn(BaseModel):
    """DTO de entrada para registrar un requisito de inscripción."""

    codigo: str = Field(..., description="Código del requisito (ej: INGRESOS_BRUTOS, REGISTRO_NACIONAL_FRIGORIFICOS)")
    descripcion: Optional[str] = Field(None, description="Descripción del requisito")
    es_general: bool = Field(False, description="¿Es un requisito general (común a todas las categorías)?")
    cumplido: bool = Field(False, description="¿Está cumplido?")
    observaciones: Optional[str] = Field(None, description="Observaciones")


class RequisitoInscripcionOut(BaseModel):
    """DTO de salida de un requisito de inscripción."""

    id: int
    operador_id: int
    codigo: str
    descripcion: Optional[str]
    es_general: bool
    cumplido: bool
    fecha_cumplimiento: Optional[datetime]
    observaciones: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}
