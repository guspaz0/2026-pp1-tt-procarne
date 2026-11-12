# """Controlador (router API) del Módulo II — Trazabilidad Comercial."""

# from __future__ import annotations

# from fastapi import APIRouter, HTTPException, Query

# from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn, RegistroTrazabilidadOut
# from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialError, TrazabilidadComercialService


# def crear_router(servicio: TrazabilidadComercialService) -> APIRouter:
#     """Crea el router API del módulo de trazabilidad comercial."""
#     router = APIRouter(prefix="/api/trazabilidad", tags=["Trazabilidad Comercial"])

#     @router.get("", response_model=list[RegistroTrazabilidadOut])
#     def listar_registros(
#         estado: str | None = Query(None, description="Filtrar por estado"),
#         especie: str | None = Query(None, description="Filtrar por especie"),
#         origen_cuit: str | None = Query(None, description="Filtrar por CUIT de origen"),
#         destino_cuit: str | None = Query(None, description="Filtrar por CUIT de destino"),
#     ):
#         """Lista registros de trazabilidad, opcionalmente filtrados."""
#         return servicio.listar(
#             estado=estado, especie=especie,
#             origen_cuit=origen_cuit, destino_cuit=destino_cuit,
#         )

#     @router.post("", response_model=RegistroTrazabilidadOut, status_code=201)
#     def registrar_ingreso(data: RegistroTrazabilidadIn):
#         """Registra un ingreso de mercadería."""
#         return servicio.registrar_ingreso(data)

#     @router.get("/{registro_id}", response_model=RegistroTrazabilidadOut)
#     def obtener_registro(registro_id: int):
#         """Obtiene un registro de trazabilidad por su id."""
#         registro = servicio.obtener_por_id(registro_id)
#         if registro is None:
#             raise HTTPException(status_code=404, detail=f"No existe un registro con id {registro_id}")
#         return registro

#     @router.post("/{registro_id}/confirmar", response_model=RegistroTrazabilidadOut)
#     def confirmar(registro_id: int):
#         """Confirma un registro de trazabilidad."""
#         try:
#             return servicio.confirmar(registro_id)
#         except TrazabilidadComercialError as e:
#             raise HTTPException(status_code=404, detail=str(e))

#     @router.post("/{registro_id}/anular", response_model=RegistroTrazabilidadOut)
#     def anular(registro_id: int):
#         """Anula un registro de trazabilidad."""
#         try:
#             return servicio.anular(registro_id)
#         except TrazabilidadComercialError as e:
#             raise HTTPException(status_code=404, detail=str(e))

#     return router
