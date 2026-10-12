"""Tests de la API REST de operadores."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from modulos.remitos_carnicos.operador.dao import Operador, operador_actividades
from modulos.remitos_carnicos.operador.categoria import Actividad, CategoriaOperador


@pytest.fixture()
def api_client(db_engine):
    """Cliente HTTP con la BD en memoria y seed mínimo."""
    from fastapi import FastAPI
    from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo
    from configs.dao import SQLiteDAO
    from sqlalchemy.orm import sessionmaker

    app = FastAPI(title="ROCCA Test")

    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )

    modulo = RemitosCarnicosModulo(dao)
    modulo.registrar(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    # Seed mínimo
    from tests.modulos.remitos_carnicos.conftest import crear_operador_test

    with dao.obtener_sesion() as session:
        bov = Actividad(id=1, nombre="Bovino/Bubalino")
        por = Actividad(id=2, nombre="Porcino")
        session.add_all([bov, por])
        session.commit()

        op = crear_operador_test(session, "20123456789", "API TEST S.A.")

        session.execute(
            insert(operador_actividades).values(operador_id=op.id, actividad_id=1)
        )
        cat = CategoriaOperador(
            operador_id=op.id,
            actividad_id=1,
            categoria="Productor/criador",
            situacion="ACTIVO",
            desde_fecha="01/01/2024",
        )
        session.add(cat)
        session.commit()

    return TestClient(app)


class TestAPIOperadores:
    """Tests de los endpoints /api/operadores."""

    def test_health(self, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_listar_operadores(self, api_client):
        r = api_client.get("/api/operadores")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["cuit"] == "20123456789"

    def test_listar_operadores_con_filtros(self, api_client):
        r = api_client.get("/api/operadores", params={"limite": 10, "offset": 0})
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_obtener_operador(self, api_client):
        r = api_client.get("/api/operadores/20123456789")
        assert r.status_code == 200
        data = r.json()
        assert data["cuit"] == "20123456789"
        assert data["razon_social"] == "API TEST S.A."
        assert len(data["actividades"]) == 1

    def test_obtener_operador_no_existe(self, api_client):
        r = api_client.get("/api/operadores/99999999999")
        assert r.status_code == 404

    def test_crear_operador(self, api_client):
        r = api_client.post(
            "/api/operadores",
            json={
                "cuit": "30333333333",
                "razon_social": "NUEVO OPERADOR S.A.",
                "situacion": "ACTIVO",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["cuit"] == "30333333333"
        assert data["razon_social"] == "NUEVO OPERADOR S.A."

    def test_crear_operador_duplicado(self, api_client):
        r = api_client.post(
            "/api/operadores",
            json={"cuit": "20123456789", "razon_social": "DUPLICADO"},
        )
        assert r.status_code == 409

    def test_operador_incluye_actividades(self, api_client):
        r = api_client.get("/api/operadores/20123456789")
        data = r.json()
        assert "actividades" in data
        act = data["actividades"][0]
        assert act["nombre"] == "Bovino/Bubalino"
        assert len(act["categorias"]) == 1
        assert act["categorias"][0]["categoria"] == "Productor/criador"
