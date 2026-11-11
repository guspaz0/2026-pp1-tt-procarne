"""Controlador (router API) del catálogo de actividades económicas.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).

Catálogo de solo lectura: no requiere servicio de negocio (el DAO expone
las lecturas directamente), por lo que no se define ``servicio.py``.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from modulos.registro_operadores.actividad_economica.dao import CatalogoActividadesDAO
from modulos.registro_operadores.actividad_economica.dto import (
    ActividadEconomicaOut,
    GrupoActividadOut,
    SubgrupoActividadOut,
)


def crear_router(dao: CatalogoActividadesDAO, prefix: str = "") -> APIRouter:
    """Crea el router API del catálogo de actividades económicas."""
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    @router.get("/catalogo/actividades/grupos", response_model=list[GrupoActividadOut])
    def catalogo_grupos():
        """Lista los grupos de actividades económicas (A, B, C, ...)."""
        return [GrupoActividadOut.model_validate(g) for g in dao.listar_grupos()]

    @router.get("/catalogo/actividades/subgrupos", response_model=list[SubgrupoActividadOut])
    def catalogo_subgrupos(grupo: str | None = Query(None, description="Filtrar por grupo")):
        """Lista los subgrupos de actividades económicas."""
        return [SubgrupoActividadOut.model_validate(s) for s in dao.listar_subgrupos(grupo=grupo)]

    @router.get("/catalogo/actividades", response_model=list[ActividadEconomicaOut])
    def catalogo_actividades(
        grupo: str | None = Query(None, description="Filtrar por grupo"),
        subgrupo: str | None = Query(None, description="Filtrar por subgrupo"),
    ):
        """Lista las actividades económicas (con alícuota)."""
        return [
            ActividadEconomicaOut.model_validate(a)
            for a in dao.listar_actividades(grupo=grupo, subgrupo=subgrupo)
        ]

    return router
