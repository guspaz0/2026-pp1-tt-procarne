"""Tests de la API REST del Módulo III — Fiscalización."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from tests.modulos.fiscalizacion.test_fiscalizacion import (
    crear_inspeccion_test,
    crear_inspeccion_con_infraccion_test,
)


@pytest.fixture()
def api_client(db_engine):
    """Cliente HTTP con la BD en memoria y seed mínimo."""
    from fastapi import FastAPI
    from configs.dao import SQLiteDAO
    from modulos.fiscalizacion.fiscalizacion import FiscalizacionModulo

    app = FastAPI(title="Fiscalización Test")

    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )

    modulo = FiscalizacionModulo(dao)
    modulo.registrar(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # Seed mínimo
    with dao.obtener_sesion() as session:
        crear_inspeccion_test(
            session,
            inspector="Inspector A",
            operador_cuit="30111111111",
            resultado="CONFORME",
        )
        crear_inspeccion_con_infraccion_test(
            session,
            inspector="Inspector B",
            operador_cuit="30222222222",
            resultado="NO_CONFORME",
        )

    return TestClient(app)


class TestAPIFiscalizacion:
    """Tests de los endpoints /api/fiscalizacion."""

    def test_health(self, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_listar_inspecciones(self, api_client):
        r = api_client.get("/api/fiscalizacion/inspecciones")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2

    def test_listar_inspecciones_filtrar_por_operador(self, api_client):
        r = api_client.get(
            "/api/fiscalizacion/inspecciones",
            params={"operador_cuit": "30222222222"},
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["inspector"] == "Inspector B"

    def test_listar_inspecciones_filtrar_por_resultado(self, api_client):
        r = api_client.get(
            "/api/fiscalizacion/inspecciones",
            params={"resultado": "NO_CONFORME"},
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["operador_cuit"] == "30222222222"

    def test_obtener_inspeccion(self, api_client):
        r = api_client.get("/api/fiscalizacion/inspecciones/1")
        assert r.status_code == 200
        data = r.json()
        assert data["inspector"] == "Inspector A"
        assert data["resultado"] == "CONFORME"

    def test_obtener_inspeccion_no_existe(self, api_client):
        r = api_client.get("/api/fiscalizacion/inspecciones/9999")
        assert r.status_code == 404

    def test_registrar_inspeccion_conforme(self, api_client):
        payload = {
            "inspector": "Inspector C",
            "operador_cuit": "30333333333",
            "tipo": "RUTINA",
            "resultado": "CONFORME",
            "latitud": -27.81,
            "longitud": -64.29,
        }
        r = api_client.post("/api/fiscalizacion/inspecciones", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["inspector"] == "Inspector C"
        assert data["resultado"] == "CONFORME"

    def test_registrar_inspeccion_con_infraccion(self, api_client):
        payload = {
            "inspector": "Inspector D",
            "operador_cuit": "30444444444",
            "tipo": "PROGRAMADA",
            "resultado": "NO_CONFORME",
            "infracciones": [
                {
                    "tipo": "HIGIENE",
                    "gravedad": "GRAVE",
                    "descripcion": "Deficiencia de higiene",
                    "sanciones": [
                        {
                            "tipo": "MULTA",
                            "monto": 50000.0,
                            "descripcion": "Multa por higiene",
                        }
                    ],
                }
            ],
        }
        r = api_client.post("/api/fiscalizacion/inspecciones", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["resultado"] == "NO_CONFORME"
        assert len(data["infracciones"]) == 1
        assert data["infracciones"][0]["tipo"] == "HIGIENE"
        assert len(data["infracciones"][0]["sanciones"]) == 1
        assert data["infracciones"][0]["sanciones"][0]["monto"] == 50000.0

    def test_registrar_inspeccion_no_conforme_sin_infracciones(self, api_client):
        payload = {
            "inspector": "Inspector E",
            "operador_cuit": "30555555555",
            "resultado": "NO_CONFORME",
        }
        r = api_client.post("/api/fiscalizacion/inspecciones", json=payload)
        assert r.status_code == 422

    def test_registrar_inspeccion_cuit_invalido(self, api_client):
        payload = {
            "inspector": "Inspector F",
            "operador_cuit": "123",
        }
        r = api_client.post("/api/fiscalizacion/inspecciones", json=payload)
        assert r.status_code == 422

    def test_marcar_enviada(self, api_client):
        r = api_client.patch("/api/fiscalizacion/inspecciones/1/enviar")
        assert r.status_code == 200
        assert r.json()["enviada"] is True

    def test_eliminar_inspeccion(self, api_client):
        r = api_client.delete("/api/fiscalizacion/inspecciones/1")
        assert r.status_code == 204
        r = api_client.get("/api/fiscalizacion/inspecciones/1")
        assert r.status_code == 404

    def test_listar_infracciones(self, api_client):
        r = api_client.get("/api/fiscalizacion/infracciones")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["tipo"] == "DOCUMENTACION"

    def test_listar_infracciones_filtrar_por_gravedad(self, api_client):
        r = api_client.get(
            "/api/fiscalizacion/infracciones",
            params={"gravedad": "GRAVE"},
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get(
            "/api/fiscalizacion/infracciones",
            params={"gravedad": "LEVE"},
        )
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_listar_reincidencias(self, api_client):
        # Registrar una reincidencia primero
        api_client.post(
            "/api/fiscalizacion/reincidencias",
            json={"operador_cuit": "30888888888", "observaciones": "Test"},
        )
        r = api_client.get("/api/fiscalizacion/reincidencias")
        assert r.status_code == 200
        data = r.json()
        assert len(data) >= 1
        assert data[0]["operador_cuit"] == "30888888888"

    def test_registrar_reincidencia(self, api_client):
        payload = {
            "operador_cuit": "30666666666",
            "observaciones": "Infracción de transporte",
        }
        r = api_client.post("/api/fiscalizacion/reincidencias", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["operador_cuit"] == "30666666666"
        assert data["cantidad"] == 1

    def test_obtener_reincidencia(self, api_client):
        # Registrar primero
        api_client.post(
            "/api/fiscalizacion/reincidencias",
            json={"operador_cuit": "30777777777", "observaciones": "Test"},
        )
        r = api_client.get("/api/fiscalizacion/reincidencias/30777777777")
        assert r.status_code == 200
        assert r.json()["cantidad"] == 1

    def test_obtener_reincidencia_no_existe(self, api_client):
        r = api_client.get("/api/fiscalizacion/reincidencias/30999999999")
        assert r.status_code == 404
