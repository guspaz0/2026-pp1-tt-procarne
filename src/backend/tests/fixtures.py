"""Fixtures de configuración compartidas para todos los módulos de tests.

Proporciona la base de datos SQLite en memoria (engine, sesión y DAO)
para que cualquier módulo de tests pueda reutilizar la misma configuración
sin duplicar código.

Uso en el conftest.py de un módulo::

    from tests.fixtures import db_config  # noqa: F401  (registra las fixtures)
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from configs.db import Base
from configs.dao import SQLiteDAO


# ---------------------------------------------------------------------------
# Configuración de base de datos (SQLite en memoria)
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_engine():
    """Motor SQLite en memoria con todas las tablas creadas."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def db_session_factory(db_engine):
    """Fábrica de sesiones vinculada al motor en memoria."""
    return sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine
    )


@pytest.fixture()
def db_dao(db_engine):
    """DAO de base de datos (SQLite) para inyección en módulos."""
    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    return dao


# ---------------------------------------------------------------------------
# Cliente HTTP de la API (usa la BD en memoria)
# ---------------------------------------------------------------------------

@pytest.fixture()
def api_client(db_engine):
    """Cliente HTTP de test con la BD en memoria inyectada."""
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from modulos.remitos_carnicos.remitos_carnicos import RemitosCarnicosModulo

    app = FastAPI(title="ROCCA Test")
    dao = SQLiteDAO("sqlite://")
    dao._engine = db_engine
    dao._session_factory = sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine
    )

    modulo = RemitosCarnicosModulo(dao)
    modulo.registrar(app)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return TestClient(app), dao
