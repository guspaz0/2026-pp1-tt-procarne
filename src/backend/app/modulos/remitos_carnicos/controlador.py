"""Controlador (router API) del módulo de Remitos Electrónicos Cárnicos."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from modulos.remitos_carnicos.enums import EstadoRemito
from modulos.remitos_carnicos.remito.schema import RemitoCarnicoIn, RemitoCarnicoOut
from modulos.remitos_carnicos.remito.servicio import RemitoCarnicoError, RemitoCarnicoService


def crear_router(servicio: RemitoCarnicoService) -> APIRouter:
    """Crea el router API del módulo de remitos electrónicos cárnicos."""
    router = APIRouter(prefix="/api/remitos-carnicos", tags=["Remitos Electrónicos Cárnicos"])

    @router.get("", response_model=list[RemitoCarnicoOut])
    def listar_remitos(
        estado: str | None = Query(None, description="Filtrar por estado"),
    ):
        """Lista remitos, opcionalmente filtrados por estado."""
        return servicio.listar(estado=estado)

    @router.post("", response_model=RemitoCarnicoOut, status_code=201)
    def emitir_remito(data: RemitoCarnicoIn):
        """Emite un remito electrónico cárnico."""
        try:
            return servicio.emitir_remito(data)
        except RemitoCarnicoError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{remito_id}", response_model=RemitoCarnicoOut)
    def obtener_remito(remito_id: int):
        """Obtiene un remito por su id."""
        remitos = servicio.listar()
        for r in remitos:
            if r.id == remito_id:
                return r
        raise HTTPException(status_code=404, detail=f"No existe un remito con id {remito_id}")

    @router.patch("/{remito_id}/estado", response_model=RemitoCarnicoOut)
    def cambiar_estado(
        remito_id: int,
        estado: EstadoRemito = Query(..., description="Nuevo estado"),
    ):
        """Cambia el estado de un remito."""
        try:
            return servicio.cambiar_estado(remito_id, estado)
        except RemitoCarnicoError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return router
