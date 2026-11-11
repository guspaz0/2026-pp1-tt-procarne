"""DTOs (schemas Pydantic) del catálogo de actividades económicas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class GrupoActividadOut(BaseModel):
    """DTO de salida de un grupo de actividad económica."""

    id: int
    codigo: str
    descripcion: str

    model_config = {"from_attributes": True}


class SubgrupoActividadOut(BaseModel):
    """DTO de salida de un subgrupo de actividad económica."""

    id: int
    codigo: str
    descripcion: str
    grupo_id: int

    model_config = {"from_attributes": True}


class ActividadEconomicaOut(BaseModel):
    """DTO de salida de una actividad económica."""

    id: int
    codigo: str
    descripcion: str
    alicuota: Optional[float]
    grupo_id: int
    subgrupo_id: Optional[int]

    model_config = {"from_attributes": True}
