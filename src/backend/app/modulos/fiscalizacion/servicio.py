# """Servicio de negocio del Módulo III — Fiscalización.

# Casos de uso:
# - Registrar una inspección.
# - Crear actas, infracciones, sanciones y decomisos.
# - Firmar actas.
# - Registrar reincidencias.
# """

# from __future__ import annotations

# from datetime import datetime, timezone

# from modulos.fiscalizacion.dao import (
#     Acta,
#     Decomiso,
#     FiscalizacionDAO,
#     Infraccion,
#     Inspeccion,
#     Reincidencia,
#     Sancion,
# )
# from modulos.fiscalizacion.enums import (
#     EstadoActa,
#     EstadoDecomiso,
#     EstadoSancion,
# )
# from modulos.fiscalizacion.schema import (
#     ActaIn,
#     ActaOut,
#     DecomisoIn,
#     DecomisoOut,
#     InspeccionIn,
#     InspeccionOut,
#     InfraccionIn,
#     InfraccionOut,
#     ReincidenciaIn,
#     ReincidenciaOut,
#     SancionIn,
#     SancionOut,
# )


# class FiscalizacionError(Exception):
#     """Error de negocio del servicio de fiscalización."""


# class FiscalizacionService:
#     """Servicio de negocio de fiscalización."""

#     def __init__(self, dao: FiscalizacionDAO) -> None:
#         self._dao = dao

#     # ------------------------------------------------------------------
#     # Inspecciones
#     # ------------------------------------------------------------------

#     def registrar_inspeccion(self, data: InspeccionIn) -> InspeccionOut:
#         """Registra una inspección."""
#         inspeccion = Inspeccion(
#             tipo=data.tipo,
#             operador_cuit=data.operador_cuit,
#             fecha=data.fecha,
#             inspector=data.inspector,
#             observaciones=data.observaciones,
#         )
#         self._dao.crear_inspeccion(inspeccion)
#         return InspeccionOut.model_validate(inspeccion)

#     def obtener_inspeccion(self, inspeccion_id: int) -> InspeccionOut | None:
#         """Busca una inspección por su id."""
#         inspeccion = self._dao.obtener_inspeccion(inspeccion_id)
#         return InspeccionOut.model_validate(inspeccion) if inspeccion else None

#     def listar_inspecciones(self, operador_cuit: str | None = None) -> list[InspeccionOut]:
#         """Lista inspecciones, opcionalmente filtradas por operador."""
#         inspecciones = self._dao.listar_inspecciones(operador_cuit=operador_cuit)
#         return [InspeccionOut.model_validate(i) for i in inspecciones]

#     # ------------------------------------------------------------------
#     # Actas
#     # ------------------------------------------------------------------

#     def crear_acta(self, data: ActaIn) -> ActaOut:
#         """Crea un acta."""
#         acta = Acta(
#             inspeccion_id=data.inspeccion_id,
#             tipo=data.tipo,
#             numero=data.numero,
#             fecha=data.fecha,
#             contenido=data.contenido,
#         )
#         self._dao.crear_acta(acta)
#         return ActaOut.model_validate(acta)

#     def firmar_acta(self, acta_id: int, firmado_por: str) -> ActaOut:
#         """Firma un acta."""
#         acta = self._dao.obtener_acta(acta_id)
#         if acta is None:
#             raise FiscalizacionError(f"No existe un acta con id {acta_id}")
#         acta.estado = EstadoActa.FIRMADA.value
#         acta.firmado_por = firmado_por
#         acta.fecha_firma = datetime.now(timezone.utc)
#         self._dao.actualizar_acta(acta)
#         return ActaOut.model_validate(acta)

#     def listar_actas(self, inspeccion_id: int | None = None) -> list[ActaOut]:
#         """Lista actas, opcionalmente filtradas por inspección."""
#         actas = self._dao.listar_actas(inspeccion_id=inspeccion_id)
#         return [ActaOut.model_validate(a) for a in actas]

#     # ------------------------------------------------------------------
#     # Infracciones
#     # ------------------------------------------------------------------

#     def registrar_infraccion(self, data: InfraccionIn) -> InfraccionOut:
#         """Registra una infracción."""
#         infraccion = Infraccion(
#             inspeccion_id=data.inspeccion_id,
#             operador_cuit=data.operador_cuit,
#             tipo=data.tipo,
#             gravedad=data.gravedad,
#             descripcion=data.descripcion,
#         )
#         self._dao.crear_infraccion(infraccion)
#         # Actualizar reincidencia
#         self._dao.actualizar_reincidencia(data.operador_cuit)
#         return InfraccionOut.model_validate(infraccion)

#     def listar_infracciones(self, operador_cuit: str | None = None) -> list[InfraccionOut]:
#         """Lista infracciones, opcionalmente filtradas por operador."""
#         infracciones = self._dao.listar_infracciones(operador_cuit=operador_cuit)
#         return [InfraccionOut.model_validate(i) for i in infracciones]

#     # ------------------------------------------------------------------
#     # Sanciones
#     # ------------------------------------------------------------------

#     def aplicar_sancion(self, data: SancionIn) -> SancionOut:
#         """Aplica una sanción."""
#         sancion = Sancion(
#             infraccion_id=data.infraccion_id,
#             operador_cuit=data.operador_cuit,
#             tipo=data.tipo,
#             monto=data.monto,
#             observaciones=data.observaciones,
#         )
#         self._dao.crear_sancion(sancion)
#         return SancionOut.model_validate(sancion)

#     def notificar_sancion(self, sancion_id: int) -> SancionOut:
#         """Notifica una sanción."""
#         sancion = self._dao.obtener_sancion(sancion_id)
#         if sancion is None:
#             raise FiscalizacionError(f"No existe una sanción con id {sancion_id}")
#         sancion.estado = EstadoSancion.NOTIFICADA.value
#         sancion.fecha_notificacion = datetime.now(timezone.utc)
#         self._dao.actualizar_sancion(sancion)
#         return SancionOut.model_validate(sancion)

#     def listar_sanciones(self, operador_cuit: str | None = None) -> list[SancionOut]:
#         """Lista sanciones, opcionalmente filtradas por operador."""
#         sanciones = self._dao.listar_sanciones(operador_cuit=operador_cuit)
#         return [SancionOut.model_validate(s) for s in sanciones]

#     # ------------------------------------------------------------------
#     # Decomisos
#     # ------------------------------------------------------------------

#     def registrar_decomiso(self, data: DecomisoIn) -> DecomisoOut:
#         """Registra un decomiso."""
#         decomiso = Decomiso(
#             inspeccion_id=data.inspeccion_id,
#             mercaderia=data.mercaderia,
#             cantidad=data.cantidad,
#             peso_kg=data.peso_kg,
#             motivo=data.motivo,
#         )
#         self._dao.crear_decomiso(decomiso)
#         return DecomisoOut.model_validate(decomiso)

#     # ------------------------------------------------------------------
#     # Reincidencias
#     # ------------------------------------------------------------------

#     def obtener_reincidencia(self, operador_cuit: str) -> ReincidenciaOut | None:
#         """Obtiene la reincidencia de un operador."""
#         reincidencia = self._dao.obtener_reincidencia(operador_cuit)
#         return ReincidenciaOut.model_validate(reincidencia) if reincidencia else None
