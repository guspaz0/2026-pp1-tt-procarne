"""Controlador (rutas API) del Módulo III — Fiscalización (ROCCA).

Endpoints:

- ``GET    /api/fiscalizacion/inspecciones``                 — listar inspecciones
- ``GET    /api/fiscalizacion/inspecciones/{id}``            — obtener inspección
- ``POST   /api/fiscalizacion/inspecciones``                 — registrar inspección
- ``PATCH  /api/fiscalizacion/inspecciones/{id}/enviar``     — marcar como enviada
- ``DELETE /api/fiscalizacion/inspecciones/{id}``            — eliminar
- ``PATCH  /api/fiscalizacion/actas/{id}/firmar``            — firmar acta
- ``GET    /api/fiscalizacion/infracciones``                 — listar infracciones
- ``PATCH  /api/fiscalizacion/sanciones/{id}/estado``        — actualizar estado sanción
- ``GET    /api/fiscalizacion/reincidencias``                — listar reincidencias
- ``GET    /api/fiscalizacion/reincidencias/{cuit}``         — obtener por CUIT
- ``POST   /api/fiscalizacion/reincidencias``                — registrar reincidencia
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .enums import (
    EstadoSancion,
    GravedadInfraccion,
    ResultadoInspeccion,
)
from .schema import (
    InspeccionIn,
    InspeccionOut,
    InfraccionOut,
    ReincidenciaIn,
    ReincidenciaOut,
)
from .servicio import FiscalizacionError, FiscalizacionService


class ActualizarEstadoSancionIn(BaseModel):
    """Cuerpo para actualizar el estado de una sanción."""

    estado: EstadoSancion


def crear_router(
    fiscalizacion_service: FiscalizacionService,
) -> APIRouter:
    """Crea el router del Módulo III inyectando el servicio.

    Args:
        fiscalizacion_service: Servicio de Fiscalización.

    Returns:
        APIRouter con los endpoints del módulo.
    """

    router = APIRouter(
        prefix="/api/fiscalizacion", tags=["Fiscalización"]
    )

    # ------------------------------------------------------------------
    # Inspecciones
    # ------------------------------------------------------------------

    @router.get("/inspecciones", response_model=list[InspeccionOut])
    def listar_inspecciones(
        operador_cuit: Optional[str] = Query(
            default=None, description="Filtrar por CUIT del operador"
        ),
        resultado: Optional[ResultadoInspeccion] = Query(
            default=None, description="Filtrar por resultado"
        ),
        desde: Optional[date] = Query(
            default=None, description="Fecha mínima"
        ),
        hasta: Optional[date] = Query(
            default=None, description="Fecha máxima"
        ),
        limite: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[InspeccionOut]:
        """Lista inspecciones con filtros opcionales."""
        return fiscalizacion_service.listar_inspecciones(
            operador_cuit=operador_cuit,
            resultado=resultado,
            desde=desde,
            hasta=hasta,
            limite=limite,
            offset=offset,
        )

    @router.get("/inspecciones/{inspeccion_id}", response_model=InspeccionOut)
    def obtener_inspeccion(inspeccion_id: int) -> InspeccionOut:
        """Obtiene una inspección por su id (con actas, decomisos e infracciones)."""
        try:
            return fiscalizacion_service.obtener_inspeccion(inspeccion_id)
        except FiscalizacionError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/inspecciones", response_model=InspeccionOut, status_code=201)
    def registrar_inspeccion(datos: InspeccionIn) -> InspeccionOut:
        """Registra una nueva inspección con sus actas, decomisos e infracciones."""
        try:
            return fiscalizacion_service.registrar_inspeccion(datos)
        except FiscalizacionError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.patch("/inspecciones/{inspeccion_id}/enviar", response_model=InspeccionOut)
    def marcar_enviada(inspeccion_id: int) -> InspeccionOut:
        """Marca la inspección como enviada (sincronizada)."""
        try:
            return fiscalizacion_service.marcar_enviada(inspeccion_id)
        except FiscalizacionError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.delete("/inspecciones/{inspeccion_id}", status_code=204)
    def eliminar_inspeccion(inspeccion_id: int) -> None:
        """Elimina una inspección (y sus actas, decomisos e infracciones)."""
        try:
            fiscalizacion_service.eliminar_inspeccion(inspeccion_id)
        except FiscalizacionError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Actas
    # ------------------------------------------------------------------

    @router.patch("/actas/{acta_id}/firmar", status_code=200)
    def firmar_acta(acta_id: int) -> dict:
        """Firma un acta (cambia su estado a FIRMADA)."""
        try:
            fiscalizacion_service.firmar_acta(acta_id)
            return {"status": "ok", "acta_id": acta_id, "estado": "FIRMADA"}
        except FiscalizacionError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ------------------------------------------------------------------
    # Infracciones
    # ------------------------------------------------------------------

    @router.get("/infracciones", response_model=list[InfraccionOut])
    def listar_infracciones(
        operador_cuit: Optional[str] = Query(
            default=None, description="Filtrar por CUIT del operador"
        ),
        gravedad: Optional[GravedadInfraccion] = Query(
            default=None, description="Filtrar por gravedad"
        ),
        limite: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[InfraccionOut]:
        """Lista infracciones con filtros opcionales."""
        return fiscalizacion_service.listar_infracciones(
            operador_cuit=operador_cuit,
            gravedad=gravedad,
            limite=limite,
            offset=offset,
        )

    # ------------------------------------------------------------------
    # Sanciones
    # ------------------------------------------------------------------

    @router.patch("/sanciones/{sancion_id}/estado", status_code=200)
    def actualizar_estado_sancion(
        sancion_id: int, datos: ActualizarEstadoSancionIn
    ) -> dict:
        """Actualiza el estado de una sanción."""
        try:
            fiscalizacion_service.actualizar_estado_sancion(sancion_id, datos.estado)
            return {"status": "ok", "sancion_id": sancion_id, "estado": datos.estado.value}
        except FiscalizacionError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Reincidencias
    # ------------------------------------------------------------------

    @router.get("/reincidencias", response_model=list[ReincidenciaOut])
    def listar_reincidencias(
        limite: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[ReincidenciaOut]:
        """Lista reincidencias ordenadas por cantidad descendente."""
        return fiscalizacion_service.listar_reincidencias(
            limite=limite, offset=offset
        )

    @router.get("/reincidencias/{operador_cuit}", response_model=ReincidenciaOut)
    def obtener_reincidencia(operador_cuit: str) -> ReincidenciaOut:
        """Obtiene la reincidencia de un operador por su CUIT."""
        try:
            return fiscalizacion_service.obtener_reincidencia(operador_cuit)
        except FiscalizacionError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/reincidencias", response_model=ReincidenciaOut, status_code=201)
    def registrar_reincidencia(datos: ReincidenciaIn) -> ReincidenciaOut:
        """Registra (o incrementa) una reincidencia para un operador."""
        return fiscalizacion_service.registrar_reincidencia(datos)

    return router
