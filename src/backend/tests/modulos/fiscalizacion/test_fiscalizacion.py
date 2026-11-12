# """Tests de los casos de uso del Módulo III — Fiscalización."""

# from __future__ import annotations

# from datetime import datetime
# from decimal import Decimal

# import pytest

# from modulos.fiscalizacion.dao import FiscalizacionDAO
# from modulos.fiscalizacion.enums import (
#     EstadoActa,
#     EstadoSancion,
#     GravedadInfraccion,
#     ResultadoInspeccion,
#     TipoActa,
#     TipoInfraccion,
#     TipoInspeccion,
#     TipoSancion,
# )
# from modulos.fiscalizacion.schema import (
#     ActaIn,
#     DecomisoIn,
#     InspeccionIn,
#     InfraccionIn,
#     SancionIn,
# )
# from modulos.fiscalizacion.servicio import FiscalizacionError, FiscalizacionService


# @pytest.fixture()
# def fiscalizacion_dao(db_session_factory):
#     """DAO de fiscalización."""
#     return FiscalizacionDAO(db_session_factory)


# @pytest.fixture()
# def fiscalizacion_service(fiscalizacion_dao):
#     """Servicio de fiscalización."""
#     return FiscalizacionService(fiscalizacion_dao)


# def _datos_inspeccion_base(**overrides):
#     """Construye un InspeccionIn válido."""
#     base = {
#         "tipo": TipoInspeccion.PROGRAMADA.value,
#         "operador_cuit": "30111111111",
#         "fecha": datetime(2025, 6, 1, 10, 0, 0),
#         "inspector": "Juan Pérez",
#     }
#     base.update(overrides)
#     return InspeccionIn(**base)


# def _datos_acta_base(inspeccion_id: int, **overrides):
#     """Construye un ActaIn válido."""
#     base = {
#         "inspeccion_id": inspeccion_id,
#         "tipo": TipoActa.INSPECCION.value,
#         "numero": "ACT-001",
#         "fecha": datetime(2025, 6, 1, 11, 0, 0),
#         "contenido": "Inspección realizada sin observaciones.",
#     }
#     base.update(overrides)
#     return ActaIn(**base)


# def _datos_infraccion_base(inspeccion_id: int, **overrides):
#     """Construye un InfraccionIn válido."""
#     base = {
#         "inspeccion_id": inspeccion_id,
#         "operador_cuit": "30111111111",
#         "tipo": TipoInfraccion.INCUMPLIMIENTO_NORMAS.value,
#         "gravedad": GravedadInfraccion.GRAVE.value,
#         "descripcion": "Falta de trazabilidad en el 20% de la mercadería.",
#     }
#     base.update(overrides)
#     return InfraccionIn(**base)


# def _datos_sancion_base(infraccion_id: int, **overrides):
#     """Construye un SancionIn válido."""
#     base = {
#         "infraccion_id": infraccion_id,
#         "operador_cuit": "30111111111",
#         "tipo": TipoSancion.MULTA.value,
#         "monto": Decimal("50000.00"),
#     }
#     base.update(overrides)
#     return SancionIn(**base)


# def _datos_decomiso_base(inspeccion_id: int, **overrides):
#     """Construye un DecomisoIn válido."""
#     base = {
#         "inspeccion_id": inspeccion_id,
#         "mercaderia": "Carne bovina",
#         "cantidad": Decimal("100"),
#         "peso_kg": Decimal("500.5"),
#         "motivo": "Mala conservación",
#     }
#     base.update(overrides)
#     return DecomisoIn(**base)


# class TestFiscalizacionService:
#     """Tests del servicio de fiscalización."""

#     # ------------------------------------------------------------------
#     # Inspecciones
#     # ------------------------------------------------------------------

#     def test_registrar_inspeccion(self, fiscalizacion_service):
#         data = _datos_inspeccion_base()
#         resultado = fiscalizacion_service.registrar_inspeccion(data)
#         assert resultado.id is not None
#         assert resultado.tipo == TipoInspeccion.PROGRAMADA.value
#         assert resultado.operador_cuit == "30111111111"
#         assert resultado.inspector == "Juan Pérez"

#     def test_obtener_inspeccion(self, fiscalizacion_service):
#         data = _datos_inspeccion_base()
#         creado = fiscalizacion_service.registrar_inspeccion(data)
#         obtenido = fiscalizacion_service.obtener_inspeccion(creado.id)
#         assert obtenido is not None
#         assert obtenido.id == creado.id

#     def test_listar_inspecciones(self, fiscalizacion_service):
#         for i in range(3):
#             data = _datos_inspeccion_base(operador_cuit=f"3011111111{i}")
#             fiscalizacion_service.registrar_inspeccion(data)

#         inspecciones = fiscalizacion_service.listar_inspecciones()
#         assert len(inspecciones) == 3

#     def test_listar_inspecciones_filtrar_por_operador(self, fiscalizacion_service):
#         data1 = _datos_inspeccion_base(operador_cuit="30111111111")
#         data2 = _datos_inspeccion_base(operador_cuit="30222222222")
#         fiscalizacion_service.registrar_inspeccion(data1)
#         fiscalizacion_service.registrar_inspeccion(data2)

#         inspecciones = fiscalizacion_service.listar_inspecciones(operador_cuit="30111111111")
#         assert len(inspecciones) == 1
#         assert inspecciones[0].operador_cuit == "30111111111"

#     # ------------------------------------------------------------------
#     # Actas
#     # ------------------------------------------------------------------

#     def test_crear_acta(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data_acta = _datos_acta_base(inspeccion.id)
#         resultado = fiscalizacion_service.crear_acta(data_acta)
#         assert resultado.id is not None
#         assert resultado.tipo == TipoActa.INSPECCION.value
#         assert resultado.numero == "ACT-001"
#         assert resultado.estado == EstadoActa.BORRADOR.value

#     def test_firmar_acta(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data_acta = _datos_acta_base(inspeccion.id)
#         acta = fiscalizacion_service.crear_acta(data_acta)

#         resultado = fiscalizacion_service.firmar_acta(acta.id, "Juan Pérez")
#         assert resultado.estado == EstadoActa.FIRMADA.value
#         assert resultado.firmado_por == "Juan Pérez"
#         assert resultado.fecha_firma is not None

#     def test_firmar_acta_no_existente(self, fiscalizacion_service):
#         with pytest.raises(FiscalizacionError):
#             fiscalizacion_service.firmar_acta(999, "Juan Pérez")

#     def test_listar_actas(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         for i in range(3):
#             data_acta = _datos_acta_base(inspeccion.id, numero=f"ACT-00{i+1}")
#             fiscalizacion_service.crear_acta(data_acta)

#         actas = fiscalizacion_service.listar_actas(inspeccion_id=inspeccion.id)
#         assert len(actas) == 3

#     # ------------------------------------------------------------------
#     # Infracciones
#     # ------------------------------------------------------------------

#     def test_registrar_infraccion(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data_infraccion = _datos_infraccion_base(inspeccion.id)
#         resultado = fiscalizacion_service.registrar_infraccion(data_infraccion)
#         assert resultado.id is not None
#         assert resultado.tipo == TipoInfraccion.INCUMPLIMIENTO_NORMAS.value
#         assert resultado.gravedad == GravedadInfraccion.GRAVE.value

#     def test_listar_infracciones(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         for i in range(3):
#             data_infraccion = _datos_infraccion_base(inspeccion.id, operador_cuit=f"3011111111{i}")
#             fiscalizacion_service.registrar_infraccion(data_infraccion)

#         infracciones = fiscalizacion_service.listar_infracciones()
#         assert len(infracciones) == 3

#     def test_listar_infracciones_filtrar_por_operador(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data1 = _datos_infraccion_base(inspeccion.id, operador_cuit="30111111111")
#         data2 = _datos_infraccion_base(inspeccion.id, operador_cuit="30222222222")
#         fiscalizacion_service.registrar_infraccion(data1)
#         fiscalizacion_service.registrar_infraccion(data2)

#         infracciones = fiscalizacion_service.listar_infracciones(operador_cuit="30111111111")
#         assert len(infracciones) == 1
#         assert infracciones[0].operador_cuit == "30111111111"

#     # ------------------------------------------------------------------
#     # Sanciones
#     # ------------------------------------------------------------------

#     def test_aplicar_sancion(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data_infraccion = _datos_infraccion_base(inspeccion.id)
#         infraccion = fiscalizacion_service.registrar_infraccion(data_infraccion)

#         data_sancion = _datos_sancion_base(infraccion.id)
#         resultado = fiscalizacion_service.aplicar_sancion(data_sancion)
#         assert resultado.id is not None
#         assert resultado.tipo == TipoSancion.MULTA.value
#         assert resultado.monto == Decimal("50000.00")
#         assert resultado.estado == EstadoSancion.PENDIENTE.value

#     def test_notificar_sancion(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data_infraccion = _datos_infraccion_base(inspeccion.id)
#         infraccion = fiscalizacion_service.registrar_infraccion(data_infraccion)

#         data_sancion = _datos_sancion_base(infraccion.id)
#         sancion = fiscalizacion_service.aplicar_sancion(data_sancion)

#         resultado = fiscalizacion_service.notificar_sancion(sancion.id)
#         assert resultado.estado == EstadoSancion.NOTIFICADA.value
#         assert resultado.fecha_notificacion is not None

#     def test_notificar_sancion_no_existente(self, fiscalizacion_service):
#         with pytest.raises(FiscalizacionError):
#             fiscalizacion_service.notificar_sancion(999)

#     def test_listar_sanciones(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         for i in range(3):
#             data_infraccion = _datos_infraccion_base(inspeccion.id, operador_cuit=f"3011111111{i}")
#             infraccion = fiscalizacion_service.registrar_infraccion(data_infraccion)
#             data_sancion = _datos_sancion_base(infraccion.id, operador_cuit=f"3011111111{i}")
#             fiscalizacion_service.aplicar_sancion(data_sancion)

#         sanciones = fiscalizacion_service.listar_sanciones()
#         assert len(sanciones) == 3

#     # ------------------------------------------------------------------
#     # Decomisos
#     # ------------------------------------------------------------------

#     def test_registrar_decomiso(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data_decomiso = _datos_decomiso_base(inspeccion.id)
#         resultado = fiscalizacion_service.registrar_decomiso(data_decomiso)
#         assert resultado.id is not None
#         assert resultado.mercaderia == "Carne bovina"
#         assert resultado.cantidad == Decimal("100")
#         assert resultado.peso_kg == Decimal("500.5")

#     # ------------------------------------------------------------------
#     # Reincidencias
#     # ------------------------------------------------------------------

#     def test_obtener_reincidencia(self, fiscalizacion_service):
#         data_inspeccion = _datos_inspeccion_base()
#         inspeccion = fiscalizacion_service.registrar_inspeccion(data_inspeccion)

#         data_infraccion = _datos_infraccion_base(inspeccion.id, operador_cuit="30111111111")
#         fiscalizacion_service.registrar_infraccion(data_infraccion)

#         reincidencia = fiscalizacion_service.obtener_reincidencia("30111111111")
#         assert reincidencia is not None
#         assert reincidencia.cantidad_infracciones == 1

#     def test_obtener_reincidencia_no_existente(self, fiscalizacion_service):
#         reincidencia = fiscalizacion_service.obtener_reincidencia("30999999999")
#         assert reincidencia is None
