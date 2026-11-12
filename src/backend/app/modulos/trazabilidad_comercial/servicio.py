# """Servicio de negocio del Módulo II — Trazabilidad Comercial.

# Casos de uso:
# - Registrar un ingreso de mercadería.
# - Buscar por número de remito o DTE.
# - Listar registros (con filtros).
# - Confirmar o anular un registro.
# """

# from __future__ import annotations

# from modulos.trazabilidad_comercial.dao import RegistroTrazabilidad, RegistroTrazabilidadDAO
# from modulos.trazabilidad_comercial.enums import EstadoTrazabilidad
# from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn, RegistroTrazabilidadOut


# class TrazabilidadComercialError(Exception):
#     """Error de negocio del servicio de trazabilidad comercial."""


# class TrazabilidadComercialService:
#     """Servicio de negocio de trazabilidad comercial."""

#     def __init__(self, dao: RegistroTrazabilidadDAO) -> None:
#         self._dao = dao

#     def registrar_ingreso(self, data: RegistroTrazabilidadIn) -> RegistroTrazabilidadOut:
#         """Registra un ingreso de mercadería."""
#         registro = RegistroTrazabilidad(
#             tipo_ingreso=data.tipo_ingreso,
#             especie=data.especie,
#             cantidad=data.cantidad,
#             peso_kg=data.peso_kg,
#             origen_cuit=data.origen_cuit,
#             destino_cuit=data.destino_cuit,
#             tipo_destino=data.tipo_destino,
#             estado=EstadoTrazabilidad.PENDIENTE.value,
#             fecha_ingreso=data.fecha_ingreso,
#             numero_remito=data.numero_remito,
#             numero_dte=data.numero_dte,
#             observaciones=data.observaciones,
#         )
#         self._dao.crear(registro)
#         return RegistroTrazabilidadOut.model_validate(registro)

#     def obtener_por_id(self, registro_id: int) -> RegistroTrazabilidadOut | None:
#         """Busca un registro por su id."""
#         registro = self._dao.obtener_por_id(registro_id)
#         return RegistroTrazabilidadOut.model_validate(registro) if registro else None

#     def listar(self, estado: str | None = None, especie: str | None = None,
#                origen_cuit: str | None = None, destino_cuit: str | None = None) -> list[RegistroTrazabilidadOut]:
#         """Lista registros, opcionalmente filtrados."""
#         registros = self._dao.listar(
#             estado=estado, especie=especie,
#             origen_cuit=origen_cuit, destino_cuit=destino_cuit,
#         )
#         return [RegistroTrazabilidadOut.model_validate(r) for r in registros]

#     def confirmar(self, registro_id: int) -> RegistroTrazabilidadOut:
#         """Confirma un registro de trazabilidad."""
#         registro = self._dao.actualizar_estado(registro_id, EstadoTrazabilidad.CONFIRMADO.value)
#         if registro is None:
#             raise TrazabilidadComercialError(f"No existe un registro con id {registro_id}")
#         return RegistroTrazabilidadOut.model_validate(registro)

#     def anular(self, registro_id: int) -> RegistroTrazabilidadOut:
#         """Anula un registro de trazabilidad."""
#         registro = self._dao.actualizar_estado(registro_id, EstadoTrazabilidad.ANULADO.value)
#         if registro is None:
#             raise TrazabilidadComercialError(f"No existe un registro con id {registro_id}")
#         return RegistroTrazabilidadOut.model_validate(registro)
