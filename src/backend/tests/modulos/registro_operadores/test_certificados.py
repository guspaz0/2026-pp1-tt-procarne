"""Tests B7 — Certificados F102, estado PENDIENTE, RBAC."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modulos.registro_operadores.dao import (
    Certificado,
    ROCCAOperador,
    ROCCAOperadorDAO,
)
from modulos.registro_operadores.enums import (
    CategoriaOperador,
    EstadoCertificado,
    EstadoRegistral,
    TipoOperador,
)
from modulos.registro_operadores.schema import (
    CertificadoIn,
    ROCCAOperadorIn,
)
from modulos.registro_operadores.controlador import crear_router
from modulos.registro_operadores.servicio import ROCCAOperadorService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def operador_service(db_session_factory, persona_service):
    dao = ROCCAOperadorDAO(db_session_factory)
    return ROCCAOperadorService(dao, persona_service=persona_service)


@pytest.fixture()
def operador_activo(operador_service):
    """Crea un operador y lo pone ACTIVO manualmente."""
    data = ROCCAOperadorIn(
        cuit="30-12345678-9",
        razon_social="TEST ACTIVO S.A.",
        tipo=TipoOperador.FRIGORIFICO.value,
        categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
    )
    op = operador_service.crear_operador(data)
    # Ponerlo ACTIVO para los tests de certificados
    operador_service._dao.actualizar_estado(op.id, EstadoRegistral.ACTIVO)
    return op


@pytest.fixture()
def operador_pendiente(operador_service):
    """Crea un operador que queda PENDIENTE (default)."""
    data = ROCCAOperadorIn(
        cuit="30-98765432-1",
        razon_social="TEST PENDIENTE S.A.",
        tipo=TipoOperador.FRIGORIFICO.value,
        categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
    )
    return operador_service.crear_operador(data)


def _crear_cert(operador_id: int, numero: str, venc: datetime | None, emision: datetime, estado: str = "ACTIVO") -> None:
    """Helper para insertar certificados directamente en la BD."""
    pass  # Se usa el servicio


# ---------------------------------------------------------------------------
# B7.1 — obtener_certificado_vigente
# ---------------------------------------------------------------------------

class TestCertificadoVigente:

    def test_sin_certificados(self, operador_activo, operador_service):
        assert operador_service.obtener_certificado_vigente(operador_activo.id) is None

    def test_un_solo_certificado(self, operador_activo, operador_service):
        data = CertificadoIn(
            numero_certificado="F-102-001",
            fecha_emision=datetime(2025, 1, 1, tzinfo=timezone.utc),
            fecha_vencimiento=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        cert = operador_service.crear_certificado(operador_activo.id, data)
        vigente = operador_service.obtener_certificado_vigente(operador_activo.id)
        assert vigente is not None
        assert vigente.numero_certificado == "F-102-001"

    def test_elige_max_vencimiento(self, operador_activo, operador_service):
        # Cert 1: vence 2025
        c1 = CertificadoIn(
            numero_certificado="F-102-001",
            fecha_emision=datetime(2024, 1, 1, tzinfo=timezone.utc),
            fecha_vencimiento=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        # Cert 2: vence 2026 (más lejano)
        c2 = CertificadoIn(
            numero_certificado="F-102-002",
            fecha_emision=datetime(2025, 6, 1, tzinfo=timezone.utc),
            fecha_vencimiento=datetime(2026, 6, 1, tzinfo=timezone.utc),
        )
        operador_service.crear_certificado(operador_activo.id, c1)
        operador_service.crear_certificado(operador_activo.id, c2)
        vigente = operador_service.obtener_certificado_vigente(operador_activo.id)
        assert vigente is not None
        assert vigente.numero_certificado == "F-102-002"

    def test_ignora_relevado(self, operador_activo, operador_service):
        # Cert 1: ACTIVO, vence 2026
        c1 = CertificadoIn(
            numero_certificado="F-102-001",
            fecha_emision=datetime(2025, 1, 1, tzinfo=timezone.utc),
            fecha_vencimiento=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        # Cert 2: se emite antes del vencimiento de c1 → c1 pasa a RELEVADO
        c2 = CertificadoIn(
            numero_certificado="F-102-002",
            fecha_emision=datetime(2025, 6, 1, tzinfo=timezone.utc),
            fecha_vencimiento=datetime(2027, 6, 1, tzinfo=timezone.utc),
        )
        operador_service.crear_certificado(operador_activo.id, c1)
        operador_service.crear_certificado(operador_activo.id, c2)
        vigente = operador_service.obtener_certificado_vigente(operador_activo.id)
        assert vigente is not None
        # c1 fue relevado, así que el vigente es c2
        assert vigente.numero_certificado == "F-102-002"

    def test_sin_vencimiento_infinito(self, operador_activo, operador_service):
        # Cert 1: con vencimiento 2026
        c1 = CertificadoIn(
            numero_certificado="F-102-001",
            fecha_emision=datetime(2025, 1, 1, tzinfo=timezone.utc),
            fecha_vencimiento=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        # Cert 2: sin vencimiento (None = ∞)
        c2 = CertificadoIn(
            numero_certificado="F-102-002",
            fecha_emision=datetime(2025, 6, 1, tzinfo=timezone.utc),
            fecha_vencimiento=None,
        )
        operador_service.crear_certificado(operador_activo.id, c1)
        operador_service.crear_certificado(operador_activo.id, c2)
        vigente = operador_service.obtener_certificado_vigente(operador_activo.id)
        assert vigente is not None
        # Sin vencimiento = infinito → gana
        assert vigente.numero_certificado == "F-102-002"

    def test_operador_no_existe(self, operador_service):
        from modulos.registro_operadores.servicio import ROCCAOperadorError
        with pytest.raises(ROCCAOperadorError):
            operador_service.obtener_certificado_vigente(99999)


# ---------------------------------------------------------------------------
# B7.4 — RBAC: crear_certificado requiere rol + estado ACTIVO
# ---------------------------------------------------------------------------

class TestRBACCertificados:

    def _app(self, operador_service):
        from modulos.registro_operadores.controlador import crear_router
        app = FastAPI()
        app.include_router(crear_router(operador_service))
        return TestClient(app)

    def test_crear_certificado_requiere_rol(self, operador_activo, operador_service):
        """Sin rol supervisor → 403."""
        client = self._app(operador_service)
        data = {
            "numero_certificado": "F-102-001",
            "fecha_emision": "2025-01-01T00:00:00Z",
        }
        r = client.post(f"/api/registro-operadores/{operador_activo.id}/certificados", json=data)
        # Sin middleware de auth, request.state.user no existe → 401
        assert r.status_code in (401, 403)

    def test_no_puede_certificar_operador_pendiente(self, operador_pendiente, operador_service):
        """Operador PENDIENTE → 400 aunque tenga rol."""
        # Simular rol supervisor mediante middleware
        from fastapi import Request
        app = FastAPI()

        @app.middleware("http")
        async def fake_auth(request: Request, call_next):
            request.state.user = {"user_metadata": {"rol": "supervisor"}}
            return await call_next(request)

        app.include_router(crear_router(operador_service))
        client = TestClient(app)

        data = {
            "numero_certificado": "F-102-001",
            "fecha_emision": "2025-01-01T00:00:00Z",
        }
        r = client.post(f"/api/registro-operadores/{operador_pendiente.id}/certificados", json=data)
        assert r.status_code == 400
        assert "ACTIVO" in r.json()["detail"]

    def test_certificar_operador_activo(self, operador_activo, operador_service):
        """Operador ACTIVO + rol supervisor → 201."""
        from fastapi import Request
        app = FastAPI()

        @app.middleware("http")
        async def fake_auth(request: Request, call_next):
            request.state.user = {"user_metadata": {"rol": "supervisor"}}
            return await call_next(request)

        app.include_router(crear_router(operador_service))
        client = TestClient(app)

        data = {
            "numero_certificado": "F-102-001",
            "fecha_emision": "2025-01-01T00:00:00Z",
            "fecha_vencimiento": "2026-01-01T00:00:00Z",
        }
        r = client.post(f"/api/registro-operadores/{operador_activo.id}/certificados", json=data)
        assert r.status_code == 201
        assert r.json()["numero_certificado"] == "F-102-001"


# ---------------------------------------------------------------------------
# B7.5 — Estado PENDIENTE + endpoint activar
# ---------------------------------------------------------------------------

class TestEstadoPendiente:

    def test_operador_nuevo_estado_pendiente(self, operador_pendiente):
        assert operador_pendiente.estado_registral == "PENDIENTE"

    def _app_supervisor(self, operador_service):
        from fastapi import Request
        app = FastAPI()

        @app.middleware("http")
        async def fake_auth(request: Request, call_next):
            request.state.user = {"user_metadata": {"rol": "supervisor"}}
            return await call_next(request)

        app.include_router(crear_router(operador_service))
        return TestClient(app)

    def test_activar_operador_pendiente(self, operador_pendiente, operador_service):
        client = self._app_supervisor(operador_service)
        r = client.post(f"/api/registro-operadores/{operador_pendiente.id}/activar")
        assert r.status_code == 200
        assert r.json()["estado_registral"] == "ACTIVO"

    def test_activar_operador_ya_activo(self, operador_activo, operador_service):
        client = self._app_supervisor(operador_service)
        r = client.post(f"/api/registro-operadores/{operador_activo.id}/activar")
        assert r.status_code == 400
        assert "ya está ACTIVO" in r.json()["detail"]

    def test_suspender_operador_activo(self, operador_activo, operador_service):
        client = self._app_supervisor(operador_service)
        r = client.post(f"/api/registro-operadores/{operador_activo.id}/suspender")
        assert r.status_code == 200
        assert r.json()["estado_registral"] == "SUSPENDIDO"

    def test_reactivar_operador_suspendido(self, operador_activo, operador_service):
        client = self._app_supervisor(operador_service)
        # Suspender primero
        client.post(f"/api/registro-operadores/{operador_activo.id}/suspender")
        # Reactivar
        r = client.post(f"/api/registro-operadores/{operador_activo.id}/reactivar")
        assert r.status_code == 200
        assert r.json()["estado_registral"] == "ACTIVO"

    def test_bajar_operador_activo(self, operador_activo, operador_service):
        client = self._app_supervisor(operador_service)
        r = client.post(f"/api/registro-operadores/{operador_activo.id}/bajar")
        assert r.status_code == 200
        assert r.json()["estado_registral"] == "BAJADO"

    def test_no_puede_certificar_operador_suspendido(self, operador_activo, operador_service):
        """Operador SUSPENDIDO → 400."""
        # Suspender
        operador_service._dao.actualizar_estado(operador_activo.id, EstadoRegistral.SUSPENDIDO)
        client = self._app_supervisor(operador_service)
        data = {
            "numero_certificado": "F-102-001",
            "fecha_emision": "2025-01-01T00:00:00Z",
        }
        r = client.post(f"/api/registro-operadores/{operador_activo.id}/certificados", json=data)
        assert r.status_code == 400
        assert "SUSPENDIDO" in r.json()["detail"]


# ---------------------------------------------------------------------------
# B7.2 — Endpoint certificado-vigente
# ---------------------------------------------------------------------------

class TestEndpointCertificadoVigente:

    def _app(self, operador_service):
        from modulos.registro_operadores.controlador import crear_router
        app = FastAPI()
        app.include_router(crear_router(operador_service))
        return TestClient(app)

    def test_no_existe(self, operador_activo, operador_service):
        client = self._app(operador_service)
        r = client.get(f"/api/registro-operadores/{operador_activo.id}/certificado-vigente")
        assert r.status_code == 404

    def test_con_certificado(self, operador_activo, operador_service):
        data = CertificadoIn(
            numero_certificado="F-102-001",
            fecha_emision=datetime(2025, 1, 1, tzinfo=timezone.utc),
            fecha_vencimiento=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        operador_service.crear_certificado(operador_activo.id, data)
        client = self._app(operador_service)
        r = client.get(f"/api/registro-operadores/{operador_activo.id}/certificado-vigente")
        assert r.status_code == 200
        assert r.json()["numero_certificado"] == "F-102-001"


# ---------------------------------------------------------------------------
# B7.3 — PDF base64
# ---------------------------------------------------------------------------

class TestPDFBase64:

    def test_pdf_devuelve_base64(self, operador_activo, operador_service):
        """GET /certificado.pdf devuelve JSON con pdf_base64."""
        from modulos.registro_operadores.controlador import crear_router
        app = FastAPI()
        app.include_router(crear_router(operador_service))
        client = TestClient(app)

        r = client.get(f"/api/registro-operadores/{operador_activo.id}/certificado.pdf")
        assert r.status_code == 200
        body = r.json()
        assert "pdf_base64" in body
        assert "nombre_archivo" in body
        assert body["content_type"] == "application/pdf"
        # Verificar que es base64 válido
        import base64
        decoded = base64.b64decode(body["pdf_base64"])
        assert decoded[:4] == b"%PDF"  # Header PDF
