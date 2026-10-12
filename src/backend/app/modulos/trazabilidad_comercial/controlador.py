"""Controlador (rutas API) del Módulo II — Trazabilidad Comercial (ROCCA).

Endpoints:

- ``GET    /api/trazabilidad``                — listar registros
- ``GET    /api/trazabilidad/{id}``           — obtener por id
- ``POST   /api/trazabilidad``                — registrar movimiento
- ``PATCH  /api/trazabilidad/{id}/validar``   — validar (confirmar recepción)
- ``PATCH  /api/trazabilidad/{id}/rechazar``  — rechazar
- ``DELETE /api/trazabilidad/{id}``           — eliminar
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .enums import Especie, EstadoTrazabilidad, TipoIngreso
from .schema import RegistroTrazabilidadIn, RegistroTrazabilidadOut
from .servicio import TrazabilidadComercialError, TrazabilidadComercialService


class RechazoIn(BaseModel):
    """Cuerpo para el rechazo de un registro."""

    motivo: Optional[str] = Field(
        default=None, description="Motivo del rechazo (opcional)"
    )


def crear_router(
    trazabilidad_service: TrazabilidadComercialService,
) -> APIRouter:
    """Crea el router del Módulo II inyectando el servicio.

    Args:
        trazabilidad_service: Servicio de Trazabilidad Comercial.

    Returns:
        APIRouter con los endpoints del módulo.
    """

    router = APIRouter(
        prefix="/api/trazabilidad", tags=["Trazabilidad Comercial"]
    )

    @router.get("", response_model=list[RegistroTrazabilidadOut])
    def listar(
        tipo_ingreso: Optional[TipoIngreso] = Query(
            default=None, description="Filtrar por tipo de ingreso"
        ),
        especie: Optional[Especie] = Query(
            default=None, description="Filtrar por especie"
        ),
        estado: Optional[EstadoTrazabilidad] = Query(
            default=None, description="Filtrar por estado"
        ),
        origen_provincia: Optional[str] = Query(
            default=None, description="Filtrar por provincia de origen"
        ),
        destino_cuit: Optional[str] = Query(
            default=None, description="Filtrar por CUIT de destino"
        ),
        desde: Optional[date] = Query(
            default=None, description="Fecha de ingreso mínima"
        ),
        hasta: Optional[date] = Query(
            default=None, description="Fecha de ingreso máxima"
        ),
        limite: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[RegistroTrazabilidadOut]:
        """Lista registros de trazabilidad con filtros opcionales."""
        return trazabilidad_service.listar(
            tipo_ingreso=tipo_ingreso,
            especie=especie,
            estado=estado,
            origen_provincia=origen_provincia,
            destino_cuit=destino_cuit,
            desde=desde,
            hasta=hasta,
            limite=limite,
            offset=offset,
        )

    @router.get("/{registro_id}", response_model=RegistroTrazabilidadOut)
    def obtener(registro_id: int) -> RegistroTrazabilidadOut:
        """Obtiene un registro de trazabilidad por su id."""
        try:
            return trazabilidad_service.obtener(registro_id)
        except TrazabilidadComercialError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("", response_model=RegistroTrazabilidadOut, status_code=201)
    def registrar(datos: RegistroTrazabilidadIn) -> RegistroTrazabilidadOut:
        """Registra un nuevo movimiento de trazabilidad comercial."""
        try:
            return trazabilidad_service.registrar(datos)
        except TrazabilidadComercialError as e:
            raise HTTPException(status_code=409, detail=str(e))

    @router.patch("/{registro_id}/validar", response_model=RegistroTrazabilidadOut)
    def validar(registro_id: int) -> RegistroTrazabilidadOut:
        """Valida el registro (confirma la recepción)."""
        try:
            return trazabilidad_service.validar(registro_id)
        except TrazabilidadComercialError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.patch("/{registro_id}/rechazar", response_model=RegistroTrazabilidadOut)
    def rechazar(registro_id: int, datos: Optional[RechazoIn] = None) -> RegistroTrazabilidadOut:
        """Rechaza el registro con motivo opcional."""
        motivo = datos.motivo if datos else None
        try:
            return trazabilidad_service.rechazar(registro_id, motivo)
        except TrazabilidadComercialError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.delete("/{registro_id}", status_code=204)
    def eliminar(registro_id: int) -> None:
        """Elimina un registro de trazabilidad."""
        try:
            trazabilidad_service.eliminar(registro_id)
        except TrazabilidadComercialError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
