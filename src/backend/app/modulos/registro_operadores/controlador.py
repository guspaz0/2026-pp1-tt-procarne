"""Controlador (rutas API) del Módulo I — Registro Provincial de Operadores.

Endpoints:

- ``GET  /api/registro-operadores``                — listar operadores
- ``GET  /api/registro-operadores/{cuit}``         — obtener por CUIT
- ``POST /api/registro-operadores``                — registrar operador
- ``PATCH /api/registro-operadores/{cuit}/estado`` — cambiar estado registral
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .enums import EstadoRegistral, TipoOperador
from .schema import ROCCAOperadorIn, ROCCAOperadorOut
from .servicio import ROCCAOperadorError, ROCCAOperadorService


class CambioEstadoIn(BaseModel):
    """Cuerpo para el cambio de estado registral."""

    estado_registral: EstadoRegistral = Field(
        description="Nuevo estado registral (ACTIVO, SUSPENDIDO, BAJADO)"
    )


def crear_router(operador_service: ROCCAOperadorService) -> APIRouter:
    """Crea el router del Módulo I inyectando el servicio.

    Args:
        operador_service: Servicio del Registro Provincial de Operadores.

    Returns:
        APIRouter con los endpoints del módulo.
    """

    router = APIRouter(prefix="/api/registro-operadores", tags=["Registro de Operadores"])

    @router.get("", response_model=list[ROCCAOperadorOut])
    def listar(
        tipo: Optional[TipoOperador] = Query(default=None, description="Filtrar por tipo de operador"),
        estado_registral: Optional[EstadoRegistral] = Query(
            default=None, description="Filtrar por estado registral"
        ),
        limite: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[ROCCAOperadorOut]:
        """Lista operadores del Registro Provincial con filtros opcionales."""
        return operador_service.listar(
            tipo=tipo, estado_registral=estado_registral, limite=limite, offset=offset
        )

    @router.get("/{cuit}", response_model=ROCCAOperadorOut)
    def obtener(cuit: str) -> ROCCAOperadorOut:
        """Obtiene un operador por su CUIT."""
        try:
            return operador_service.obtener(cuit)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("", response_model=ROCCAOperadorOut, status_code=201)
    def registrar(datos: ROCCAOperadorIn) -> ROCCAOperadorOut:
        """Registra un nuevo operador en el ROCCA."""
        try:
            return operador_service.registrar(datos)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=409, detail=str(e))

    @router.patch("/{cuit}/estado", response_model=ROCCAOperadorOut)
    def cambiar_estado(cuit: str, datos: CambioEstadoIn) -> ROCCAOperadorOut:
        """Cambia el estado registral del operador."""
        try:
            return operador_service.cambiar_estado(cuit, datos.estado_registral)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
