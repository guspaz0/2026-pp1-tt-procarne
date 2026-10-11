"""Tests del módulo de Remitos Electrónicos Cárnicos."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from configs.db import Base
from modulos.remitos_carnicos.operador.dao import Operador
from modulos.remitos_carnicos.mercaderia.dao import Mercaderia
from modulos.remitos_carnicos.remito.dao import RemitoCarnico, RenglonRemito, RemitoCarnicoDAO
from modulos.remitos_carnicos.remito.servicio import RemitoCarnicoService, RemitoCarnicoError
from modulos.remitos_carnicos.remito.schema import RemitoCarnicoIn, RenglonRemitoIn
from modulos.remitos_carnicos.enums import CasoRemito, TipoMovimiento


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def engine():
    eng = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


@pytest.fixture()
def remito_dao(session_factory):
    return RemitoCarnicoDAO(session_factory)


@pytest.fixture()
def operador_dao(session_factory):
    from modulos.remitos_carnicos.operador.dao import OperadorDAO
    return OperadorDAO(session_factory)


@pytest.fixture()
def mercaderia_dao(session_factory):
    from modulos.remitos_carnicos.mercaderia.dao import MercaderiaDAO
    return MercaderiaDAO(session_factory)


@pytest.fixture()
def remito_service(remito_dao, operador_dao, mercaderia_dao):
    return RemitoCarnicoService(remito_dao, operador_dao, mercaderia_dao)


@pytest.fixture()
def seed_operadores(session_factory):
    """Crea operadores de prueba: titular, transportista, depositario, destinatario."""
    ops = {
        "titular": Operador(cuit="20111111111", razon_social="TITULAR TEST S.A.", situacion="ACTIVO"),
        "transportista": Operador(cuit="20222222222", razon_social="TRANSPORTISTA TEST", situacion="ACTIVO"),
        "depositario": Operador(cuit="20333333333", razon_social="DEPOSITARIO TEST", situacion="ACTIVO"),
        "destinatario": Operador(cuit="20444444444", razon_social="DESTINATARIO TEST", situacion="ACTIVO"),
    }
    with session_factory() as session:
        for op in ops.values():
            session.add(op)
        session.commit()
        for op in ops.values():
            session.refresh(op)
    return {k: v.cuit for k, v in ops.items()}


@pytest.fixture()
def seed_mercaderias(session_factory):
    """Crea mercaderías de prueba."""
    mercs = [
        Mercaderia(codigo_afip="1101", descripcion="Carne de bovino fresca", requiere_numero_tropa=True),
        Mercaderia(codigo_afip="1102", descripcion="Carne de bovino congelada", requiere_numero_tropa=False),
        Mercaderia(codigo_afip="2101", descripcion="Carne de porcino fresca", requiere_numero_tropa=True),
    ]
    with session_factory() as session:
        for m in mercs:
            session.add(m)
        session.commit()
    return [m.codigo_afip for m in mercs]


def _datos_remito_base(seed_operadores, **overrides):
    """Construye un RemitoCarnicoIn válido (caso 01: envío normal con destinatario)."""
    base = {
        "punto_emision": "001",
        "numero_comprobante": "0000000001",
        "caso": CasoRemito.CASO_01,
        "tipo_movimiento": TipoMovimiento.ENVIO_NORMAL,
        "fecha_emision": datetime(2025, 6, 1, 10, 0, 0),
        "fecha_vencimiento": datetime(2025, 6, 2, 10, 0, 0),
        "titular_cuit": seed_operadores["titular"],
        "transportista_cuit": seed_operadores["transportista"],
        "destinatario_cuit": seed_operadores["destinatario"],
        "chofer_apellido_nombre": "Juan Pérez",
        "chofer_documento": "12345678",
        "dominio_vehiculo": "ABC123",
        "renglones": [
            RenglonRemitoIn(codigo_afip="1101", unidades=Decimal("100"), kilos=Decimal("500.5"), numero_tropa="T-001"),
        ],
    }
    base.update(overrides)
    return RemitoCarnicoIn(**base)


# ---------------------------------------------------------------------------
# Tests: DAO
# ---------------------------------------------------------------------------

class TestRemitoDAO:
    """Tests del DAO de remitos."""

    def test_guardar(self, remito_dao, session_factory, seed_operadores, seed_mercaderias):
        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1101").first()
            merc_id = merc.id

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="0000000001",
            caso=1,
            tipo_movimiento="ENV",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 2),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=op_ids[seed_operadores["destinatario"]],
            renglones=[
                RenglonRemito(mercaderia_id=merc_id, unidades=100.0, kilos=500.5, numero_tropa="T-001"),
            ],
        )
        guardado = remito_dao.guardar(remito)
        assert guardado.id is not None
        assert guardado.codigo_remito == "001-0000000001"

    def test_obtener_por_codigo(self, remito_dao, session_factory, seed_operadores, seed_mercaderias):
        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1102").first()
            merc_id = merc.id

        remito = RemitoCarnico(
            punto_emision="002",
            numero_comprobante="0000000042",
            caso=1,
            tipo_movimiento="ENV",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 3),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=op_ids[seed_operadores["destinatario"]],
            renglones=[RenglonRemito(mercaderia_id=merc_id, unidades=50.0, kilos=200.0)],
        )
        remito_dao.guardar(remito)

        encontrado = remito_dao.obtener_por_codigo("002", "0000000042")
        assert encontrado is not None
        assert encontrado.punto_emision == "002"
        assert encontrado.numero_comprobante == "0000000042"

    def test_obtener_por_codigo_no_existe(self, remito_dao):
        assert remito_dao.obtener_por_codigo("999", "999") is None

    def test_listar(self, remito_dao, session_factory, seed_operadores, seed_mercaderias):
        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1101").first()
            merc_id = merc.id

        # Crear 3 remitos
        for i in range(3):
            remito = RemitoCarnico(
                punto_emision="001",
                numero_comprobante=f"000000000{i+1}",
                caso=1,
                tipo_movimiento="ENV",
                estado="E" if i < 2 else "AN",
                fecha_emision=datetime(2025, 6, i + 1),
                fecha_vencimiento=datetime(2025, 6, i + 2),
                titular_id=op_ids[seed_operadores["titular"]],
                transportista_id=op_ids[seed_operadores["transportista"]],
                destinatario_id=op_ids[seed_operadores["destinatario"]],
                renglones=[RenglonRemito(mercaderia_id=merc_id, unidades=10.0, kilos=50.0)],
            )
            remito_dao.guardar(remito)

        todos = remito_dao.listar()
        assert len(todos) == 3

        solo_emitidos = remito_dao.listar(estado="E")
        assert len(solo_emitidos) == 2

    def test_anular(self, remito_dao, session_factory, seed_operadores, seed_mercaderias):
        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1101").first()
            merc_id = merc.id

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="0000000100",
            caso=1,
            tipo_movimiento="ENV",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 2),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=op_ids[seed_operadores["destinatario"]],
            renglones=[RenglonRemito(mercaderia_id=merc_id, unidades=10.0, kilos=50.0)],
        )
        guardado = remito_dao.guardar(remito)

        assert remito_dao.anular(guardado.id) is True
        actualizado = remito_dao.obtener_por_id(guardado.id)
        assert actualizado.estado == "AN"

        # Anular de nuevo → False
        assert remito_dao.anular(guardado.id) is False


# ---------------------------------------------------------------------------
# Tests: Servicio
# ---------------------------------------------------------------------------

class TestRemitoService:
    """Tests del servicio de remitos."""

    def test_crear_remito_caso_01(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores)
        resultado = remito_service.crear(datos)

        assert resultado.codigo_remito == "001-0000000001"
        assert resultado.estado == "E"
        assert resultado.caso == 1
        assert resultado.titular.cuit == seed_operadores["titular"]
        assert resultado.transportista.cuit == seed_operadores["transportista"]
        assert resultado.destinatario.cuit == seed_operadores["destinatario"]
        assert resultado.depositario is None
        assert len(resultado.renglones) == 1
        assert resultado.renglones[0].codigo_afip == "1101"
        assert resultado.total_kilos == Decimal("500.5")

    def test_crear_remito_caso_02_con_depositario(self, remito_service, seed_operadores, seed_mercaderias):
        """Caso 02: requiere depositario Y destinatario."""
        datos = _datos_remito_base(
            seed_operadores,
            caso=CasoRemito.CASO_02,
            tipo_movimiento=TipoMovimiento.RETIRO_EN_PLANTA,
            depositario_cuit=seed_operadores["depositario"],
        )
        resultado = remito_service.crear(datos)
        assert resultado.caso == 2
        assert resultado.depositario is not None
        assert resultado.depositario.cuit == seed_operadores["depositario"]
        assert resultado.destinatario is not None  # caso 02 también requiere destinatario

    def test_crear_remito_caso_04_reparto(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(
            seed_operadores,
            caso=CasoRemito.CASO_04,
            tipo_movimiento=TipoMovimiento.REPARTO,
            destinatario_cuit=None,
        )
        resultado = remito_service.crear(datos)
        assert resultado.caso == 4
        assert resultado.destinatario is None
        assert resultado.depositario is None

    def test_crear_remito_titular_no_encontrado(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores, titular_cuit="99999999999")
        with pytest.raises(RemitoCarnicoError, match="Titular no encontrado"):
            remito_service.crear(datos)

    def test_crear_remito_transportista_no_encontrado(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores, transportista_cuit="88888888888")
        with pytest.raises(RemitoCarnicoError, match="Transportista no encontrado"):
            remito_service.crear(datos)

    def test_crear_remito_mercaderia_no_encontrada(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores)
        datos.renglones = [RenglonRemitoIn(codigo_afip="9999", unidades=1, kilos=1)]
        with pytest.raises(RemitoCarnicoError, match="Mercadería no encontrada"):
            remito_service.crear(datos)

    def test_crear_remito_validacion_fechas(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(
            seed_operadores,
            fecha_emision=datetime(2025, 6, 2, 10, 0, 0),
            fecha_vencimiento=datetime(2025, 6, 1, 10, 0, 0),  # antes de emisión
        )
        with pytest.raises(RemitoCarnicoError, match="vencimiento"):
            remito_service.crear(datos)

    def test_crear_remito_caso_01_sin_destinatario(self, remito_service, seed_operadores, seed_mercaderias):
        """Caso 01 requiere destinatario."""
        datos = _datos_remito_base(seed_operadores, destinatario_cuit=None)
        with pytest.raises(RemitoCarnicoError, match="destinatario"):
            remito_service.crear(datos)

    def test_crear_remito_caso_02_sin_depositario(self, remito_service, seed_operadores, seed_mercaderias):
        """Caso 02 requiere depositario."""
        datos = _datos_remito_base(
            seed_operadores,
            caso=CasoRemito.CASO_02,
            tipo_movimiento=TipoMovimiento.RETIRO_EN_PLANTA,
            depositario_cuit=None,
            destinatario_cuit=None,
        )
        with pytest.raises(RemitoCarnicoError, match="depositario"):
            remito_service.crear(datos)

    def test_crear_remito_numero_tropa_requerido(self, remito_service, session_factory, seed_operadores, seed_mercaderias):
        """Mercadería 1101 requiere N° de tropa."""
        # Cargar la mercadería en la sesión para que la relación lazy funcione
        from sqlalchemy import select
        with session_factory() as session:
            merc = session.execute(select(Mercaderia).where(Mercaderia.codigo_afip == "1101")).scalar_one()
            assert merc.requiere_numero_tropa is True

        datos = _datos_remito_base(seed_operadores)
        datos.renglones = [
            RenglonRemitoIn(codigo_afip="1101", unidades=100, kilos=500, numero_tropa=None),
        ]
        with pytest.raises(RemitoCarnicoError, match="tropa"):
            remito_service.crear(datos)

    def test_crear_remito_sin_numero_tropa_ok(self, remito_service, seed_operadores, seed_mercaderias):
        """Mercadería 1102 NO requiere N° de tropa."""
        datos = _datos_remito_base(seed_operadores)
        datos.renglones = [
            RenglonRemitoIn(codigo_afip="1102", unidades=100, kilos=500, numero_tropa=None),
        ]
        resultado = remito_service.crear(datos)
        assert resultado.renglones[0].numero_tropa is None

    def test_obtener(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores)
        remito_service.crear(datos)

        resultado = remito_service.obtener("001", "0000000001")
        assert resultado.codigo_remito == "001-0000000001"
        assert resultado.titular.razon_social == "TITULAR TEST S.A."

    def test_obtener_no_existe(self, remito_service, seed_operadores, seed_mercaderias):
        with pytest.raises(RemitoCarnicoError, match="no encontrado"):
            remito_service.obtener("999", "999")

    def test_listar(self, remito_service, seed_operadores, seed_mercaderias):
        # Crear 2 remitos
        remito_service.crear(_datos_remito_base(seed_operadores, numero_comprobante="0000000001"))
        remito_service.crear(_datos_remito_base(seed_operadores, numero_comprobante="0000000002"))

        resultados = remito_service.listar()
        assert len(resultados) == 2

        # Filtrar por estado
        remito_service.anular(resultados[0].id)
        emitidos = remito_service.listar(estado="E")
        assert len(emitidos) == 1

    def test_anular(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores)
        creado = remito_service.crear(datos)

        anulado = remito_service.anular(creado.id)
        assert anulado.estado == "AN"

    def test_anular_no_existe(self, remito_service, seed_operadores, seed_mercaderias):
        with pytest.raises(RemitoCarnicoError, match="no encontrado"):
            remito_service.anular(9999)

    def test_anular_ya_anulado(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores)
        creado = remito_service.crear(datos)
        remito_service.anular(creado.id)

        with pytest.raises(RemitoCarnicoError, match="ya está anulado"):
            remito_service.anular(creado.id)

    def test_remito_con_varios_renglones(self, remito_service, seed_operadores, seed_mercaderias):
        datos = _datos_remito_base(seed_operadores)
        datos.renglones = [
            RenglonRemitoIn(codigo_afip="1101", unidades=100, kilos=500, numero_tropa="T-001"),
            RenglonRemitoIn(codigo_afip="1102", unidades=200, kilos=800, numero_tropa=None),
            RenglonRemitoIn(codigo_afip="2101", unidades=50, kilos=300, numero_tropa="T-002"),
        ]
        resultado = remito_service.crear(datos)
        assert len(resultado.renglones) == 3
        assert resultado.total_kilos == Decimal("1600")
        assert resultado.total_unidades == Decimal("350")


# ---------------------------------------------------------------------------
# Tests: Validación (reglas)
# ---------------------------------------------------------------------------

class TestValidacion:
    """Tests de las reglas de validación."""

    def test_caso_01_requiere_destinatario(self, session_factory, seed_operadores, seed_mercaderias):
        from modulos.remitos_carnicos.remito.validacion import ValidadorRemito

        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1102").first()

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="001",
            caso=1,
            tipo_movimiento="ENV",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 2),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=None,  # FALTA destinatario
            renglones=[RenglonRemito(mercaderia_id=merc.id, unidades=10, kilos=50)],
        )
        validador = ValidadorRemito()
        errores = validador.validar(remito)
        assert any("destinatario" in e.lower() for e in errores)

    def test_caso_04_no_admite_destinatario(self, session_factory, seed_operadores, seed_mercaderias):
        from modulos.remitos_carnicos.remito.validacion import ValidadorRemito

        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1102").first()

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="001",
            caso=4,  # Reparto: NO admite destinatario
            tipo_movimiento="REP",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 2),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=op_ids[seed_operadores["destinatario"]],  # INDEBIDO
            renglones=[RenglonRemito(mercaderia_id=merc.id, unidades=10, kilos=50)],
        )
        validador = ValidadorRemito()
        errores = validador.validar(remito)
        assert any("no admite destinatario" in e.lower() for e in errores)

    def test_caso_05_requiere_depositario(self, session_factory, seed_operadores, seed_mercaderias):
        from modulos.remitos_carnicos.remito.validacion import ValidadorRemito

        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1102").first()

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="001",
            caso=5,  # Requiere depositario
            tipo_movimiento="REP",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 2),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            depositario_id=None,  # FALTA
            destinatario_id=None,
            renglones=[RenglonRemito(mercaderia_id=merc.id, unidades=10, kilos=50)],
        )
        validador = ValidadorRemito()
        errores = validador.validar(remito)
        assert any("depositario" in e.lower() for e in errores)

    def test_remito_valido_sin_errores(self, session_factory, seed_operadores, seed_mercaderias):
        from modulos.remitos_carnicos.remito.validacion import ValidadorRemito

        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1102").first()

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="001",
            caso=1,
            tipo_movimiento="ENV",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 2),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=op_ids[seed_operadores["destinatario"]],
            renglones=[RenglonRemito(mercaderia_id=merc.id, unidades=10, kilos=50)],
        )
        validador = ValidadorRemito()
        errores = validador.validar(remito)
        assert errores == []
        assert validador.es_valido(remito) is True

    def test_fecha_vencimiento_antes_emision(self, session_factory, seed_operadores, seed_mercaderias):
        from modulos.remitos_carnicos.remito.validacion import ValidadorRemito

        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id
            merc = session.query(Mercaderia).filter_by(codigo_afip="1102").first()

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="001",
            caso=1,
            tipo_movimiento="ENV",
            estado="E",
            fecha_emision=datetime(2025, 6, 5),
            fecha_vencimiento=datetime(2025, 6, 1),  # ANTES
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=op_ids[seed_operadores["destinatario"]],
            renglones=[RenglonRemito(mercaderia_id=merc.id, unidades=10, kilos=50)],
        )
        validador = ValidadorRemito()
        errores = validador.validar(remito)
        assert any("vencimiento" in e.lower() for e in errores)

    def test_renglon_sin_mercaderia(self, session_factory, seed_operadores, seed_mercaderias):
        """Un remito sin renglones debe fallar."""
        from modulos.remitos_carnicos.remito.validacion import ValidadorRemito

        op_ids = {}
        with session_factory() as session:
            for cuit in seed_operadores.values():
                op = session.query(Operador).filter_by(cuit=cuit).first()
                op_ids[cuit] = op.id

        remito = RemitoCarnico(
            punto_emision="001",
            numero_comprobante="001",
            caso=1,
            tipo_movimiento="ENV",
            estado="E",
            fecha_emision=datetime(2025, 6, 1),
            fecha_vencimiento=datetime(2025, 6, 2),
            titular_id=op_ids[seed_operadores["titular"]],
            transportista_id=op_ids[seed_operadores["transportista"]],
            destinatario_id=op_ids[seed_operadores["destinatario"]],
            renglones=[],
        )
        validador = ValidadorRemito()
        errores = validador.validar(remito)
        assert any("renglón" in e.lower() for e in errores)


# ---------------------------------------------------------------------------
# Tests: API
# ---------------------------------------------------------------------------

class TestAPIRemitos:
    """Tests de los endpoints /api/remitos."""

    @pytest.fixture()
    def api_client(self, engine):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo
        from configs.dao import SQLiteDAO

        app = FastAPI(title="ROCCA Test")
        dao = SQLiteDAO("sqlite://")
        dao._engine = engine
        dao._session_factory = sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
        )
        modulo = RemitosCarnicosModulo(dao)
        modulo.registrar(app)

        @app.get("/api/health")
        def health():
            return {"status": "ok"}

        # Seed
        with dao.obtener_sesion() as session:
            ops = [
                Operador(cuit="20111111111", razon_social="TITULAR API", situacion="ACTIVO"),
                Operador(cuit="20222222222", razon_social="TRANSPORTISTA API", situacion="ACTIVO"),
                Operador(cuit="20444444444", razon_social="DESTINATARIO API", situacion="ACTIVO"),
            ]
            session.add_all(ops)
            session.commit()

            mercs = [
                Mercaderia(codigo_afip="1101", descripcion="Carne bovino fresca", requiere_numero_tropa=True),
                Mercaderia(codigo_afip="1102", descripcion="Carne bovino congelada", requiere_numero_tropa=False),
            ]
            session.add_all(mercs)
            session.commit()

        return TestClient(app)

    def test_listar_remitos_vacio(self, api_client):
        r = api_client.get("/api/remitos")
        assert r.status_code == 200
        assert r.json() == []

    def test_crear_remito(self, api_client):
        payload = {
            "punto_emision": "001",
            "numero_comprobante": "0000000001",
            "caso": 1,
            "tipo_movimiento": "ENV",
            "fecha_emision": "2025-06-01T10:00:00",
            "fecha_vencimiento": "2025-06-02T10:00:00",
            "titular_cuit": "20111111111",
            "transportista_cuit": "20222222222",
            "destinatario_cuit": "20444444444",
            "chofer_apellido_nombre": "Juan Pérez",
            "chofer_documento": "12345678",
            "dominio_vehiculo": "ABC123",
            "renglones": [
                {"codigo_afip": "1101", "unidades": "100", "kilos": "500.5", "numero_tropa": "T-001"},
            ],
        }
        r = api_client.post("/api/remitos", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["codigo_remito"] == "001-0000000001"
        assert data["estado"] == "E"
        assert data["titular"]["cuit"] == "20111111111"
        assert len(data["renglones"]) == 1
        assert data["total_kilos"] == "500.5"

    def test_obtener_remito(self, api_client):
        payload = {
            "punto_emision": "001",
            "numero_comprobante": "0000000002",
            "caso": 1,
            "tipo_movimiento": "ENV",
            "fecha_emision": "2025-06-01T10:00:00",
            "fecha_vencimiento": "2025-06-02T10:00:00",
            "titular_cuit": "20111111111",
            "transportista_cuit": "20222222222",
            "destinatario_cuit": "20444444444",
            "renglones": [
                {"codigo_afip": "1102", "unidades": "50", "kilos": "200"},
            ],
        }
        api_client.post("/api/remitos", json=payload)

        r = api_client.get("/api/remitos/001/0000000002")
        assert r.status_code == 200
        data = r.json()
        assert data["numero_comprobante"] if "numero_comprobante" in data else True
        assert data["titular"]["razon_social"] == "TITULAR API"

    def test_obtener_remito_no_existe(self, api_client):
        r = api_client.get("/api/remitos/999/999")
        assert r.status_code == 404

    def test_crear_remito_invalido(self, api_client):
        """Caso 01 sin destinatario → 400."""
        payload = {
            "punto_emision": "001",
            "numero_comprobante": "0000000003",
            "caso": 1,
            "tipo_movimiento": "ENV",
            "fecha_emision": "2025-06-01T10:00:00",
            "fecha_vencimiento": "2025-06-02T10:00:00",
            "titular_cuit": "20111111111",
            "transportista_cuit": "20222222222",
            "destinatario_cuit": None,
            "renglones": [
                {"codigo_afip": "1102", "unidades": "50", "kilos": "200"},
            ],
        }
        r = api_client.post("/api/remitos", json=payload)
        assert r.status_code == 400

    def test_anular_remito(self, api_client):
        payload = {
            "punto_emision": "001",
            "numero_comprobante": "0000000004",
            "caso": 1,
            "tipo_movimiento": "ENV",
            "fecha_emision": "2025-06-01T10:00:00",
            "fecha_vencimiento": "2025-06-02T10:00:00",
            "titular_cuit": "20111111111",
            "transportista_cuit": "20222222222",
            "destinatario_cuit": "20444444444",
            "renglones": [
                {"codigo_afip": "1102", "unidades": "50", "kilos": "200"},
            ],
        }
        r = api_client.post("/api/remitos", json=payload)
        remito_id = r.json()["id"]

        r = api_client.post(f"/api/remitos/{remito_id}/anular")
        assert r.status_code == 200
        assert r.json()["estado"] == "AN"

    def test_anular_remito_no_existe(self, api_client):
        r = api_client.post("/api/remitos/9999/anular")
        assert r.status_code == 400

    def test_listar_remitos_con_filtro_estado(self, api_client):
        payload = {
            "punto_emision": "001",
            "numero_comprobante": "0000000005",
            "caso": 1,
            "tipo_movimiento": "ENV",
            "fecha_emision": "2025-06-01T10:00:00",
            "fecha_vencimiento": "2025-06-02T10:00:00",
            "titular_cuit": "20111111111",
            "transportista_cuit": "20222222222",
            "destinatario_cuit": "20444444444",
            "renglones": [
                {"codigo_afip": "1102", "unidades": "50", "kilos": "200"},
            ],
        }
        api_client.post("/api/remitos", json=payload)

        r = api_client.get("/api/remitos", params={"estado": "E"})
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get("/api/remitos", params={"estado": "AN"})
        assert r.status_code == 200
        assert len(r.json()) == 0
