"""Tests de la API REST del módulo de Remitos Electrónicos Cárnicos."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from tests.modulos.remitos_carnicos.conftest import crear_operador_test


@pytest.fixture()
def api_client(db_engine):
    """Cliente HTTP con la BD en memoria y seed mínimo."""
    from fastapi import FastAPI
    from configs.dao import SQLiteDAO
    from core.mercaderia.dao import MercaderiaDAO
    from core.mercaderia.servicio import MercaderiaService
    from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo
    from modulos.remitos_carnicos.operador.dao import RemitoOperadorDAO
    from modulos.remitos_carnicos.remito.dao import RemitoCarnicoDAO
    from modulos.remitos_carnicos.remito.servicio import RemitoCarnicoService
    from sqlalchemy.orm import sessionmaker

    app = FastAPI(title="ROCCA Test")

    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine
    )

    # Seed mínimo
    with dao.obtener_sesion() as session:
        crear_operador_test(session, "30111111111", "TITULAR S.A.")
        crear_operador_test(session, "30222222222", "TRANSPORTES XYZ")
        crear_operador_test(session, "30333333333", "DESTINATARIO S.R.L.")
        from core.mercaderia.dao import Mercaderia
        m1 = Mercaderia(
            codigo="1101",
            descripcion="Media res con hueso",
            requiere_trazabilidad=True,
            requiere_numero_tropa=True,
        )
        session.add(m1)
        session.commit()

    # Componer el módulo
    operador_dao = RemitoOperadorDAO(dao.obtener_sesion)
    mercaderia_dao = MercaderiaDAO(dao.obtener_sesion)
    remito_dao = RemitoCarnicoDAO(dao.obtener_sesion)
    remito_service = RemitoCarnicoService(remito_dao, operador_dao, mercaderia_dao)

    from modulos.remitos_carnicos.controlador import crear_router
    router = crear_router(remito_service)
    app.include_router(router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return TestClient(app)


def _datos_remito_api(**overrides):
    """Construye un dict de RemitoCarnicoIn válido para la API."""
    base = {
        "punto_emision": "0001",
        "numero_comprobante": "0000000001",
        "caso": "01",
        "tipo_movimiento": "ENVIO_NORMAL",
        "fecha_emision": "2025-06-01T10:00:00",
        "fecha_vencimiento": "2025-06-02T10:00:00",
        "titular_cuit": "30111111111",
        "transportista_cuit": "30222222222",
        "destinatario_cuit": "30333333333",
        "chofer_apellido_nombre": "Juan Pérez",
        "chofer_documento": "12345678",
        "dominio_vehiculo": "ABC123",
        "renglones": [
            {"codigo_afip": "1101", "unidades": "100", "kilos": "500.5", "numero_tropa": "T-001"},
        ],
    }
    base.update(overrides)
    return base


class TestAPIRemitosCarnicos:
    """Tests de los endpoints /api/remitos-carnicos."""

    def test_health(self, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_listar_vacio(self, api_client):
        r = api_client.get("/api/remitos-carnicos")
        assert r.status_code == 200
        assert r.json() == []

    def test_emitir_remito(self, api_client):
        data = _datos_remito_api()
        r = api_client.post("/api/remitos-carnicos", json=data)
        assert r.status_code == 201
        body = r.json()
        assert body["punto_emision"] == "0001"
        assert body["estado"] == "EMITIDO"
        assert len(body["renglones"]) == 1

    def test_emitir_remito_punto_emision_invalido(self, api_client):
        data = _datos_remito_api(punto_emision="12")
        r = api_client.post("/api/remitos-carnicos", json=data)
        assert r.status_code == 400

    def test_emitir_remito_sin_renglones(self, api_client):
        data = _datos_remito_api(renglones=[])
        r = api_client.post("/api/remitos-carnicos", json=data)
        assert r.status_code == 400

    def test_listar_despues_de_emitir(self, api_client):
        data = _datos_remito_api()
        api_client.post("/api/remitos-carnicos", json=data)

        r = api_client.get("/api/remitos-carnicos")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_obtener_remito(self, api_client):
        data = _datos_remito_api()
        r_emitir = api_client.post("/api/remitos-carnicos", json=data)
        remito_id = r_emitir.json()["id"]

        r = api_client.get(f"/api/remitos-carnicos/{remito_id}")
        assert r.status_code == 200
        assert r.json()["id"] == remito_id

    def test_obtener_remito_no_existente(self, api_client):
        r = api_client.get("/api/remitos-carnicos/999")
        assert r.status_code == 404

    def test_cambiar_estado(self, api_client):
        data = _datos_remito_api()
        r_emitir = api_client.post("/api/remitos-carnicos", json=data)
        remito_id = r_emitir.json()["id"]

        r = api_client.patch(
            f"/api/remitos-carnicos/{remito_id}/estado",
            params={"estado": "ENTREGADO"},
        )
        assert r.status_code == 200
        assert r.json()["estado"] == "ENTREGADO"
