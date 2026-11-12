# """Controlador (router API) del Módulo III — Fiscalización."""

# from __future__ import annotations

# from fastapi import APIRouter, HTTPException, Query

# from modulos.fiscalizacion.schema import (
#     ActaIn,
#     ActaOut,
#     DecomisoIn,
#     DecomisoOut,
#     InspeccionIn,
#     InspeccionOut,
#     InfraccionIn,
#     InfraccionOut,
#     ReincidenciaOut,
#     SancionIn,
#     SancionOut,
# )
# from modulos.fiscalizacion.servicio import FiscalizacionError, FiscalizacionService


# def crear_router(servicio: FiscalizacionService) -> APIRouter:
#     """Crea el router API del módulo de fiscalización."""
#     router = APIRouter(prefix="/api/fiscalizacion", tags=["Fiscalización"])

#     # ------------------------------------------------------------------
#     # Inspecciones
#     # ------------------------------------------------------------------

#     @router.get("/inspecciones", response_model=list[InspeccionOut])
#     def listar_inspecciones(
#         operador_cuit: str | None = Query(None, description="Filtrar por CUIT del operador"),
#     ):
#         """Lista inspecciones, opcionalmente filtradas por operador."""
#         return servicio.listar_inspecciones(operador_cuit=operador_cuit)

#     @router.post("/inspecciones", response_model=InspeccionOut, status_code=201)
#     def registrar_inspeccion(data: InspeccionIn):
#         """Registra una inspección."""
#         return servicio.registrar_inspeccion(data)

#     @router.get("/inspecciones/{inspeccion_id}", response_model=InspeccionOut)
#     def obtener_inspeccion(inspeccion_id: int):
#         """Obtiene una inspección por su id."""
#         inspeccion = servicio.obtener_inspeccion(inspeccion_id)
#         if inspeccion is None:
#             raise HTTPException(status_code=404, detail=f"No existe una inspección con id {inspeccion_id}")
#         return inspeccion

#     # ------------------------------------------------------------------
#     # Actas
#     # ------------------------------------------------------------------

#     @router.get("/actas", response_model=list[ActaOut])
#     def listar_actas(
#         inspeccion_id: int | None = Query(None, description="Filtrar por inspección"),
#     ):
#         """Lista actas, opcionalmente filtradas por inspección."""
#         return servicio.listar_actas(inspeccion_id=inspeccion_id)

#     @router.post("/actas", response_model=ActaOut, status_code=201)
#     def crear_acta(data: ActaIn):
#         """Crea un acta."""
#         return servicio.crear_acta(data)

#     @router.post("/actas/{acta_id}/firmar", response_model=ActaOut)
#     def firmar_acta(acta_id: int, firmado_por: str = Query(..., description="Nombre del firmante")):
#         """Firma un acta."""
#         try:
#             return servicio.firmar_acta(acta_id, firmado_por)
#         except FiscalizacionError as e:
#             raise HTTPException(status_code=404, detail=str(e))

#     # ------------------------------------------------------------------
#     # Infracciones
#     # ------------------------------------------------------------------

#     @router.get("/infracciones", response_model=list[InfraccionOut])
#     def listar_infracciones(
#         operador_cuit: str | None = Query(None, description="Filtrar por CUIT del operador"),
#     ):
#         """Lista infracciones, opcionalmente filtradas por operador."""
#         return servicio.listar_infracciones(operador_cuit=operador_cuit)

#     @router.post("/infracciones", response_model=InfraccionOut, status_code=201)
#     def registrar_infraccion(data: InfraccionIn):
#         """Registra una infracción."""
#         return servicio.registrar_infraccion(data)

#     # ------------------------------------------------------------------
#     # Sanciones
#     # ------------------------------------------------------------------

#     @router.get("/sanciones", response_model=list[SancionOut])
#     def listar_sanciones(
#         operador_cuit: str | None = Query(None, description="Filtrar por CUIT del operador"),
#     ):
#         """Lista sanciones, opcionalmente filtradas por operador."""
#         return servicio.listar_sanciones(operador_cuit=operador_cuit)

#     @router.post("/sanciones", response_model=SancionOut, status_code=201)
#     def aplicar_sancion(data: SancionIn):
#         """Aplica una sanción."""
#         return servicio.aplicar_sancion(data)

#     @router.post("/sanciones/{sancion_id}/notificar", response_model=SancionOut)
#     def notificar_sancion(sancion_id: int):
#         """Notifica una sanción."""
#         try:
#             return servicio.notificar_sancion(sancion_id)
#         except FiscalizacionError as e:
#             raise HTTPException(status_code=404, detail=str(e))

#     # ------------------------------------------------------------------
#     # Decomisos
#     # ------------------------------------------------------------------

#     @router.post("/decomisos", response_model=DecomisoOut, status_code=201)
#     def registrar_decomiso(data: DecomisoIn):
#         """Registra un decomiso."""
#         return servicio.registrar_decomiso(data)

#     # ------------------------------------------------------------------
#     # Reincidencias
#     # ------------------------------------------------------------------

#     @router.get("/reincidencias/{operador_cuit}", response_model=ReincidenciaOut)
#     def obtener_reincidencia(operador_cuit: str):
#         """Obtiene la reincidencia de un operador."""
#         reincidencia = servicio.obtener_reincidencia(operador_cuit)
#         if reincidencia is None:
#             raise HTTPException(status_code=404, detail=f"No hay reincidencias para el operador {operador_cuit}")
#         return reincidencia

#     return router
