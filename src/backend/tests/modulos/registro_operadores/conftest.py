"""Fixtures del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

import pytest

# Reutilizar fixtures de configuración compartidas
from tests.fixtures import db_engine, db_session_factory, db_dao  # noqa: F401

# Importar los modelos del módulo (y la tabla personas, FK NOT NULL de
# operadores) para que Base.metadata los conozca al crear las tablas.
from core.persona.dao import Persona  # noqa: F401
from core.persona.servicio import PersonaService  # noqa: F401
from modulos.registro_operadores.dao import (  # noqa: F401
    Operador,
)


@pytest.fixture()
def session_factory(db_session_factory):
    """Alias de :func:`db_session_factory` para compatibilidad."""
    return db_session_factory


@pytest.fixture()
def persona_service(db_session_factory):
    """PersonaService sobre la BD en memoria (para resolver la persona titular)."""
    from core.persona.dao import PersonaDAO
    from core.persona.servicio import PersonaService

    return PersonaService(PersonaDAO(db_session_factory))


@pytest.fixture()
def operador_service(db_session_factory, persona_service):
    """OperadorService con sus servicios delegados inyectados."""
    from modulos.registro_operadores.adjunto_operador.dao import AdjuntoOperadorDAO
    from modulos.registro_operadores.certificado.dao import CertificadoDAO
    from modulos.registro_operadores.operador.dao import OperadorDAO
    from modulos.registro_operadores.operador.servicio import OperadorService
    from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
    from modulos.registro_operadores.requisito_inscripcion.servicio import RequisitoInscripcionService

    operador_dao = OperadorDAO(db_session_factory)
    requisito_service = RequisitoInscripcionService(RequisitoInscripcionDAO(db_session_factory))

    return OperadorService(
        operador_dao,
        persona_service=persona_service,
        requisito_service=requisito_service,
    )
