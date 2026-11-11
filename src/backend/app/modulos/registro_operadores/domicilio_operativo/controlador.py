"""Controlador (router API) de ``DomicilioOperativo``.

Se incluye dentro del router raíz ``/api/registro-operadores`` del módulo
(ver :mod:`modulos.registro_operadores.controlador`).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from modulos.registro_operadores.domicilio_operativo.dto import (
    DomicilioOperativoIn,
    DomicilioOperativoOut,
)
from modulos.registro_operadores.domicilio_operativo.servicio import (
    DomicilioOperativoService,
)
from modulos.registro_operadores.operador.servicio import OperadorError, OperadorService


def crear_router(servicio: DomicilioOperativoService,
                 operador_service: OperadorService, prefix: str = "") -> APIRouter:
    """Crea el router API de domicilios operativos."""
    router = APIRouter(prefix=prefix, tags=["Registro de Operadores"])

    @router.get("/{operador_id}/domicilios-operativos", response_model=list[DomicilioOperativoOut])
    def listar_domicilios_operativos(operador_id: int):
        """Lista los domicilios operativos de un operador."""
        return servicio.listar(operador_id)

    @router.post("/{operador_id}/domicilios-operativos", response_model=DomicilioOperativoOut, status_code=201)
    def agregar_domicilio_operativo(operador_id: int, data: DomicilioOperativoIn):
        """Agrega un domicilio operativo a un operador."""
        if operador_service.obtener(operador_id) is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
        try:
            return servicio.agregar(operador_id, data)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
