"""Tests de la API REST del Módulo I — Catálogo de actividades económicas."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modulos.registro_operadores.actividad_economica.dao import (
    ActividadEconomica,
    CatalogoActividadesDAO,
    GrupoActividad,
    SubgrupoActividad,
)
from modulos.registro_operadores.controlador import crear_router
from modulos.registro_operadores.operador.dao import OperadorDAO
from modulos.registro_operadores.operador.servicio import OperadorService


@pytest.fixture()
def app(db_session_factory, persona_service):
    """Aplicación FastAPI con el router del módulo."""
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
    return TestClient(app)


def _seed_catalogo_minimo(db_session_factory):
    """Carga un catálogo mínimo: 1 grupo, 1 subgrupo, 2 actividades."""
    with db_session_factory() as session:
        grupo = GrupoActividad(codigo="A", descripcion="Ganadería y agricultura")
        session.add(grupo)
        session.flush()
        subgrupo = SubgrupoActividad(
            grupo_id="A", codigo="11", descripcion="Faena de ganado"
        )
        session.add(subgrupo)
        session.flush()
        act1 = ActividadEconomica(
            codigo="11110", grupo_id="A", subgrupo_codigo="11",
            descripcion="Faena de ganado bovino",
        )
        act2 = ActividadEconomica(
            codigo="11120", grupo_id="A", subgrupo_codigo="11",
            descripcion="Faena de ganado ovino",
        )
        session.add_all([act1, act2])
        session.commit()


class TestAPICatalogoActividades:
    """Tests de los endpoints del catálogo de actividades económicas."""

    def test_listar_grupos(self, client, db_session_factory):
        _seed_catalogo_minimo(db_session_factory)
        response = client.get("/api/registro-operadores/catalogo/actividades/grupos")
        assert response.status_code == 200
        grupos = response.json()
        assert len(grupos) == 1
        assert grupos[0]["codigo"] == "A"
        assert grupos[0]["descripcion"] == "Ganadería y agricultura"

    def test_listar_subgrupos(self, client, db_session_factory):
        _seed_catalogo_minimo(db_session_factory)
        response = client.get("/api/registro-operadores/catalogo/actividades/subgrupos")
        assert response.status_code == 200
        subgrupos = response.json()
        assert len(subgrupos) == 1
        assert subgrupos[0]["codigo"] == "11"

    def test_listar_subgrupos_filtrar_por_grupo(self, client, db_session_factory):
        _seed_catalogo_minimo(db_session_factory)
        response = client.get(
            "/api/registro-operadores/catalogo/actividades/subgrupos",
            params={"grupo": "A"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_listar_actividades(self, client, db_session_factory):
        _seed_catalogo_minimo(db_session_factory)
        response = client.get("/api/registro-operadores/catalogo/actividades")
        assert response.status_code == 200
        actividades = response.json()
        assert len(actividades) == 2
        codigos = [a["codigo"] for a in actividades]
        assert "11110" in codigos
        assert "11120" in codigos

    def test_listar_actividades_filtrar_por_grupo(self, client, db_session_factory):
        _seed_catalogo_minimo(db_session_factory)
        response = client.get(
            "/api/registro-operadores/catalogo/actividades",
            params={"grupo": "A"},
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_listar_actividades_vacio(self, client):
        """Sin datos seed → lista vacía (200)."""
        response = client.get("/api/registro-operadores/catalogo/actividades")
        assert response.status_code == 200
        assert response.json() == []
