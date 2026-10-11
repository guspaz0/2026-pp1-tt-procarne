"""Data Access Objects (DAO) para cada motor de base de datos.

Aplica **Dependency Inversion**: los módulos de negocio dependen de la
interfaz abstracta :class:`DatabaseDAO`, no de una implementación concreta.

- :class:`SQLiteDAO` — para SQLite (dev)
- :class:`PostgreSQLDAO` — para PostgreSQL (producción)

El DAO encapsula la creación del motor, la sesión y las operaciones de
ciclo de vida (crear tablas, cerrar conexiones).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from .db import Base, DATABASE_URL


class DatabaseDAO(ABC):
    """Interfaz abstracta de acceso a la base de datos.

    Cada implementación concreta encapsula la configuración del motor
    y la sesión para un motor específico.
    """

    @abstractmethod
    def __init__(self, url: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def crear_tablas(self) -> None:
        """Crea todas las tablas definidas en :class:`Base`."""
        raise NotImplementedError

    @abstractmethod
    def obtener_sesion(self) -> Session:
        """Devuelve una nueva sesión transaccional."""
        raise NotImplementedError

    @abstractmethod
    def cerrar(self) -> None:
        """Cierra el motor y libera recursos."""
        raise NotImplementedError


class SQLiteDAO(DatabaseDAO):
    """DAO para SQLite (desarrollo)."""

    def __init__(self, url: Optional[str] = None) -> None:
        self._url = url or "sqlite:///./rocca.db"
        self._engine: Engine = create_engine(
            self._url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False, bind=self._engine
        )

    def crear_tablas(self) -> None:
        Base.metadata.create_all(bind=self._engine)

    def obtener_sesion(self) -> Session:
        return self._session_factory()

    def cerrar(self) -> None:
        self._engine.dispose()


class PostgreSQLDAO(DatabaseDAO):
    """DAO para PostgreSQL (producción)."""

    def __init__(self, url: Optional[str] = None) -> None:
        if url is None:
            import os

            url = os.environ.get(
                "ROCCA_DATABASE_URL",
                "postgresql+psycopg2://rocca:rocca@localhost:5432/rocca",
            )
        self._url = url
        self._engine: Engine = create_engine(self._url, echo=False)
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False, bind=self._engine
        )

    def crear_tablas(self) -> None:
        Base.metadata.create_all(bind=self._engine)

    def obtener_sesion(self) -> Session:
        return self._session_factory()

    def cerrar(self) -> None:
        self._engine.dispose()


def crear_dao(url: str) -> DatabaseDAO:
    """Fábrica: crea el DAO apropiado según el esquema de la URL."""
    if url.startswith("sqlite"):
        return SQLiteDAO(url)
    return PostgreSQLDAO(url)
