"""Tests de la API REST del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modulos.registro_operadores.controlador import crear_router
from modulos.registro_operadores.operador.dao import OperadorDAO
from modulos.registro_operadores.operador.servicio import OperadorService

from .conftest import crear_operador_test


@pytest.fixture()
def app(db_session_factory, persona_service):
    """Crea la aplicación FastAPI con el router del módulo."""
    from modulos.registro_operadores.actividad_economica.dao import CatalogoActividadesDAO
    from modulos.registro_operadores.certificado.dao import CertificadoDAO
    from modulos.registro_operadores.certificado.servicio import CertificadoService
    from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
    from modulos.registro_operadores.requisito_inscripcion.servicio import (
        RequisitoInscripcionService,
    )

    catalogo = CatalogoActividadesDAO(db_session_factory)
    requisito_service = RequisitoInscripcionService(RequisitoInscripcionDAO(db_session_factory))
    certificado_service = CertificadoService(CertificadoDAO(db_session_factory))
    operador_service = OperadorService(
        OperadorDAO(db_session_factory),
        persona_service=persona_service,
        requisito_service=requisito_service,
        certificado_service=certificado_service,
        catalogo_actividades_dao=catalogo,
    )
    router = crear_router(
        operador_service=operador_service,
        catalogo_actividades_dao=catalogo,
        certificado_service=certificado_service,
        requisito_service=requisito_service,
        adjunto_service=None,
    )
    application = FastAPI()
    application.include_router(router)
    return application


@pytest.fixture()
def client(app):
    """Cliente de test para la API."""
    return TestClient(app)


class TestAPIOperadores:
    """Tests de los endpoints de operadores."""

    def test_crear_operador(self, client):
        payload = {
            "cuit": "30111111111",
            "razon_social": "FRIGORIFICO TEST S.A.",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        }
        response = client.post("/api/registro-operadores", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["cuit"] == "30111111111"
        assert data["razon_social"] == "FRIGORIFICO TEST S.A."
        assert data["tipo"] == "FRIGORIFICO"
        assert data["categoria"] == "SALA_DE_DESPOSTE"
        assert data["estado_registral"] == "PENDIENTE"

    def test_crear_operador_misma_persona_distinto_operador(self, client):
        """Dos POST con el mismo CUIT → dos operadores distintos (misma persona)."""
        payload = {
            "cuit": "30111111111",
            "razon_social": "FRIGORIFICO TEST S.A.",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        }
        r1 = client.post("/api/registro-operadores", json=payload)
        r2 = client.post("/api/registro-operadores", json=payload)
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] != r2.json()["id"]

    def test_crear_operador_sin_cuit_ni_persona(self, client):
        payload = {
            "razon_social": "SIN TITULAR",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        }
        response = client.post("/api/registro-operadores", json=payload)
        assert response.status_code == 400
        assert "persona_id o cuit" in response.json()["detail"]

    def test_crear_operador_categoria_invalida(self, client):
        payload = {
            "cuit": "30555555555",
            "razon_social": "OPERADOR INVALIDO",
            "tipo": "FRIGORIFICO",
            "categoria": "CATEGORIA_INEXISTENTE",
        }
        response = client.post("/api/registro-operadores", json=payload)
        assert response.status_code == 400
        assert "Categoría inválida" in response.json()["detail"]

    def test_listar_operadores(self, client):
        payload = {
            "cuit": "30111111111",
            "razon_social": "FRIGORIFICO TEST S.A.",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        }
        client.post("/api/registro-operadores", json=payload)
        response = client.get("/api/registro-operadores")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_listar_operadores_filtrar_por_tipo(self, client):
        payload_frigo = {
            "cuit": "30111111111",
            "razon_social": "FRIGORIFICO",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        }
        payload_carn = {
            "cuit": "30111111112",
            "razon_social": "CARNICERIA",
            "tipo": "CARNICERIA",
            "categoria": "CARNICERIAS",
        }
        client.post("/api/registro-operadores", json=payload_frigo)
        client.post("/api/registro-operadores", json=payload_carn)
        response = client.get(
            "/api/registro-operadores", params={"tipo": "FRIGORIFICO"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["tipo"] == "FRIGORIFICO"

    def test_obtener_operador(self, client):
        payload = {
            "cuit": "30111111111",
            "razon_social": "FRIGORIFICO TEST S.A.",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        }
        created = client.post("/api/registro-operadores", json=payload)
        operador_id = created.json()["id"]
        response = client.get(f"/api/registro-operadores/{operador_id}")
        assert response.status_code == 200
        assert response.json()["razon_social"] == "FRIGORIFICO TEST S.A."

    def test_obtener_operador_no_existente(self, client):
        response = client.get("/api/registro-operadores/99999")
        assert response.status_code == 404

    def test_cambiar_estado(self, client):
        payload = {
            "cuit": "30111111111",
            "razon_social": "FRIGORIFICO TEST S.A.",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        }
        created = client.post("/api/registro-operadores", json=payload)
        operador_id = created.json()["id"]
        response = client.patch(
            f"/api/registro-operadores/{operador_id}/estado",
            params={"estado": "SUSPENDIDO"},
        )
        assert response.status_code == 200
        assert response.json()["estado_registral"] == "SUSPENDIDO"

    def test_cambiar_estado_no_existente(self, client):
        response = client.patch(
            "/api/registro-operadores/99999/estado",
            params={"estado": "ACTIVO"},
        )
        assert response.status_code == 404
