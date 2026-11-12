"""DTOs (schemas Pydantic) del catálogo de actividades económicas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class GrupoActividadOut(BaseModel):
    """DTO de salida de un grupo de actividad económica."""

    codigo: str
    descripcion: str

    model_config = {"from_attributes": True}


class SubgrupoActividadOut(BaseModel):
    """DTO de salida de un subgrupo de actividad económica."""

    codigo: str
    descripcion: str
    grupo_id: str

    model_config = {"from_attributes": True}


class SubSubgrupoActividadOut(BaseModel):
    """DTO de salida de un sub-subgrupo de actividad económica (3.er dígito)."""

    codigo: str
    descripcion: str
    grupo_id: str
    subgrupo_codigo: str

    model_config = {"from_attributes": True}


class ActividadEconomicaOut(BaseModel):
    """DTO de salida de una actividad económica.

    El ``codigo`` es el código DGR único de la actividad. El prefijo de
    grupo/subgrupo NO se incrusta en el código: se expone por separado como
    campos calculados (``codigo_grupo`` y ``codigo_subgrupo``), derivados de
    las FK del ORM al momento de construir el DTO.
    """

    id: int
    codigo: str
    descripcion: str
    grupo_id: str
    subgrupo_codigo: Optional[str] = None
    subsubgrupo_codigo: Optional[str] = None
    codigo_grupo: Optional[str] = None
    codigo_subgrupo: Optional[str] = None
    codigo_subsubgrupo: Optional[str] = None
    codigo_completo: Optional[str] = None

    model_config = {"from_attributes": True}
