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
        autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine
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
            "/api/registro-operadores", params={"estado_registral": "PENDIENTE"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = api_client.get(
            "/api/registro-operadores", params={"estado_registral": "BAJADO"}
        )
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_crear_operador(self, api_client):
        data = {
            "cuit": "30222222222",
            "razon_social": "CARNICERIA NUEVA",
            "tipo": "CARNICERIA",
        }
        r = api_client.post("/api/registro-operadores", json=data)
        assert r.status_code == 201
        body = r.json()
        assert body["cuit"] == "30222222222"
        assert body["estado_registral"] == "PENDIENTE"

    def test_crear_operador_misma_persona(self, api_client):
        """Crear otro operador con el mismo CUIT es válido (misma persona, otra sucursal)."""
        data = {
            "cuit": "30111111111",
            "razon_social": "SUCURSAL 2",
            "tipo": "FRIGORIFICO",
        }
        r = api_client.post("/api/registro-operadores", json=data)
        assert r.status_code == 201

    def test_obtener_operador(self, api_client):
        r = api_client.get("/api/registro-operadores/1")
        assert r.status_code == 200
        assert r.json()["cuit"] == "30111111111"

    def test_obtener_operador_no_existente(self, api_client):
        r = api_client.get("/api/registro-operadores/999")
        assert r.status_code == 404

    def test_cambiar_estado(self, api_client):
        r = api_client.patch(
            "/api/registro-operadores/1/estado",
            params={"estado": "SUSPENDIDO"},
        )
        assert r.status_code == 200
        assert r.json()["estado_registral"] == "SUSPENDIDO"

    def test_agregar_habilitacion(self, api_client):
        data = {"actividad": "FAENA BOVINA"}
        r = api_client.post("/api/registro-operadores/1/habilitaciones", json=data)
        assert r.status_code == 201
        assert r.json()["actividad"] == "FAENA BOVINA"

    def test_listar_habilitaciones(self, api_client):
        api_client.post(
            "/api/registro-operadores/1/habilitaciones",
            json={"actividad": "FAENA BOVINA"},
        )
        r = api_client.get("/api/registro-operadores/1/habilitaciones")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_agregar_inscripcion(self, api_client):
        data = {"tipo": "PRINCIPAL", "numero_inscripcion": "ROCCA-001"}
        r = api_client.post("/api/registro-operadores/1/inscripciones", json=data)
        assert r.status_code == 201
        assert r.json()["numero_inscripcion"] == "ROCCA-001"

    def test_agregar_domicilio_operativo(self, api_client):
        data = {
            "direccion": "Av. Siempreviva 742",
            "localidad": "Springfield",
            "provincia": "BA",
            "es_principal": True,
        }
        r = api_client.post("/api/registro-operadores/1/domicilios-operativos", json=data)
        assert r.status_code == 201
        assert r.json()["direccion"] == "Av. Siempreviva 742"
