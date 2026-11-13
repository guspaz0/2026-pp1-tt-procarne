"""Tests de la API REST del Módulo I — Certificados de habilitación."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modulos.registro_operadores.certificado.dao import CertificadoDAO
from modulos.registro_operadores.certificado.servicio import CertificadoService
from modulos.registro_operadores.controlador import crear_router
from modulos.registro_operadores.operador.dao import OperadorDAO
from modulos.registro_operadores.operador.servicio import OperadorService
from modulos.registro_operadores.requisito_inscripcion.dao import (
    RequisitoInscripcionDAO,
)
from modulos.registro_operadores.requisito_inscripcion.servicio import (
    RequisitoInscripcionService,
)

from .conftest import crear_operador_test


@pytest.fixture()
def app(db_session_factory, persona_service):
    """Aplicación FastAPI con el router del módulo."""
    from modulos.registro_operadores.actividad_economica.dao import CatalogoActividadesDAO

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

    # Middleware de test: inyecta un usuario supervisor autenticado
    # (en producción lo hace el middleware de InsForge).
    @application.middleware("http")
    async def _auth(request, call_next):
        request.state.user = {"user_metadata": {"rol": "supervisor"}}
        return await call_next(request)

    return application


@pytest.fixture()
def client(app):
    return TestClient(app)


def _crear_operador_activo(db_session_factory, cuit="30111111111") -> int:
    """Crea un operador ACTIVO (estado requerido para certificados)."""
    with db_session_factory() as session:
        op = crear_operador_test(
            session, cuit, "FRIGO CERT S.A.", estado_registral="ACTIVO"
        )
        session.commit()
        return op.id


class TestAPICertificados:
    """Tests de los endpoints de certificados."""

    def test_crear_certificado(self, client, db_session_factory):
        operador_id = _crear_operador_activo(db_session_factory)
        payload = {
            "numero_certificado": "F102-0001",
            "fecha_emision": datetime.now(timezone.utc).isoformat(),
        }
        response = client.post(
            f"/api/registro-operadores/{operador_id}/certificados",
            json=payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["numero_certificado"] == "F102-0001"
        assert data["operador_id"] == operador_id
        assert data["estado"] == "ACTIVO"

    def test_listar_certificados(self, client, db_session_factory):
        operador_id = _crear_operador_activo(db_session_factory)
        payload = {
            "numero_certificado": "F102-0001",
            "fecha_emision": datetime.now(timezone.utc).isoformat(),
        }
        client.post(
            f"/api/registro-operadores/{operador_id}/certificados",
            json=payload,
        )
        response = client.get(
            f"/api/registro-operadores/{operador_id}/certificados"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_certificado_vigente(self, client, db_session_factory):
        operador_id = _crear_operador_activo(db_session_factory)
        payload = {
            "numero_certificado": "F102-0001",
            "fecha_emision": datetime.now(timezone.utc).isoformat(),
        }
        client.post(
            f"/api/registro-operadores/{operador_id}/certificados",
            json=payload,
        )
        response = client.get(
            f"/api/registro-operadores/{operador_id}/certificado-vigente"
        )
        assert response.status_code == 200
        assert response.json()["numero_certificado"] == "F102-0001"

    def test_certificado_vigente_no_existente(self, client, db_session_factory):
        operador_id = _crear_operador_activo(db_session_factory)
        response = client.get(
            f"/api/registro-operadores/{operador_id}/certificado-vigente"
        )
        assert response.status_code == 404

    def test_operador_no_activo_no_puede_certificarse(self, client, db_session_factory):
        """Un operador en estado PENDIENTE no puede tener certificado."""
        with db_session_factory() as session:
            op = crear_operador_test(
                session, "30222222222", "FRIGO PENDIENTE", estado_registral="PENDIENTE"
            )
            session.commit()
            operador_id = op.id
        payload = {
            "numero_certificado": "F102-0002",
            "fecha_emision": datetime.now(timezone.utc).isoformat(),
        }
        response = client.post(
            f"/api/registro-operadores/{operador_id}/certificados",
            json=payload,
        )
        assert response.status_code == 400
        assert "ACTIVO" in response.json()["detail"]

    def test_operador_inexistente_404(self, client):
        payload = {
            "numero_certificado": "F102-0003",
            "fecha_emision": datetime.now(timezone.utc).isoformat(),
        }
        response = client.post(
            "/api/registro-operadores/99999/certificados",
            json=payload,
        )
        assert response.status_code == 404
