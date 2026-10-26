"""Tests de la API REST del Módulo III — Fiscalización."""

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
    from modulos.fiscalizacion.fiscalizacion import FiscalizacionModulo
    from sqlalchemy.orm import sessionmaker

    app = FastAPI(title="ROCCA Test")

    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine
    )

    modulo = FiscalizacionModulo(dao)
    modulo.registrar(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return TestClient(app)


def _datos_inspeccion_api(**overrides):
    base = {
        "tipo": "PROGRAMADA",
        "operador_cuit": "30111111111",
        "fecha": "2025-06-01T10:00:00",
        "inspector": "Juan Pérez",
    }
    base.update(overrides)
    return base


def _datos_acta_api(inspeccion_id: int, **overrides):
    base = {
        "inspeccion_id": inspeccion_id,
        "tipo": "INSPECCION",
        "numero": "ACT-001",
        "fecha": "2025-06-01T11:00:00",
        "contenido": "Inspección realizada sin observaciones.",
    }
    base.update(overrides)
    return base


def _datos_infraccion_api(inspeccion_id: int, **overrides):
    base = {
        "inspeccion_id": inspeccion_id,
        "operador_cuit": "30111111111",
        "tipo": "INCUMPLIMIENTO_NORMAS",
        "gravedad": "GRAVE",
        "descripcion": "Falta de trazabilidad.",
    }
    base.update(overrides)
    return base


def _datos_sancion_api(infraccion_id: int, **overrides):
    base = {
        "infraccion_id": infraccion_id,
        "operador_cuit": "30111111111",
        "tipo": "MULTA",
        "monto": "50000.00",
    }
    base.update(overrides)
    return base


def _datos_decomiso_api(inspeccion_id: int, **overrides):
    base = {
        "inspeccion_id": inspeccion_id,
        "mercaderia": "Carne bovina",
        "cantidad": "100",
        "peso_kg": "500.5",
        "motivo": "Mala conservación",
    }
    base.update(overrides)
    return base


class TestAPIFiscalizacion:
    """Tests de los endpoints /api/fiscalizacion."""

    def test_health(self, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    # ------------------------------------------------------------------
    # Inspecciones
    # ------------------------------------------------------------------

    def test_listar_inspecciones_vacio(self, api_client):
        r = api_client.get("/api/fiscalizacion/inspecciones")
        assert r.status_code == 200
        assert r.json() == []

    def test_registrar_inspeccion(self, api_client):
        data = _datos_inspeccion_api()
        r = api_client.post("/api/fiscalizacion/inspecciones", json=data)
        assert r.status_code == 201
        body = r.json()
        assert body["tipo"] == "PROGRAMADA"
        assert body["operador_cuit"] == "30111111111"
        assert body["inspector"] == "Juan Pérez"

    def test_listar_inspecciones_despues_de_registrar(self, api_client):
        data = _datos_inspeccion_api()
        api_client.post("/api/fiscalizacion/inspecciones", json=data)

        r = api_client.get("/api/fiscalizacion/inspecciones")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_listar_inspecciones_filtrar_por_operador(self, api_client):
        data1 = _datos_inspeccion_api(operador_cuit="30111111111")
        data2 = _datos_inspeccion_api(operador_cuit="30222222222")
        api_client.post("/api/fiscalizacion/inspecciones", json=data1)
        api_client.post("/api/fiscalizacion/inspecciones", json=data2)

        r = api_client.get(
            "/api/fiscalizacion/inspecciones",
            params={"operador_cuit": "30111111111"},
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_obtener_inspeccion(self, api_client):
        data = _datos_inspeccion_api()
        r_registrar = api_client.post("/api/fiscalizacion/inspecciones", json=data)
        inspeccion_id = r_registrar.json()["id"]

        r = api_client.get(f"/api/fiscalizacion/inspecciones/{inspeccion_id}")
        assert r.status_code == 200
        assert r.json()["id"] == inspeccion_id

    def test_obtener_inspeccion_no_existente(self, api_client):
        r = api_client.get("/api/fiscalizacion/inspecciones/999")
        assert r.status_code == 404

    # ------------------------------------------------------------------
    # Actas
    # ------------------------------------------------------------------

    def test_crear_acta(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data_acta = _datos_acta_api(inspeccion_id)
        r = api_client.post("/api/fiscalizacion/actas", json=data_acta)
        assert r.status_code == 201
        body = r.json()
        assert body["tipo"] == "INSPECCION"
        assert body["numero"] == "ACT-001"
        assert body["estado"] == "BORRADOR"

    def test_firmar_acta(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data_acta = _datos_acta_api(inspeccion_id)
        r_acta = api_client.post("/api/fiscalizacion/actas", json=data_acta)
        acta_id = r_acta.json()["id"]

        r = api_client.post(
            f"/api/fiscalizacion/actas/{acta_id}/firmar",
            params={"firmado_por": "Juan Pérez"},
        )
        assert r.status_code == 200
        assert r.json()["estado"] == "FIRMADA"
        assert r.json()["firmado_por"] == "Juan Pérez"

    def test_firmar_acta_no_existente(self, api_client):
        r = api_client.post(
            "/api/fiscalizacion/actas/999/firmar",
            params={"firmado_por": "Juan Pérez"},
        )
        assert r.status_code == 404

    def test_listar_actas(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        for i in range(3):
            data_acta = _datos_acta_api(inspeccion_id, numero=f"ACT-00{i+1}")
            api_client.post("/api/fiscalizacion/actas", json=data_acta)

        r = api_client.get(
            "/api/fiscalizacion/actas",
            params={"inspeccion_id": inspeccion_id},
        )
        assert r.status_code == 200
        assert len(r.json()) == 3

    # ------------------------------------------------------------------
    # Infracciones
    # ------------------------------------------------------------------

    def test_registrar_infraccion(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data_infraccion = _datos_infraccion_api(inspeccion_id)
        r = api_client.post("/api/fiscalizacion/infracciones", json=data_infraccion)
        assert r.status_code == 201
        body = r.json()
        assert body["tipo"] == "INCUMPLIMIENTO_NORMAS"
        assert body["gravedad"] == "GRAVE"

    def test_listar_infracciones(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        for i in range(3):
            data_infraccion = _datos_infraccion_api(inspeccion_id, operador_cuit=f"3011111111{i}")
            api_client.post("/api/fiscalizacion/infracciones", json=data_infraccion)

        r = api_client.get("/api/fiscalizacion/infracciones")
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_listar_infracciones_filtrar_por_operador(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data1 = _datos_infraccion_api(inspeccion_id, operador_cuit="30111111111")
        data2 = _datos_infraccion_api(inspeccion_id, operador_cuit="30222222222")
        api_client.post("/api/fiscalizacion/infracciones", json=data1)
        api_client.post("/api/fiscalizacion/infracciones", json=data2)

        r = api_client.get(
            "/api/fiscalizacion/infracciones",
            params={"operador_cuit": "30111111111"},
        )
        assert r.status_code == 200
        assert len(r.json()) == 1

    # ------------------------------------------------------------------
    # Sanciones
    # ------------------------------------------------------------------

    def test_aplicar_sancion(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data_infraccion = _datos_infraccion_api(inspeccion_id)
        r_infraccion = api_client.post("/api/fiscalizacion/infracciones", json=data_infraccion)
        infraccion_id = r_infraccion.json()["id"]

        data_sancion = _datos_sancion_api(infraccion_id)
        r = api_client.post("/api/fiscalizacion/sanciones", json=data_sancion)
        assert r.status_code == 201
        body = r.json()
        assert body["tipo"] == "MULTA"
        assert body["monto"] == "50000.00"
        assert body["estado"] == "PENDIENTE"

    def test_notificar_sancion(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data_infraccion = _datos_infraccion_api(inspeccion_id)
        r_infraccion = api_client.post("/api/fiscalizacion/infracciones", json=data_infraccion)
        infraccion_id = r_infraccion.json()["id"]

        data_sancion = _datos_sancion_api(infraccion_id)
        r_sancion = api_client.post("/api/fiscalizacion/sanciones", json=data_sancion)
        sancion_id = r_sancion.json()["id"]

        r = api_client.post(f"/api/fiscalizacion/sanciones/{sancion_id}/notificar")
        assert r.status_code == 200
        assert r.json()["estado"] == "NOTIFICADA"

    def test_notificar_sancion_no_existente(self, api_client):
        r = api_client.post("/api/fiscalizacion/sanciones/999/notificar")
        assert r.status_code == 404

    def test_listar_sanciones(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        for i in range(3):
            data_infraccion = _datos_infraccion_api(inspeccion_id, operador_cuit=f"3011111111{i}")
            r_infraccion = api_client.post("/api/fiscalizacion/infracciones", json=data_infraccion)
            infraccion_id = r_infraccion.json()["id"]
            data_sancion = _datos_sancion_api(infraccion_id, operador_cuit=f"3011111111{i}")
            api_client.post("/api/fiscalizacion/sanciones", json=data_sancion)

        r = api_client.get("/api/fiscalizacion/sanciones")
        assert r.status_code == 200
        assert len(r.json()) == 3

    # ------------------------------------------------------------------
    # Decomisos
    # ------------------------------------------------------------------

    def test_registrar_decomiso(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data_decomiso = _datos_decomiso_api(inspeccion_id)
        r = api_client.post("/api/fiscalizacion/decomisos", json=data_decomiso)
        assert r.status_code == 201
        body = r.json()
        assert body["mercaderia"] == "Carne bovina"
        assert float(body["cantidad"]) == 100.0
        assert float(body["peso_kg"]) == 500.5

    # ------------------------------------------------------------------
    # Reincidencias
    # ------------------------------------------------------------------

    def test_obtener_reincidencia(self, api_client):
        data_inspeccion = _datos_inspeccion_api()
        r_inspeccion = api_client.post("/api/fiscalizacion/inspecciones", json=data_inspeccion)
        inspeccion_id = r_inspeccion.json()["id"]

        data_infraccion = _datos_infraccion_api(inspeccion_id, operador_cuit="30111111111")
        api_client.post("/api/fiscalizacion/infracciones", json=data_infraccion)

        r = api_client.get("/api/fiscalizacion/reincidencias/30111111111")
        assert r.status_code == 200
        assert r.json()["cantidad_infracciones"] == 1

    def test_obtener_reincidencia_no_existente(self, api_client):
        r = api_client.get("/api/fiscalizacion/reincidencias/30999999999")
        assert r.status_code == 404
