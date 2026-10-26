"""Capa de acceso a datos (DAO) de base de datos de ROCCA.

Abstrahe el driver concreto (SQLite para desarrollo/tests, PostgreSQL
para producción) detrás de una interfaz única.

Uso::

    from configs.dao import crear_dao
    db_dao = crear_dao()
    with db_dao.obtener_sesion() as session:
        ...
"""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from configs.db import Base

# URL de la base de datos: se toma de la variable de entorno
# ``ROCCA_DATABASE_URL`` o se usa SQLite local por defecto.
DATABASE_URL = os.environ.get("ROCCA_DATABASE_URL", "sqlite:///./rocca.db")


class DatabaseDAO:
    """DAO de base de datos genérico.

    Encapsula el motor y la fábrica de sesiones. Expone
    ``obtener_sesion()`` como contexto manager para que los servicios
    de negocio no dependan de SQLAlchemy directamente.
    """

    def __init__(self, database_url: str | None = None) -> None:
        self._database_url = database_url or DATABASE_URL
        self._engine = self._crear_engine()
        self._session_factory = self._crear_session_factory()

    def _crear_engine(self):
        """Crea el motor según el tipo de base de datos."""
        kwargs: dict = {}
        if self._database_url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
            if self._database_url in ("sqlite://", "sqlite:///:memory:"):
                kwargs["poolclass"] = StaticPool
        return create_engine(self._database_url, **kwargs)

    def _crear_session_factory(self) -> sessionmaker[Session]:
        """Crea la fábrica de sesiones vinculada al motor."""
        return sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False,
            bind=self._engine,
        )

    @contextmanager
    def obtener_sesion(self) -> Generator[Session, None, None]:
        """Abre una sesión transaccional (commit/rollback automático)."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def crear_tablas(self) -> None:
        """Crea todas las tablas definidas en ``Base.metadata``."""
        Base.metadata.create_all(bind=self._engine)

    @property
    def engine(self):
        """Motor SQLAlchemy (útil para tests y Alembic)."""
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        """Fábrica de sesiones (útil para tests y DAOs de entidad)."""
        return self._session_factory


# ---------------------------------------------------------------------------
# DAOs concretos por driver
# ---------------------------------------------------------------------------

class SQLiteDAO(DatabaseDAO):
    """DAO para SQLite (desarrollo y tests)."""


class PostgreSQLDAO(DatabaseDAO):
    """DAO para PostgreSQL (producción)."""

    def __init__(self, database_url: str | None = None) -> None:
        super().__init__(
            database_url or os.environ.get(
                "ROCCA_DATABASE_URL", "postgresql+psycopg://rocca:rocca@localhost/rocca"
            )
        )


def crear_dao(database_url: str | None = None) -> DatabaseDAO:
    """Factory: crea el DAO adecuado según la URL de la base de datos."""
    url = database_url or DATABASE_URL
    if url.startswith("sqlite"):
        return SQLiteDAO(url)
    return PostgreSQLDAO(url)
