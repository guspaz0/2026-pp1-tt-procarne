"""Controlador (router API) del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from modulos.registro_operadores.enums import EstadoRegistral
from modulos.registro_operadores.schema import (
    DomicilioOperativoIn,
    DomicilioOperativoOut,
    HabilitacionIn,
    HabilitacionOut,
    InscripcionIn,
    InscripcionOut,
    ROCCAOperadorIn,
    ROCCAOperadorOut,
)
from modulos.registro_operadores.servicio import ROCCAOperadorError, ROCCAOperadorService


def crear_router(servicio: ROCCAOperadorService) -> APIRouter:
    """Crea el router API del módulo de registro de operadores."""
    router = APIRouter(prefix="/api/registro-operadores", tags=["Registro de Operadores"])

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    @router.get("", response_model=list[ROCCAOperadorOut])
    def listar_operadores(
        tipo: str | None = Query(None, description="Filtrar por tipo de operador"),
        estado_registral: str | None = Query(None, description="Filtrar por estado registral"),
    ):
        """Lista operadores, opcionalmente filtrados por tipo y estado."""
        return servicio.listar(tipo=tipo, estado_registral=estado_registral)

    @router.post("", response_model=ROCCAOperadorOut, status_code=201)
    def crear_operador(data: ROCCAOperadorIn):
        """Da de alta un operador en el registro provincial."""
        try:
            return servicio.crear_operador(data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{operador_id}", response_model=ROCCAOperadorOut)
    def obtener_operador(operador_id: int):
        """Obtiene un operador por su id."""
        operadores = servicio.listar()
        for op in operadores:
            if op.id == operador_id:
                return op
        raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")

    @router.patch("/{operador_id}/estado", response_model=ROCCAOperadorOut)
    def cambiar_estado(operador_id: int, estado: EstadoRegistral = Query(..., description="Nuevo estado registral")):
        """Cambia el estado registral de un operador."""
        try:
            return servicio.cambiar_estado(operador_id, estado)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Habilitaciones
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/habilitaciones", response_model=list[HabilitacionOut])
    def listar_habilitaciones(operador_id: int):
        """Lista las habilitaciones de un operador."""
        return servicio.listar_habilitaciones(operador_id)

    @router.post("/{operador_id}/habilitaciones", response_model=HabilitacionOut, status_code=201)
    def agregar_habilitacion(operador_id: int, data: HabilitacionIn):
        """Agrega una habilitación a un operador."""
        try:
            return servicio.agregar_habilitacion(operador_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Inscripciones
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/inscripciones", response_model=list[InscripcionOut])
    def listar_inscripciones(operador_id: int):
        """Lista las inscripciones de un operador."""
        return servicio.listar_inscripciones(operador_id)

    @router.post("/{operador_id}/inscripciones", response_model=InscripcionOut, status_code=201)
    def agregar_inscripcion(operador_id: int, data: InscripcionIn):
        """Agrega una inscripción a un operador."""
        try:
            return servicio.agregar_inscripcion(operador_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Domicilios operativos
    # ------------------------------------------------------------------

    @router.get("/{operador_id}/domicilios-operativos", response_model=list[DomicilioOperativoOut])
    def listar_domicilios_operativos(operador_id: int):
        """Lista los domicilios operativos de un operador."""
        return servicio.listar_domicilios_operativos(operador_id)

    @router.post("/{operador_id}/domicilios-operativos", response_model=DomicilioOperativoOut, status_code=201)
    def agregar_domicilio_operativo(operador_id: int, data: DomicilioOperativoIn):
        """Agrega un domicilio operativo a un operador."""
        try:
            return servicio.agregar_domicilio_operativo(operador_id, data)
        except ROCCAOperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
