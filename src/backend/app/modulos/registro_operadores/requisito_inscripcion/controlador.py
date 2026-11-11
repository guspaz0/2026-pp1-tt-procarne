"""Controlador (router API) de ``RequisitoInscripcion``.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).

Incluye además el endpoint de catálogo de requisitos (referencia).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from modulos.registro_operadores.operador.servicio import OperadorError
from modulos.registro_operadores.requisito_inscripcion.dto import RequisitoInscripcionOut
from modulos.registro_operadores.requisito_inscripcion.servicio import (
    REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
    REQUISITOS_GENERALES,
    RequisitoInscripcionService,
)


def crear_router(servicio: RequisitoInscripcionService, prefix: str = "") -> APIRouter:
    """Crea el router API de requisitos de inscripción."""
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    @router.get("/catalogo/requisitos")
    def catalogo_requisitos():
        """Devuelve el catálogo de requisitos generales y específicos por categoría."""
        return {
            "generales": REQUISITOS_GENERALES,
            "especificos_por_categoria": REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
        }

    @router.get("/{operador_id}/requisitos", response_model=list[RequisitoInscripcionOut])
    def listar_requisitos(operador_id: int):
        """Lista los requisitos de inscripción de un operador."""
        return servicio.listar(operador_id)

    @router.get("/{operador_id}/requisitos/pendientes", response_model=list[RequisitoInscripcionOut])
    def listar_requisitos_pendientes(operador_id: int):
        """Lista los requisitos aún no cumplidos de un operador."""
        return servicio.listar_pendientes(operador_id)

    @router.patch("/{operador_id}/requisitos/{requisito_id}")
    def actualizar_requisito(
        operador_id: int,
        requisito_id: int,
        cumplido: bool = Query(..., description="¿Está cumplido?"),
        observaciones: str | None = Query(None, description="Observaciones"),
    ):
        """Actualiza el estado de cumplimiento de un requisito."""
        try:
            return servicio.actualizar(operador_id, requisito_id, cumplido, observaciones)
        except OperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
