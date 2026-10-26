"""Tests de la API REST del Módulo II — Trazabilidad Comercial."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def api_client(db_engine):
    """Cliente HTTP con la BD en memoria."""
    from fastapi import FastAPI
    from configs.dao import SQLiteDAO
    from modulos.trazabilidad_comercial.trazabilidad_comercial import TrazabilidadComercialModulo
    from sqlalchemy.orm import sessionmaker

    app = FastAPI(title="ROCCA Test")

    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine
    )

    modulo = TrazabilidadComercialModulo(dao)
    modulo.registrar(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return TestClient(app)


def _datos_ingreso_api(**overrides):
    """Construye un dict de RegistroTrazabilidadIn válido para la API."""
    base = {
        "tipo_ingreso": "COMPRA",
        "especie": "BOVINO",
        "cantidad": "10",
        "peso_kg": "500.5",
        "origen_cuit": "30111111111",
        "destino_cuit": "30222222222",
        "tipo_destino": "FRIGORIFICO",
        "fecha_ingreso": "2025-06-01T10:00:00",
        "numero_remito": "REM-001",
        "numero_dte": "DTE-001",
    }
    base.update(overrides)
    return base


class TestAPITrazabilidadComercial:
    """Tests de los endpoints /api/trazabilidad."""

    def test_health(self, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_listar_vacio(self, api_client):
        r = api_client.get("/api/trazabilidad")
        assert r.status_code == 200
        assert r.json() == []

    def test_registrar_ingreso(self, api_client):
        data = _datos_ingreso_api()
        r = api_client.post("/api/trazabilidad", json=data)
        assert r.status_code == 201
        body = r.json()
        assert body["estado"] == "PENDIENTE"
        assert body["origen_cuit"] == "30111111111"
        assert body["destino_cuit"] == "30222222222"

    def test_listar_despues_de_registrar(self, api_client):
        data = _datos_ingreso_api()
        api_client.post("/api/trazabilidad", json=data)

        r = api_client.get("/api/trazabilidad")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_listar_filtrar_por_estado(self, api_client):
        data1 = _datos_ingreso_api(numero_remito="REM-001")
        data2 = _datos_ingreso_api(numero_remito="REM-002")
        r1 = api_client.post("/api/trazabilidad", json=data1)
        r2 = api_client.post("/api/trazabilidad", json=data2)

        id1 = r1.json()["id"]
        api_client.post(f"/api/trazabilidad/{id1}/confirmar")

        r = api_client.get("/api/trazabilidad", params={"estado": "PENDIENTE"})
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get("/api/trazabilidad", params={"estado": "CONFIRMADO"})
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_listar_filtrar_por_especie(self, api_client):
        data1 = _datos_ingreso_api(especie="BOVINO", numero_remito="REM-001")
        data2 = _datos_ingreso_api(especie="PORCINO", numero_remito="REM-002")
        api_client.post("/api/trazabilidad", json=data1)
        api_client.post("/api/trazabilidad", json=data2)

        r = api_client.get("/api/trazabilidad", params={"especie": "BOVINO"})
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get("/api/trazabilidad", params={"especie": "PORCINO"})
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_obtener_registro(self, api_client):
        data = _datos_ingreso_api()
        r_registrar = api_client.post("/api/trazabilidad", json=data)
        registro_id = r_registrar.json()["id"]

        r = api_client.get(f"/api/trazabilidad/{registro_id}")
        assert r.status_code == 200
        assert r.json()["id"] == registro_id

    def test_obtener_registro_no_existente(self, api_client):
        r = api_client.get("/api/trazabilidad/999")
        assert r.status_code == 404

    def test_confirmar(self, api_client):
        data = _datos_ingreso_api()
        r_registrar = api_client.post("/api/trazabilidad", json=data)
        registro_id = r_registrar.json()["id"]

        r = api_client.post(f"/api/trazabilidad/{registro_id}/confirmar")
        assert r.status_code == 200
        assert r.json()["estado"] == "CONFIRMADO"

    def test_anular(self, api_client):
        data = _datos_ingreso_api()
        r_registrar = api_client.post("/api/trazabilidad", json=data)
        registro_id = r_registrar.json()["id"]

        r = api_client.post(f"/api/trazabilidad/{registro_id}/anular")
        assert r.status_code == 200
        assert r.json()["estado"] == "ANULADO"

    def test_confirmar_no_existente(self, api_client):
        r = api_client.post("/api/trazabilidad/999/confirmar")
        assert r.status_code == 404

    def test_anular_no_existente(self, api_client):
        r = api_client.post("/api/trazabilidad/999/anular")
        assert r.status_code == 404
