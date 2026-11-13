"""Tests de la API REST del Módulo I — Adjuntos (documentos) de operador."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modulos.registro_operadores.adjunto_operador.dao import AdjuntoOperadorDAO
from modulos.registro_operadores.adjunto_operador.servicio import (
    AdjuntoOperadorService,
)
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


class StorageDummy:
    """Storage en memoria para tests (sin InsForge)."""

    def __init__(self):
        self.files: dict[str, bytes] = {}

    async def upload(self, filename: str, content_type: str, size: int, data: bytes) -> str:
        key = f"test/{filename}"
        self.files[key] = data
        return key

    async def download_url(self, key: str) -> str:
        return f"https://storage.test/{key}"

    async def delete(self, key: str) -> None:
        self.files.pop(key, None)


@pytest.fixture()
def storage():
    return StorageDummy()


@pytest.fixture()
def app(db_session_factory, persona_service, storage):
    """Aplicación FastAPI con el router del módulo (adjuntos con storage dummy)."""
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
    adjunto_service = AdjuntoOperadorService(
        AdjuntoOperadorDAO(db_session_factory),
        storage=storage,
        operador_dao=OperadorDAO(db_session_factory),
        requisito_service=requisito_service,
    )
    router = crear_router(
        operador_service=operador_service,
        catalogo_actividades_dao=catalogo,
        certificado_service=certificado_service,
        requisito_service=requisito_service,
        adjunto_service=adjunto_service,
    )
    application = FastAPI()
    application.include_router(router)
    return application


@pytest.fixture()
def client(app):
    return TestClient(app)


def _crear_operador(db_session_factory, cuit="30111111111") -> int:
    with db_session_factory() as session:
        op = crear_operador_test(session, cuit, "FRIGO ADJUNTOS S.A.")
        session.commit()
        return op.id


class TestAPIAdjuntos:
    """Tests de los endpoints de adjuntos (documentos) de operador."""

    def test_subir_adjunto(self, client, db_session_factory):
        operador_id = _crear_operador(db_session_factory)
        payload = {
            "requisito": "formulario_101",
            "filename": "formulario101.pdf",
            "content_type": "application/pdf",
            "data_base64": "aGVsbG8=",
        }
        response = client.post(
            f"/api/registro-operadores/{operador_id}/adjuntos",
            json=payload,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["operador_id"] == operador_id
        assert data["requisito"] == "formulario_101"
        assert data["content_type"] == "application/pdf"

    def test_subir_adjunto_tipo_no_permitido(self, client, db_session_factory):
        operador_id = _crear_operador(db_session_factory)
        payload = {
            "requisito": "formulario_101",
            "filename": "malware.exe",
            "content_type": "application/x-msdownload",
            "data_base64": "aGVsbG8=",
        }
        response = client.post(
            f"/api/registro-operadores/{operador_id}/adjuntos",
            json=payload,
        )
        assert response.status_code == 400
        assert "no permitido" in response.json()["detail"]

    def test_subir_adjunto_requisito_no_corresponde(self, client, db_session_factory):
        """El requisito debe corresponder a la categoría del operador."""
        operador_id = _crear_operador(db_session_factory)
        payload = {
            "requisito": "plano_camara",  # específico de CAMARAS_FRIGORIFICAS
            "filename": "plano.pdf",
            "content_type": "application/pdf",
            "data_base64": "aGVsbG8=",
        }
        response = client.post(
            f"/api/registro-operadores/{operador_id}/adjuntos",
            json=payload,
        )
        assert response.status_code == 400
        assert "no corresponde" in response.json()["detail"]

    def test_listar_adjuntos(self, client, db_session_factory):
        operador_id = _crear_operador(db_session_factory)
        payload = {
            "requisito": "formulario_101",
            "filename": "formulario101.pdf",
            "content_type": "application/pdf",
            "data_base64": "aGVsbG8=",
        }
        client.post(
            f"/api/registro-operadores/{operador_id}/adjuntos",
            json=payload,
        )
        response = client.get(
            f"/api/registro-operadores/{operador_id}/adjuntos"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_obtener_url_adjunto(self, client, db_session_factory):
        operador_id = _crear_operador(db_session_factory)
        payload = {
            "requisito": "formulario_101",
            "filename": "formulario101.pdf",
            "content_type": "application/pdf",
            "data_base64": "aGVsbG8=",
        }
        created = client.post(
            f"/api/registro-operadores/{operador_id}/adjuntos",
            json=payload,
        )
        adjunto_id = created.json()["id"]
        response = client.get(
            f"/api/registro-operadores/{operador_id}/adjuntos/{adjunto_id}/url"
        )
        assert response.status_code == 200
        assert "storage.test" in response.json()["url"]

    def test_eliminar_adjunto(self, client, db_session_factory):
        operador_id = _crear_operador(db_session_factory)
        payload = {
            "requisito": "formulario_101",
            "filename": "formulario101.pdf",
            "content_type": "application/pdf",
            "data_base64": "aGVsbG8=",
        }
        created = client.post(
            f"/api/registro-operadores/{operador_id}/adjuntos",
            json=payload,
        )
        adjunto_id = created.json()["id"]
        response = client.delete(
            f"/api/registro-operadores/{operador_id}/adjuntos/{adjunto_id}"
        )
        assert response.status_code == 204
        # Verificar que se eliminó
        listados = client.get(
            f"/api/registro-operadores/{operador_id}/adjuntos"
        ).json()
        assert len(listados) == 0

    def test_operador_inexistente(self, client):
        """El controlador mapea OperadorError → 400 en el POST de adjuntos."""
        payload = {
            "requisito": "formulario_101",
            "filename": "formulario101.pdf",
            "content_type": "application/pdf",
            "data_base64": "aGVsbG8=",
        }
        response = client.post(
            "/api/registro-operadores/99999/adjuntos",
            json=payload,
        )
        assert response.status_code == 400
        assert "No existe un operador" in response.json()["detail"]
