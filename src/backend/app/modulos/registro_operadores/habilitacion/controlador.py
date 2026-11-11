"""Controlador (router API) de ``Habilitacion``.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from modulos.registro_operadores.habilitacion.dto import HabilitacionIn, HabilitacionOut
from modulos.registro_operadores.habilitacion.servicio import HabilitacionService
from modulos.registro_operadores.operador.servicio import OperadorService


def crear_router(servicio: HabilitacionService,
                 operador_service: OperadorService | None = None,
                 prefix: str = "") -> APIRouter:
    """Crea el router API de habilitaciones de operador."""
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    @router.get("/{operador_id}/habilitaciones", response_model=list[HabilitacionOut])
    def listar_habilitaciones(operador_id: int):
        """Lista las habilitaciones de un operador."""
        return servicio.listar(operador_id)

    @router.post("/{operador_id}/habilitaciones", response_model=HabilitacionOut, status_code=201)
    def agregar_habilitacion(operador_id: int, data: HabilitacionIn):
        """Agrega una habilitación a un operador."""
        if operador_service.obtener(operador_id) is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
        try:
            return servicio.agregar(operador_id, data)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
