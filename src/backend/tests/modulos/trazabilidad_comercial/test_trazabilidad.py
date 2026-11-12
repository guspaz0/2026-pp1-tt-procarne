# """Tests de los casos de uso del Módulo II — Trazabilidad Comercial."""

# from __future__ import annotations

# from datetime import datetime
# from decimal import Decimal

# import pytest

# from modulos.trazabilidad_comercial.dao import RegistroTrazabilidad, RegistroTrazabilidadDAO
# from modulos.trazabilidad_comercial.enums import EstadoTrazabilidad, Especie, TipoDestino, TipoIngreso
# from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn
# from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialError, TrazabilidadComercialService


# @pytest.fixture()
# def trazabilidad_dao(db_session_factory):
#     """DAO de trazabilidad."""
#     return RegistroTrazabilidadDAO(db_session_factory)


# @pytest.fixture()
# def trazabilidad_service(trazabilidad_dao):
#     """Servicio de trazabilidad."""
#     return TrazabilidadComercialService(trazabilidad_dao)


# def _datos_ingreso_base(**overrides):
#     """Construye un RegistroTrazabilidadIn válido."""
#     base = {
#         "tipo_ingreso": TipoIngreso.COMPRA.value,
#         "especie": Especie.BOVINO.value,
#         "cantidad": Decimal("10"),
#         "peso_kg": Decimal("500.5"),
#         "origen_cuit": "30111111111",
#         "destino_cuit": "30222222222",
#         "tipo_destino": TipoDestino.FRIGORIFICO.value,
#         "fecha_ingreso": datetime(2025, 6, 1, 10, 0, 0),
#         "numero_remito": "REM-001",
#         "numero_dte": "DTE-001",
#     }
#     base.update(overrides)
#     return RegistroTrazabilidadIn(**base)


# class TestTrazabilidadComercialService:
#     """Tests del servicio de trazabilidad comercial."""

#     def test_registrar_ingreso(self, trazabilidad_service):
#         data = _datos_ingreso_base()
#         resultado = trazabilidad_service.registrar_ingreso(data)
#         assert resultado.id is not None
#         assert resultado.estado == EstadoTrazabilidad.PENDIENTE.value
#         assert resultado.origen_cuit == "30111111111"
#         assert resultado.destino_cuit == "30222222222"

#     def test_obtener_por_id(self, trazabilidad_service):
#         data = _datos_ingreso_base()
#         creado = trazabilidad_service.registrar_ingreso(data)
#         obtenido = trazabilidad_service.obtener_por_id(creado.id)
#         assert obtenido is not None
#         assert obtenido.id == creado.id

#     def test_listar(self, trazabilidad_service):
#         for i in range(3):
#             data = _datos_ingreso_base(numero_remito=f"REM-00{i+1}")
#             trazabilidad_service.registrar_ingreso(data)

#         registros = trazabilidad_service.listar()
#         assert len(registros) == 3

#     def test_listar_filtrar_por_estado(self, trazabilidad_service):
#         data1 = _datos_ingreso_base(numero_remito="REM-001")
#         data2 = _datos_ingreso_base(numero_remito="REM-002")
#         r1 = trazabilidad_service.registrar_ingreso(data1)
#         r2 = trazabilidad_service.registrar_ingreso(data2)

#         trazabilidad_service.confirmar(r1.id)

#         pendientes = trazabilidad_service.listar(estado=EstadoTrazabilidad.PENDIENTE.value)
#         assert len(pendientes) == 1
#         assert pendientes[0].id == r2.id

#         confirmados = trazabilidad_service.listar(estado=EstadoTrazabilidad.CONFIRMADO.value)
#         assert len(confirmados) == 1
#         assert confirmados[0].id == r1.id

#     def test_listar_filtrar_por_especie(self, trazabilidad_service):
#         data1 = _datos_ingreso_base(especie=Especie.BOVINO.value, numero_remito="REM-001")
#         data2 = _datos_ingreso_base(especie=Especie.PORCINO.value, numero_remito="REM-002")
#         trazabilidad_service.registrar_ingreso(data1)
#         trazabilidad_service.registrar_ingreso(data2)

#         bovinos = trazabilidad_service.listar(especie=Especie.BOVINO.value)
#         assert len(bovinos) == 1
#         assert bovinos[0].especie == Especie.BOVINO.value

#         porcinos = trazabilidad_service.listar(especie=Especie.PORCINO.value)
#         assert len(porcinos) == 1
#         assert porcinos[0].especie == Especie.PORCINO.value

#     def test_listar_filtrar_por_origen(self, trazabilidad_service):
#         data1 = _datos_ingreso_base(origen_cuit="30111111111", numero_remito="REM-001")
#         data2 = _datos_ingreso_base(origen_cuit="30333333333", numero_remito="REM-002")
#         trazabilidad_service.registrar_ingreso(data1)
#         trazabilidad_service.registrar_ingreso(data2)

#         registros = trazabilidad_service.listar(origen_cuit="30111111111")
#         assert len(registros) == 1
#         assert registros[0].origen_cuit == "30111111111"

#     def test_listar_filtrar_por_destino(self, trazabilidad_service):
#         data1 = _datos_ingreso_base(destino_cuit="30222222222", numero_remito="REM-001")
#         data2 = _datos_ingreso_base(destino_cuit="30444444444", numero_remito="REM-002")
#         trazabilidad_service.registrar_ingreso(data1)
#         trazabilidad_service.registrar_ingreso(data2)

#         registros = trazabilidad_service.listar(destino_cuit="30222222222")
#         assert len(registros) == 1
#         assert registros[0].destino_cuit == "30222222222"

#     def test_confirmar(self, trazabilidad_service):
#         data = _datos_ingreso_base()
#         creado = trazabilidad_service.registrar_ingreso(data)
#         confirmado = trazabilidad_service.confirmar(creado.id)
#         assert confirmado.estado == EstadoTrazabilidad.CONFIRMADO.value

#     def test_anular(self, trazabilidad_service):
#         data = _datos_ingreso_base()
#         creado = trazabilidad_service.registrar_ingreso(data)
#         anulado = trazabilidad_service.anular(creado.id)
#         assert anulado.estado == EstadoTrazabilidad.ANULADO.value

#     def test_confirmar_no_existente(self, trazabilidad_service):
#         with pytest.raises(TrazabilidadComercialError):
#             trazabilidad_service.confirmar(999)

#     def test_anular_no_existente(self, trazabilidad_service):
#         with pytest.raises(TrazabilidadComercialError):
#             trazabilidad_service.anular(999)
