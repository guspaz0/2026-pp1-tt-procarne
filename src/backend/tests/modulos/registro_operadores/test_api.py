"""Tests de la API REST del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.modulos.registro_operadores.test_operador import crear_rocca_operador_test


@pytest.fixture()
def api_client(db_engine):
    """Cliente HTTP con la BD en memoria y seed mínimo."""
    from fastapi import FastAPI
    from configs.dao import SQLiteDAO
    from modulos.registro_operadores.registro_operadores import RegistroOperadoresModulo
    from sqlalchemy.orm import sessionmaker

    app = FastAPI(title="ROCCA Test")

    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )

    modulo = RegistroOperadoresModulo(dao)
    modulo.registrar(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # Seed mínimo
    with dao.obtener_sesion() as session:
        crear_rocca_operador_test(
            session, "30111111111", "FRIGORIFICO TEST S.A.", tipo="FRIGORIFICO"
        )

    return TestClient(app)


class TestAPIRegistroOperadores:
    """Tests de los endpoints /api/registro-operadores."""

    def test_health(self, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_listar(self, api_client):
        r = api_client.get("/api/registro-operadores")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["cuit"] == "30111111111"

    def test_listar_filtrar_por_tipo(self, api_client):
        r = api_client.get(
            "/api/registro-operadores", params={"tipo": "FRIGORIFICO"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get(
            "/api/registro-operadores", params={"tipo": "CARNICERIA"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_listar_filtrar_por_estado(self, api_client):
        r = api_client.get(
            "/api/registro-operadores", params={"estado_registral": "ACTIVO"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get(
            "/api/registro-operadores", params={"estado_registral": "BAJADO"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_obtener_por_cuit(self, api_client):
        r = api_client.get("/api/registro-operadores/30111111111")
        assert r.status_code == 200
        data = r.json()
        assert data["cuit"] == "30111111111"
        assert data["razon_social"] == "FRIGORIFICO TEST S.A."
        assert data["tipo"] == "FRIGORIFICO"
        assert data["estado_registral"] == "ACTIVO"

    def test_obtener_no_existe(self, api_client):
        r = api_client.get("/api/registro-operadores/99999999999")
        assert r.status_code == 404

    def test_registrar(self, api_client):
        payload = {
            "cuit": "30222222222",
            "razon_social": "CARNICERIA EL ESTERO",
            "tipo": "CARNICERIA",
            "domicilio": "Av. Rivadavia 500",
            "telefono": "385-4444444",
            "email": "carniceria@ester.com",
            "habilitaciones": [
                {
                    "tipo": "Sanitaria",
                    "numero": "HAB-100",
                    "autoridad": "ProCarne Fiscalización",
                    "fecha_emision": "2026-01-10",
                    "estado": "VIGENTE",
                }
            ],
            "inscripciones": [
                {
                    "tipo": "NACIONAL",
                    "organismo": "RFOCB",
                    "numero": "RFOCB-999",
                    "fecha_inscripcion": "2025-11-20",
                    "estado": "ACTIVA",
                }
            ],
            "domicilios": [
                {
                    "tipo": "PRINCIPAL",
                    "calle": "Av. Rivadavia",
                    "numero": "500",
                    "localidad": "Santiago del Estero",
                    "departamento": "Capital",
                    "provincia": "Santiago del Estero",
                }
            ],
        }
        r = api_client.post("/api/registro-operadores", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["cuit"] == "30222222222"
        assert data["tipo"] == "CARNICERIA"
        assert len(data["habilitaciones"]) == 1
        assert len(data["inscripciones"]) == 1
        assert len(data["domicilios"]) == 1
        assert data["domicilios"][0]["localidad"] == "Santiago del Estero"

    def test_registrar_duplicado(self, api_client):
        payload = {
            "cuit": "30111111111",
            "razon_social": "FRIGORIFICO TEST S.A.",
            "tipo": "FRIGORIFICO",
        }
        r = api_client.post("/api/registro-operadores", json=payload)
        assert r.status_code == 409

    def test_registrar_cuit_invalido(self, api_client):
        payload = {
            "cuit": "123",
            "razon_social": "INVALIDO",
            "tipo": "FRIGORIFICO",
        }
        r = api_client.post("/api/registro-operadores", json=payload)
        assert r.status_code == 422

    def test_cambiar_estado(self, api_client):
        r = api_client.patch(
            "/api/registro-operadores/30111111111/estado",
            json={"estado_registral": "SUSPENDIDO"},
        )
        assert r.status_code == 200
        assert r.json()["estado_registral"] == "SUSPENDIDO"

    def test_cambiar_estado_no_existe(self, api_client):
        r = api_client.patch(
            "/api/registro-operadores/99999999999/estado",
            json={"estado_registral": "BAJADO"},
        )
        assert r.status_code == 404
