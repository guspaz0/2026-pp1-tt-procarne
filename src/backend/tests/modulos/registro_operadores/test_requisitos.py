"""Tests de la API REST del Módulo I — Requisitos de inscripción."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

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
    from modulos.registro_operadores.certificado.dao import CertificadoDAO
    from modulos.registro_operadores.certificado.servicio import CertificadoService

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
    application.state.operador_service = operador_service
    application.include_router(router)
    return application


@pytest.fixture()
def client(app):
    return TestClient(app)


def _crear_operador(app, cuit="30111111111") -> int:
    """Crea el operador vía OperadorService (genera sus requisitos iniciales)."""
    from modulos.registro_operadores.operador.dto import OperadorIn

    # El fixture ``app`` guarda el servicio para que los tests puedan crear
    # operadores con la misma lógica de negocio (requisitos iniciales, etc.).
    operador_service = app.state.operador_service
    out = operador_service.crear_operador(OperadorIn(
        cuit=cuit, razon_social="FRIGO REQUISITOS S.A.",
        tipo="FRIGORIFICO", categoria="SALA_DE_DESPOSTE",
    ))
    return out.id


class TestAPIRequisitos:
    """Tests de los endpoints de requisitos de inscripción."""

    def test_catalogo_requisitos(self, client):
        response = client.get("/api/registro-operadores/catalogo/requisitos")
        assert response.status_code == 200
        data = response.json()
        assert "generales" in data
        assert "especificos_por_categoria" in data
        # Los requisitos de sala de desposte incluyen el formulario 101
        codigos = data["especificos_por_categoria"]["SALA_DE_DESPOSTE"]
        assert "formulario_101" in codigos

    def test_listar_requisitos_operador(self, client, app):
        operador_id = _crear_operador(app)
        response = client.get(
            f"/api/registro-operadores/{operador_id}/requisitos"
        )
        assert response.status_code == 200
        requisitos = response.json()
        assert isinstance(requisitos, list)
        # Un operador con categoría SALA_DE_DESPOSTE tiene requisitos generales
        # + específicos de su categoría
        assert len(requisitos) > 0
        assert all(r["operador_id"] == operador_id for r in requisitos)

    def test_listar_requisitos_operador_inexistente(self, client):
        response = client.get(
            "/api/registro-operadores/99999/requisitos"
        )
        # El endpoint no valida la existencia del operador: devuelve []
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_requisitos_pendientes(self, client, app):
        operador_id = _crear_operador(app)
        response = client.get(
            f"/api/registro-operadores/{operador_id}/requisitos/pendientes"
        )
        assert response.status_code == 200
        pendientes = response.json()
        assert all(r["cumplido"] is False for r in pendientes)

    def test_actualizar_requisito(self, client, app):
        operador_id = _crear_operador(app)
        # Obtener un requisito del operador
        listados = client.get(
            f"/api/registro-operadores/{operador_id}/requisitos"
        ).json()
        requisito = listados[0]
        response = client.patch(
            f"/api/registro-operadores/{operador_id}/requisitos/{requisito['id']}",
            params={"cumplido": "true", "observaciones": "Verificado"},
        )
        assert response.status_code == 200
        assert response.json()["cumplido"] is True
        assert response.json()["observaciones"] == "Verificado"
        assert response.json()["fecha_cumplimiento"] is not None

    def test_actualizar_requisito_no_existente(self, client, app):
        operador_id = _crear_operador(app)
        response = client.patch(
            f"/api/registro-operadores/{operador_id}/requisitos/99999",
            params={"cumplido": "true"},
        )
        assert response.status_code == 404
