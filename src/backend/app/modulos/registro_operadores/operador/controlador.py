"""Controlador (router API) de ``Operador``.

Rutas ``/api/registro-operadores``:
- ``GET  /`` — listado de operadores (con filtros).
- ``POST /`` — alta de operador.
- ``GET  /{operador_id}`` — detalle.
- ``PATCH /{operador_id}/estado`` — cambio de estado registral.
- ``POST /{operador_id}/activar|suspender|reactivar|bajar`` — ciclo de
  vida (solo supervisor/admin).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from modulos.registro_operadores.enums import EstadoRegistral
from modulos.registro_operadores.operador.dto import OperadorIn, OperadorOut
from modulos.registro_operadores.operador.servicio import OperadorError, OperadorService


def _require_supervisor(request: Request) -> None:
    """Verifica que el usuario autenticado tenga rol supervisor o admin.

    Lee ``request.state.user.user_metadata.rol`` (inyectado por el middleware
    de InsForge). Si no tiene rol suficiente → 403.
    """
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="No autenticado")
    metadata = user.get("user_metadata", {}) if isinstance(user, dict) else getattr(user, "user_metadata", {})
    rol = metadata.get("rol", "") if isinstance(metadata, dict) else ""
    if rol not in ("supervisor", "admin"):
        raise HTTPException(status_code=403, detail="Requiere rol supervisor o admin")


def crear_router(servicio: OperadorService, prefix: str = "") -> APIRouter:
    """Crea el router API de operadores del módulo de registro."""
    router = APIRouter(prefix="/api/registro-operadores", tags=["Registro de Operadores"])

    @router.get("", response_model=list[OperadorOut])
    def listar_operadores(
        tipo: str | None = Query(None, description="Filtrar por tipo de operador"),
        estado_registral: str | None = Query(None, description="Filtrar por estado registral"),
        categoria: str | None = Query(None, description="Filtrar por categoría (SALA_DE_DESPOSTE, CARNICERIAS, etc.)"),
    ):
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        return servicio.listar(tipo=tipo, estado_registral=estado_registral, categoria=categoria)

    @router.post("", response_model=OperadorOut, status_code=201)
    def crear_operador(data: OperadorIn):
        """Da de alta un operador en el registro provincial."""
        try:
            return servicio.crear_operador(data)
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{operador_id}", response_model=OperadorOut)
    def obtener_operador(operador_id: int):
        """Obtiene un operador por su id."""
        operador = servicio.obtener(operador_id)
        if operador is None:
            raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
        return operador

    @router.patch("/{operador_id}/estado", response_model=OperadorOut)
    def cambiar_estado(operador_id: int, estado: EstadoRegistral = Query(..., description="Nuevo estado registral")):
        """Cambia el estado registral de un operador."""
        try:
            return servicio.cambiar_estado(operador_id, estado)
        except OperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # ------------------------------------------------------------------
    # Ciclo de vida del operador (activar / suspender / reactivar / bajar)
    # ------------------------------------------------------------------

    @router.post("/{operador_id}/activar", response_model=OperadorOut)
    def activar_operador(operador_id: int, request: Request):
        """Activa un operador PENDIENTE (acción de supervisor).

        Cambia PENDIENTE → ACTIVO. Si ya está ACTIVO → 400.
        """
        _require_supervisor(request)
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral == EstadoRegistral.ACTIVO.value:
                raise HTTPException(status_code=400, detail="El operador ya está ACTIVO")
            if operador.estado_registral == EstadoRegistral.BAJADO.value:
                raise HTTPException(status_code=400, detail="No se puede activar un operador BAJADO")
            return servicio.cambiar_estado(operador_id, EstadoRegistral.ACTIVO)
        except HTTPException:
            raise
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/suspender", response_model=OperadorOut)
    def suspender_operador(operador_id: int, request: Request):
        """Suspende un operador ACTIVO (acción de supervisor).

        Cambia ACTIVO → SUSPENDIDO.
        """
        _require_supervisor(request)
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral != EstadoRegistral.ACTIVO.value:
                raise HTTPException(status_code=400, detail=f"Solo se puede suspender un operador ACTIVO (estado actual: {operador.estado_registral})")
            return servicio.cambiar_estado(operador_id, EstadoRegistral.SUSPENDIDO)
        except HTTPException:
            raise
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/reactivar", response_model=OperadorOut)
    def reactivar_operador(operador_id: int, request: Request):
        """Reactiva un operador SUSPENDIDO (acción de supervisor).

        Cambia SUSPENDIDO → ACTIVO.
        """
        _require_supervisor(request)
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral != EstadoRegistral.SUSPENDIDO.value:
                raise HTTPException(status_code=400, detail=f"Solo se puede reactivar un operador SUSPENDIDO (estado actual: {operador.estado_registral})")
            return servicio.cambiar_estado(operador_id, EstadoRegistral.ACTIVO)
        except HTTPException:
            raise
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/{operador_id}/bajar", response_model=OperadorOut)
    def bajar_operador(operador_id: int, request: Request):
        """Da de baja un operador (acción de supervisor).

        Cambia a BAJADO. Solo desde ACTIVO o SUSPENDIDO.
        """
        _require_supervisor(request)
        try:
            operador = servicio.obtener(operador_id)
            if operador is None:
                raise HTTPException(status_code=404, detail=f"No existe un operador con id {operador_id}")
            if operador.estado_registral not in (EstadoRegistral.ACTIVO.value, EstadoRegistral.SUSPENDIDO.value):
                raise HTTPException(status_code=400, detail=f"Solo se puede dar de baja un operador ACTIVO o SUSPENDIDO (estado actual: {operador.estado_registral})")
            return servicio.cambiar_estado(operador_id, EstadoRegistral.BAJADO)
        except HTTPException:
            raise
        except OperadorError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
