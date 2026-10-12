"""Tests de la API REST del Módulo II — Trazabilidad Comercial."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from tests.modulos.trazabilidad_comercial.test_trazabilidad import (
    crear_registro_trazabilidad_test,
)


@pytest.fixture()
def api_client(db_engine):
    """Cliente HTTP con la BD en memoria y seed mínimo."""
    from fastapi import FastAPI
    from configs.dao import SQLiteDAO
    from modulos.trazabilidad_comercial.trazabilidad_comercial import (
        TrazabilidadComercialModulo,
    )

    app = FastAPI(title="Trazabilidad Test")

    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )

    modulo = TrazabilidadComercialModulo(dao)
    modulo.registrar(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # Seed mínimo
    with dao.obtener_sesion() as session:
        crear_registro_trazabilidad_test(
            session,
            tipo_ingreso="INGRESO_EXTRAPROVINCIAL",
            especie="BOVINO",
            cantidad_kg=500.0,
            origen_provincia="Córdoba",
            numero_dte="DTE-001",
            numero_remito="REC-001",
            destino_cuit="30111111111",
        )

    return TestClient(app)


class TestAPITrazabilidad:
    """Tests de los endpoints /api/trazabilidad."""

    def test_health(self, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_listar(self, api_client):
        r = api_client.get("/api/trazabilidad")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["numero_dte"] == "DTE-001"

    def test_listar_filtrar_por_tipo_ingreso(self, api_client):
        r = api_client.get(
            "/api/trazabilidad", params={"tipo_ingreso": "INGRESO_EXTRAPROVINCIAL"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get(
            "/api/trazabilidad", params={"tipo_ingreso": "FAENA_PROVINCIAL"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_listar_filtrar_por_especie(self, api_client):
        r = api_client.get("/api/trazabilidad", params={"especie": "BOVINO"})
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get("/api/trazabilidad", params={"especie": "OVINO"})
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_listar_filtrar_por_estado(self, api_client):
        r = api_client.get("/api/trazabilidad", params={"estado": "REGISTRADO"})
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get("/api/trazabilidad", params={"estado": "VALIDADO"})
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_listar_filtrar_por_origen(self, api_client):
        r = api_client.get(
            "/api/trazabilidad", params={"origen_provincia": "Córdoba"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get(
            "/api/trazabilidad", params={"origen_provincia": "Buenos Aires"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_listar_filtrar_por_destino_cuit(self, api_client):
        r = api_client.get(
            "/api/trazabilidad", params={"destino_cuit": "30111111111"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_obtener_por_id(self, api_client):
        r = api_client.get("/api/trazabilidad/1")
        assert r.status_code == 200
        data = r.json()
        assert data["numero_dte"] == "DTE-001"
        assert data["cantidad_kg"] == 500.0
        assert data["especie"] == "BOVINO"
        assert data["origen_provincia"] == "Córdoba"

    def test_obtener_no_existe(self, api_client):
        r = api_client.get("/api/trazabilidad/9999")
        assert r.status_code == 404

    def test_registrar(self, api_client):
        payload = {
            "tipo_ingreso": "FAENA_PROVINCIAL",
            "cantidad_kg": 150.0,
            "especie": "OVINO",
            "establecimiento_faena": "MATADERO LA BANDA",
            "numero_dte": "DTE-100",
            "numero_remito": "REC-100",
            "destino_tipo": "CARNICERIA",
            "destino_cuit": "30555555555",
            "destino_razon_social": "CARNICERIA CENTRAL",
        }
        r = api_client.post("/api/trazabilidad", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["tipo_ingreso"] == "FAENA_PROVINCIAL"
        assert data["cantidad_kg"] == 150.0
        assert data["especie"] == "OVINO"
        assert data["estado"] == "REGISTRADO"
        assert data["destino_cuit"] == "30555555555"

    def test_registrar_duplicado_dte(self, api_client):
        payload = {
            "tipo_ingreso": "INGRESO_EXTRAPROVINCIAL",
            "cantidad_kg": 100.0,
            "especie": "BOVINO",
            "origen_provincia": "Córdoba",
            "numero_dte": "DTE-001",
        }
        r = api_client.post("/api/trazabilidad", json=payload)
        assert r.status_code == 409

    def test_registrar_duplicado_remito(self, api_client):
        payload = {
            "tipo_ingreso": "INGRESO_EXTRAPROVINCIAL",
            "cantidad_kg": 100.0,
            "especie": "OVINO",
            "origen_provincia": "Salta",
            "numero_remito": "REC-001",
        }
        r = api_client.post("/api/trazabilidad", json=payload)
        assert r.status_code == 409

    def test_registrar_cantidad_negativa(self, api_client):
        payload = {
            "tipo_ingreso": "FAENA_PROVINCIAL",
            "cantidad_kg": -50.0,
            "especie": "BOVINO",
        }
        r = api_client.post("/api/trazabilidad", json=payload)
        assert r.status_code == 422

    def test_registrar_extraprovincial_sin_origen(self, api_client):
        payload = {
            "tipo_ingreso": "INGRESO_EXTRAPROVINCIAL",
            "cantidad_kg": 100.0,
            "especie": "BOVINO",
        }
        r = api_client.post("/api/trazabilidad", json=payload)
        assert r.status_code == 422

    def test_validar(self, api_client):
        r = api_client.patch("/api/trazabilidad/1/validar")
        assert r.status_code == 200
        assert r.json()["estado"] == "VALIDADO"

    def test_validar_ya_validado(self, api_client):
        # Primero validar
        api_client.patch("/api/trazabilidad/1/validar")
        # Intentar validar de nuevo
        r = api_client.patch("/api/trazabilidad/1/validar")
        assert r.status_code == 400

    def test_rechazar(self, api_client):
        r = api_client.patch(
            "/api/trazabilidad/1/rechazar",
            json={"motivo": "Documentación incompleta"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["estado"] == "RECHAZADO"
        assert "Documentación incompleta" in data["observaciones"]

    def test_rechazar_no_existe(self, api_client):
        r = api_client.patch(
            "/api/trazabilidad/9999/rechazar",
            json={"motivo": "No existe"},
        )
        assert r.status_code == 400

    def test_eliminar(self, api_client):
        r = api_client.delete("/api/trazabilidad/1")
        assert r.status_code == 204
        r = api_client.get("/api/trazabilidad/1")
        assert r.status_code == 404

    def test_eliminar_no_existe(self, api_client):
        r = api_client.delete("/api/trazabilidad/9999")
        assert r.status_code == 404
