"""Configuración compartida de ROCCA (base de datos y DAOs)."""

from .dao import (
    DATABASE_URL,
    DatabaseDAO,
    PostgreSQLDAO,
    SQLiteDAO,
    crear_dao,
)
from .db import Base, crear_engine, crear_session_factory, sesion_de

__all__ = [
    "DATABASE_URL",
    "Base",
    "DatabaseDAO",
    "PostgreSQLDAO",
    "SQLiteDAO",
    "crear_dao",
    "crear_engine",
    "crear_session_factory",
    "sesion_de",
]
