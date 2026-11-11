"""Controlador (router API) de ``Inscripcion``.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from modulos.registro_operadores.inscripcion.dto import InscripcionIn, InscripcionOut
from modulos.registro_operadores.inscripcion.servicio import InscripcionService
from modulos.registro_operadores.operador.servicio import OperadorService


def crear_router(servicio: InscripcionService,
                 operador_service: OperadorService | None = None,
                 prefix: str = "") -> APIRouter:
    """Crea el router API de inscripciones de operador."""
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    @router.get("/{operador_id}/inscripciones", response_model=list[InscripcionOut])
    def listar_inscripciones(operador_id: int):
        """Lista las inscripciones de un operador."""
        return servicio.listar(operador_id)

    @router.post("/{operador_id}/inscripciones", response_model=InscripcionOut, status_code=201)
    def agregar_inscripcion(operador_id: int, data: InscripcionIn):
        """Agrega una inscripción a un operador."""
        if operador_service.obtener(operador_id) is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
        return servicio.agregar(operador_id, data)

    return router
