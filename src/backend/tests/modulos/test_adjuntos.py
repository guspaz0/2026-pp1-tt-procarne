"""Tests de adjuntos (persona y operador).

Cubre:
- Validación de content type y tamaño
- Validación de requisito por categoría
- Listado de adjuntos
- Eliminación de adjuntos
- Storage no configurado → error
"""

from __future__ import annotations

import asyncio
import base64
from unittest.mock import AsyncMock

import pytest

from core.persona.adjunto_dao import AdjuntoPersonaDAO
from core.persona.dao import Persona, PersonaDAO
from core.persona.servicio import PersonaError, PersonaService
from configs.dao import crear_dao
from modulos.registro_operadores.adjunto_dao import AdjuntoOperadorDAO
from modulos.registro_operadores.dao import ROCCAOperador, ROCCAOperadorDAO
from modulos.registro_operadores.enums import CategoriaOperador
from modulos.registro_operadores.servicio import ROCCAOperadorError, ROCCAOperadorService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db():
    dao = crear_dao("sqlite:///:memory:")
    dao.crear_tablas()
    yield dao
    # SQLite in-memory no necesita cierre explícito


@pytest.fixture
def persona_service(db):
    persona_dao = PersonaDAO(db.obtener_sesion)
    adjunto_dao = AdjuntoPersonaDAO(db.obtener_sesion)
    return PersonaService(persona_dao, adjunto_dao=adjunto_dao, storage=None)


@pytest.fixture
def operador_service(db):
    dao = ROCCAOperadorDAO(db.obtener_sesion)
    adjunto_dao = AdjuntoOperadorDAO(db.obtener_sesion)
    return ROCCAOperadorService(dao, adjunto_dao=adjunto_dao, storage=None)


@pytest.fixture
def mock_storage():
    """Storage mock que simula éxito."""
    storage = AsyncMock()
    storage.upload = AsyncMock(return_value="uploads/test-file.jpg")
    storage.download_url = AsyncMock(return_value="https://insforge.test/files/test-file.jpg")
    storage.delete = AsyncMock()
    return storage


def _crear_persona(db, doc="12345678", nombre="Test User"):
    """Crea una persona física y devuelve su id."""
    with db.obtener_sesion() as s:
        p = Persona(tipo="fisica", tipo_documento="DNI", identificador=doc, nombre=nombre)
        s.add(p)
        s.commit()
        return p.id


def _crear_operador(db, categoria=CategoriaOperador.SALA_DE_DESPOSTE.value):
    """Crea un operador con persona jurídica y devuelve su id."""
    with db.obtener_sesion() as s:
        p = Persona(tipo="juridica", tipo_documento="CUIT", identificador="30-12345678-9", nombre="Empresa SA")
        s.add(p)
        s.commit()
        op = ROCCAOperador(
            persona_id=p.id,
            cuit="3012345678901",
            razon_social="Empresa SA",
            tipo="empresa",
            categoria=categoria,
            estado_registral="ACTIVO",
        )
        s.add(op)
        s.commit()
        return op.id


# ---------------------------------------------------------------------------
# Persona adjuntos
# ---------------------------------------------------------------------------

class TestPersonaAdjuntos:
    def test_storage_no_configurado(self, persona_service, db):
        """Sin storage configurado, subir adjunto debe fallar."""
        pid = _crear_persona(db)
        with pytest.raises(PersonaError, match="Storage no configurado"):
            asyncio.run(persona_service.subir_adjunto(
                persona_id=pid, requisito="dni_frente",
                filename="dni.jpg", content_type="image/jpeg",
                size=100, data=b"x" * 100,
            ))

    def test_requisito_invalido(self, persona_service, db, mock_storage):
        """Requisito no válido para persona."""
        persona_service._storage = mock_storage
        pid = _crear_persona(db)
        with pytest.raises(PersonaError, match="Requisito inválido"):
            asyncio.run(persona_service.subir_adjunto(
                persona_id=pid, requisito="FORMULARIO_101",
                filename="f.jpg", content_type="image/jpeg",
                size=100, data=b"x" * 100,
            ))

    def test_content_type_invalido(self, persona_service, db, mock_storage):
        """Content type no permitido."""
        persona_service._storage = mock_storage
        pid = _crear_persona(db)
        with pytest.raises(PersonaError, match="no permitido"):
            asyncio.run(persona_service.subir_adjunto(
                persona_id=pid, requisito="dni_frente",
                filename="dni.exe", content_type="application/x-msdownload",
                size=100, data=b"x" * 100,
            ))

    def test_tamano_excedido(self, persona_service, db, mock_storage):
        """Archivo > 10 MB."""
        persona_service._storage = mock_storage
        pid = _crear_persona(db)
        with pytest.raises(PersonaError, match="tamaño"):
            asyncio.run(persona_service.subir_adjunto(
                persona_id=pid, requisito="dni_frente",
                filename="grande.jpg", content_type="image/jpeg",
                size=11 * 1024 * 1024, data=b"x",
            ))

    def test_subir_y_listar(self, persona_service, db, mock_storage):
        """Sube un adjunto y lo lista."""
        persona_service._storage = mock_storage
        pid = _crear_persona(db)

        result = asyncio.run(persona_service.subir_adjunto(
            persona_id=pid, requisito="dni_frente",
            filename="dni.jpg", content_type="image/jpeg",
            size=100, data=b"x" * 100,
        ))
        assert result["requisito"] == "dni_frente"
        assert result["persona_id"] == pid
        assert result["storage_key"] == "uploads/test-file.jpg"

        adjuntos = persona_service.listar_adjuntos(pid)
        assert len(adjuntos) == 1
        assert adjuntos[0]["requisito"] == "dni_frente"

    def test_eliminar_adjunto(self, persona_service, db, mock_storage):
        """Elimina un adjunto."""
        persona_service._storage = mock_storage
        pid = _crear_persona(db)

        result = asyncio.run(persona_service.subir_adjunto(
            persona_id=pid, requisito="dni_frente",
            filename="dni.jpg", content_type="image/jpeg",
            size=100, data=b"x" * 100,
        ))
        adjunto_id = result["id"]

        asyncio.run(persona_service.eliminar_adjunto(pid, adjunto_id))
        assert mock_storage.delete.called
        assert persona_service.listar_adjuntos(pid) == []

    def test_persona_no_existe(self, persona_service, db, mock_storage):
        """Persona inexistente."""
        persona_service._storage = mock_storage
        with pytest.raises(PersonaError, match="No existe"):
            asyncio.run(persona_service.subir_adjunto(
                persona_id=99999, requisito="dni_frente",
                filename="dni.jpg", content_type="image/jpeg",
                size=100, data=b"x" * 100,
            ))


# ---------------------------------------------------------------------------
# Operador adjuntos
# ---------------------------------------------------------------------------

class TestOperadorAdjuntos:
    def test_requisito_no_corresponde_categoria(self, operador_service, db, mock_storage):
        """Un requisito de FABRICA no puede subirse a un SALA_DE_DESPOSTE."""
        operador_service._storage = mock_storage
        op_id = _crear_operador(db, CategoriaOperador.SALA_DE_DESPOSTE.value)

        with pytest.raises(ROCCAOperadorError, match="no corresponde"):
            asyncio.run(operador_service.subir_adjunto_operador(
                operador_id=op_id, requisito="libreta_sanitaria",
                filename="libro.pdf", content_type="application/pdf",
                size=100, data=b"x" * 100,
            ))

    def test_requisito_valido_para_categoria(self, operador_service, db, mock_storage):
        """Un requisito válido para la categoría se sube correctamente."""
        operador_service._storage = mock_storage
        op_id = _crear_operador(db, CategoriaOperador.SALA_DE_DESPOSTE.value)

        result = asyncio.run(operador_service.subir_adjunto_operador(
            operador_id=op_id, requisito="habilitacion_municipal",
            filename="habilitacion.pdf", content_type="application/pdf",
            size=100, data=b"x" * 100,
        ))
        assert result["requisito"] == "habilitacion_municipal"
        assert result["operador_id"] == op_id

    def test_listar_adjuntos_operador(self, operador_service, db, mock_storage):
        """Lista adjuntos de un operador."""
        operador_service._storage = mock_storage
        op_id = _crear_operador(db, CategoriaOperador.SALA_DE_DESPOSTE.value)

        asyncio.run(operador_service.subir_adjunto_operador(
            operador_id=op_id, requisito="habilitacion_municipal",
            filename="hab.pdf", content_type="application/pdf",
            size=100, data=b"x" * 100,
        ))
        asyncio.run(operador_service.subir_adjunto_operador(
            operador_id=op_id, requisito="afip_ultimo_pago",
            filename="afip.jpg", content_type="image/jpeg",
            size=100, data=b"x" * 100,
        ))

        adjuntos = operador_service.listar_adjuntos_operador(op_id)
        assert len(adjuntos) == 2

    def test_operador_no_existe(self, operador_service, db, mock_storage):
        """Operador inexistente."""
        operador_service._storage = mock_storage
        with pytest.raises(ROCCAOperadorError, match="No existe"):
            asyncio.run(operador_service.subir_adjunto_operador(
                operador_id=99999, requisito="afip_ultimo_pago",
                filename="afip.jpg", content_type="image/jpeg",
                size=100, data=b"x" * 100,
            ))

    def test_validar_requisito_para_categoria(self, operador_service):
        """El método de validación devuelve True/False correctamente."""
        # Específico de SALA_DE_DESPOSTE
        assert operador_service.validar_requisito_para_categoria(
            CategoriaOperador.SALA_DE_DESPOSTE.value, "habilitacion_municipal"
        )
        # No corresponde a SALA_DE_DESPOSTE
        assert not operador_service.validar_requisito_para_categoria(
            CategoriaOperador.SALA_DE_DESPOSTE.value, "libreta_sanitaria"
        )
        # Generales siempre válidos
        assert operador_service.validar_requisito_para_categoria(
            CategoriaOperador.TRANSPONEDOR.value, "afip_ultimo_pago"
        )

    def test_transponedor_sin_especificos(self, operador_service, db, mock_storage):
        """TRANSPONEDOR no tiene requisitos específicos, solo generales."""
        operador_service._storage = mock_storage
        op_id = _crear_operador(db, CategoriaOperador.TRANSPONEDOR.value)

        # General: OK
        result = asyncio.run(operador_service.subir_adjunto_operador(
            operador_id=op_id, requisito="afip_ultimo_pago",
            filename="afip.jpg", content_type="image/jpeg",
            size=100, data=b"x" * 100,
        ))
        assert result["requisito"] == "afip_ultimo_pago"

        # Específico de otra categoría: NO
        with pytest.raises(ROCCAOperadorError, match="no corresponde"):
            asyncio.run(operador_service.subir_adjunto_operador(
                operador_id=op_id, requisito="habilitacion_municipal",
                filename="hab.pdf", content_type="application/pdf",
                size=100, data=b"x" * 100,
            ))
