"""Configuración de la aplicación: base de datos y DAO."""

from .db import Base, DATABASE_URL, get_db, init_db
from .dao import DatabaseDAO, SQLiteDAO, PostgreSQLDAO, crear_dao

__all__ = [
    "Base",
    "DATABASE_URL",
    "get_db",
    "init_db",
    "DatabaseDAO",
    "SQLiteDAO",
    "PostgreSQLDAO",
    "crear_dao",
]
