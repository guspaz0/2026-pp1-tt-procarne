"""Fixtures del Módulo II — Trazabilidad Comercial."""

from __future__ import annotations

import pytest

# Reutilizar fixtures de configuración compartidas
from tests.fixtures import db_engine, db_session_factory, db_dao  # noqa: F401

# Importar los modelos del módulo para que Base.metadata los conozca
from modulos.trazabilidad_comercial.dao import RegistroTrazabilidad  # noqa: F401


@pytest.fixture()
def session_factory(db_session_factory):
    """Alias de :func:`db_session_factory` para compatibilidad."""
    return db_session_factory
