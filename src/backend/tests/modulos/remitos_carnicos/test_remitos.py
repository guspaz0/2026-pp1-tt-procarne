# """Tests del módulo de Remitos Electrónicos Cárnicos."""

# from __future__ import annotations

# from datetime import datetime
# from decimal import Decimal

# import pytest

# from modulos.remitos_carnicos.operador.dao import OperadorORM
# from core.mercaderia.dao import Mercaderia
# from modulos.remitos_carnicos.remito.dao import RemitoCarnico, RenglonRemito
# from modulos.remitos_carnicos.remito.servicio import RemitoCarnicoService, RemitoCarnicoError
# from modulos.remitos_carnicos.remito.schema import RemitoCarnicoIn, RenglonRemitoIn
# from modulos.remitos_carnicos.enums import CasoRemito, TipoMovimiento
# from tests.modulos.remitos_carnicos.conftest import obtener_operador_id_por_cuit


# # ---------------------------------------------------------------------------
# # Fixtures locales (los fixtures de BD provienen de conftest.py)
# # ---------------------------------------------------------------------------

# @pytest.fixture()
# def remito_service(remito_dao, operador_dao, mercaderia_dao):
#     return RemitoCarnicoService(remito_dao, operador_dao, mercaderia_dao)


# def _datos_remito_base(seed_operadores, **overrides):
#     """Construye un RemitoCarnicoIn válido (caso 01: envío normal con destinatario)."""
#     base = {
#         "punto_emision": "0001",
#         "numero_comprobante": "0000000001",
#         "caso": CasoRemito.CASO_01,
#         "tipo_movimiento": TipoMovimiento.ENVIO_NORMAL,
#         "fecha_emision": datetime(2025, 6, 1, 10, 0, 0),
#         "fecha_vencimiento": datetime(2025, 6, 2, 10, 0, 0),
#         "titular_cuit": seed_operadores["titular"],
#         "transportista_cuit": seed_operadores["transportista"],
#         "destinatario_cuit": seed_operadores["destinatario"],
#         "chofer_apellido_nombre": "Juan Pérez",
#         "chofer_documento": "12345678",
#         "dominio_vehiculo": "ABC123",
#         "renglones": [
#             RenglonRemitoIn(codigo_afip="1101", unidades=Decimal("100"), kilos=Decimal("500.5"), numero_tropa="T-001"),
#         ],
#     }
#     base.update(overrides)
#     return RemitoCarnicoIn(**base)


# # ---------------------------------------------------------------------------
# # Tests: DAO
# # ---------------------------------------------------------------------------

# class TestRemitoDAO:
#     """Tests del DAO de remitos."""

#     def test_guardar(self, remito_dao, session_factory, seed_operadores, seed_mercaderias):
#         op_ids = {}
#         with session_factory() as session:
#             op_ids["titular"] = obtener_operador_id_por_cuit(session, seed_operadores["titular"])

#         remito = RemitoCarnico(
#             punto_emision="001",
#             numero_comprobante="0000000001",
#             caso="01",
#             tipo_movimiento="ENVIO_NORMAL",
#             fecha_emision=datetime(2025, 6, 1, 10, 0, 0),
#             fecha_vencimiento=datetime(2025, 6, 2, 10, 0, 0),
#             titular_cuit=seed_operadores["titular"],
#             transportista_cuit=seed_operadores["transportista"],
#             destinatario_cuit=seed_operadores["destinatario"],
#         )
#         remito.renglones.append(
#             RenglonRemito(codigo_afip="1101", unidades=Decimal("100"), kilos=Decimal("500.5"))
#         )

#         guardado = remito_dao.crear(remito)
#         assert guardado.id is not None
#         assert guardado.punto_emision == "001"

#     def test_obtener_por_id(self, remito_dao, session_factory, seed_operadores, seed_mercaderias):
#         remito = RemitoCarnico(
#             punto_emision="001",
#             numero_comprobante="0000000001",
#             caso="01",
#             tipo_movimiento="ENVIO_NORMAL",
#             fecha_emision=datetime(2025, 6, 1, 10, 0, 0),
#             fecha_vencimiento=datetime(2025, 6, 2, 10, 0, 0),
#             titular_cuit=seed_operadores["titular"],
#             transportista_cuit=seed_operadores["transportista"],
#         )
#         guardado = remito_dao.crear(remito)

#         obtenido = remito_dao.obtener_por_id(guardado.id)
#         assert obtenido is not None
#         assert obtenido.id == guardado.id

#     def test_obtener_por_comprobante(self, remito_dao, session_factory, seed_operadores):
#         remito = RemitoCarnico(
#             punto_emision="001",
#             numero_comprobante="0000000001",
#             caso="01",
#             tipo_movimiento="ENVIO_NORMAL",
#             fecha_emision=datetime(2025, 6, 1, 10, 0, 0),
#             fecha_vencimiento=datetime(2025, 6, 2, 10, 0, 0),
#             titular_cuit=seed_operadores["titular"],
#             transportista_cuit=seed_operadores["transportista"],
#         )
#         remito_dao.crear(remito)

#         obtenido = remito_dao.obtener_por_comprobante("001", "0000000001")
#         assert obtenido is not None
#         assert obtenido.punto_emision == "001"

#     def test_listar(self, remito_dao, session_factory, seed_operadores):
#         for i in range(3):
#             remito = RemitoCarnico(
#                 punto_emision="001",
#                 numero_comprobante=f"000000000{i+1}",
#                 caso="01",
#                 tipo_movimiento="ENVIO_NORMAL",
#                 fecha_emision=datetime(2025, 6, 1, 10, 0, 0),
#                 fecha_vencimiento=datetime(2025, 6, 2, 10, 0, 0),
#                 titular_cuit=seed_operadores["titular"],
#                 transportista_cuit=seed_operadores["transportista"],
#             )
#             remito_dao.crear(remito)

#         remitos = remito_dao.listar()
#         assert len(remitos) == 3


# # ---------------------------------------------------------------------------
# # Tests: Servicio
# # ---------------------------------------------------------------------------

# class TestRemitoCarnicoService:
#     """Tests del servicio de remitos."""

#     def test_emitir_remito(self, remito_service, seed_operadores, seed_mercaderias):
#         data = _datos_remito_base(seed_operadores)
#         resultado = remito_service.emitir_remito(data)
#         assert resultado.id is not None
#         assert resultado.estado == "EMITIDO"
#         assert len(resultado.renglones) == 1

#     def test_emitir_remito_punto_emision_invalido(self, remito_service, seed_operadores, seed_mercaderias):
#         data = _datos_remito_base(seed_operadores, punto_emision="12")
#         with pytest.raises(RemitoCarnicoError):
#             remito_service.emitir_remito(data)

#     def test_emitir_remito_numero_comprobante_invalido(self, remito_service, seed_operadores, seed_mercaderias):
#         data = _datos_remito_base(seed_operadores, numero_comprobante="123")
#         with pytest.raises(RemitoCarnicoError):
#             remito_service.emitir_remito(data)

#     def test_emitir_remito_fecha_vencimiento_invalida(self, remito_service, seed_operadores, seed_mercaderias):
#         data = _datos_remito_base(
#             seed_operadores,
#             fecha_vencimiento=datetime(2025, 5, 31, 10, 0, 0),
#         )
#         with pytest.raises(RemitoCarnicoError):
#             remito_service.emitir_remito(data)

#     def test_emitir_remito_sin_renglones(self, remito_service, seed_operadores, seed_mercaderias):
#         data = _datos_remito_base(seed_operadores, renglones=[])
#         with pytest.raises(RemitoCarnicoError):
#             remito_service.emitir_remito(data)

#     def test_emitir_remito_mercaderia_inexistente(self, remito_service, seed_operadores, seed_mercaderias):
#         data = _datos_remito_base(
#             seed_operadores,
#             renglones=[RenglonRemitoIn(codigo_afip="9999", unidades=Decimal("10"), kilos=Decimal("50"))],
#         )
#         with pytest.raises(RemitoCarnicoError):
#             remito_service.emitir_remito(data)

#     def test_cambiar_estado(self, remito_service, seed_operadores, seed_mercaderias):
#         data = _datos_remito_base(seed_operadores)
#         emitido = remito_service.emitir_remito(data)

#         from modulos.remitos_carnicos.enums import EstadoRemito
#         resultado = remito_service.cambiar_estado(emitido.id, EstadoRemito.ENTREGADO)
#         assert resultado.estado == "ENTREGADO"
#         assert resultado.fecha_entrega is not None

#     def test_listar(self, remito_service, seed_operadores, seed_mercaderias):
#         for i in range(3):
#             data = _datos_remito_base(seed_operadores, numero_comprobante=f"000000000{i+1}")
#             remito_service.emitir_remito(data)

#         remitos = remito_service.listar()
#         assert len(remitos) == 3
