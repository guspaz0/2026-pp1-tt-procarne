"""Controlador (rutas API) del módulo de Remitos Electrónicos Cárnicos.

Agrega los routers de los submódulos (operador, mercadería, remito) en un
único :class:`APIRouter`. Recibe los servicios por inyección de dependencias
(**Dependency Inversion**).

Endpoints:

- ``/api/operadores`` — CRUD de operadores de la cadena cárnica
- ``/api/mercaderias`` — CRUD del catálogo de mercaderías (códigos AFIP)
- ``/api/remitos`` — CRUD de remitos electrónicos cárnicos
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .mercaderia.schema import MercaderiaIn, MercaderiaOut
from .mercaderia.servicio import MercaderiaError, MercaderiaService
from .operador.schema import OperadorIn, OperadorOut
from .operador.servicio import OperadorError, OperadorService
from .remito.schema import RemitoCarnicoIn, RemitoCarnicoOut
from .remito.servicio import RemitoCarnicoError, RemitoCarnicoService


def crear_router(
    operador_service: OperadorService,
    mercaderia_service: MercaderiaService,
    remito_service: RemitoCarnicoService,
) -> APIRouter:
    """Crea el router del módulo inyectando los servicios.

    Args:
        operador_service: Servicio de operadores.
        mercaderia_service: Servicio de mercaderías.
        remito_service: Servicio de remitos.

    Returns:
        APIRouter con todos los endpoints del módulo.
    """

    router = APIRouter(tags=["Remitos Cárnicos"])

    # ------------------------------------------------------------------
    # Operadores
    # ------------------------------------------------------------------

    @router.get("/api/operadores", response_model=list[OperadorOut])
    def listar_operadores(
        limite: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[OperadorOut]:
        """Lista operadores de la cadena cárnica."""
        return operador_service.listar(limite=limite, offset=offset)

    @router.get("/api/operadores/{cuit}", response_model=OperadorOut)
    def obtener_operador(cuit: str) -> OperadorOut:
        """Obtiene un operador por su CUIT."""
        try:
            return operador_service.obtener(cuit)
        except OperadorError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/api/operadores", response_model=OperadorOut, status_code=201)
    def crear_operador(datos: OperadorIn) -> OperadorOut:
        """Crea un nuevo operador."""
        try:
            return operador_service.crear(datos)
        except OperadorError as e:
            raise HTTPException(status_code=409, detail=str(e))

    # ------------------------------------------------------------------
    # Mercaderías
    # ------------------------------------------------------------------

    @router.get("/api/mercaderias", response_model=list[MercaderiaOut])
    def listar_mercaderias(
        limite: int = Query(default=200, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[MercaderiaOut]:
        """Lista el catálogo de mercaderías (códigos AFIP)."""
        return mercaderia_service.listar(limite=limite, offset=offset)

    @router.get("/api/mercaderias/{codigo_afip}", response_model=MercaderiaOut)
    def obtener_mercaderia(codigo_afip: str) -> MercaderiaOut:
        """Obtiene una mercadería por su código AFIP."""
        try:
            return mercaderia_service.obtener(codigo_afip)
        except MercaderiaError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/api/mercaderias", response_model=MercaderiaOut, status_code=201)
    def crear_mercaderia(datos: MercaderiaIn) -> MercaderiaOut:
        """Crea una nueva mercadería en el catálogo."""
        try:
            return mercaderia_service.crear(datos)
        except MercaderiaError as e:
            raise HTTPException(status_code=409, detail=str(e))

    # ------------------------------------------------------------------
    # Remitos
    # ------------------------------------------------------------------

    @router.get("/api/remitos", response_model=list[RemitoCarnicoOut])
    def listar_remitos(
        estado: Optional[str] = Query(default=None, description="Filtrar por estado (E, AN, NU)"),
        desde: Optional[datetime] = Query(default=None, description="Fecha de emisión mínima"),
        hasta: Optional[datetime] = Query(default=None, description="Fecha de emisión máxima"),
        limite: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[RemitoCarnicoOut]:
        """Lista remitos con filtros opcionales."""
        return remito_service.listar(estado=estado, desde=desde, hasta=hasta, limite=limite, offset=offset)

    @router.get("/api/remitos/{punto_emision}/{numero_comprobante}", response_model=RemitoCarnicoOut)
    def obtener_remito(punto_emision: str, numero_comprobante: str) -> RemitoCarnicoOut:
        """Obtiene un remito por su código (punto de emisión + número)."""
        try:
            return remito_service.obtener(punto_emision, numero_comprobante)
        except RemitoCarnicoError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/api/remitos", response_model=RemitoCarnicoOut, status_code=201)
    def crear_remito(datos: RemitoCarnicoIn) -> RemitoCarnicoOut:
        """Crea un nuevo Remito Electrónico Cárnico."""
        try:
            return remito_service.crear(datos)
        except RemitoCarnicoError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/api/remitos/{remito_id}/anular", response_model=RemitoCarnicoOut)
    def anular_remito(remito_id: int) -> RemitoCarnicoOut:
        """Anula un remito (cambia su estado a AN)."""
        try:
            return remito_service.anular(remito_id)
        except RemitoCarnicoError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
