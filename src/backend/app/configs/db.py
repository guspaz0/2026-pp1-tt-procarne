"""Configuración de la base de datos.

Define la :class:`Base` declarativa, el motor de conexión y la sesión.
El motor se selecciona según la URL de la base de datos (SQLite en dev,
PostgreSQL en producción).
"""

from __future__ import annotations

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# URL de la base de datos. En dev: SQLite; en prod: PostgreSQL.
# Ej: postgresql+psycopg2://rocca:rocca@localhost:5432/rocca
DATABASE_URL: str = os.environ.get(
    "ROCCA_DATABASE_URL",
    "sqlite:///./rocca.db",
)

# ``connect_args`` solo aplica a SQLite; en PostgreSQL no se usa.
_connect_args: dict = (
    {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=_connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base declarativa para todas las entidades ORM."""


def get_db():
    """Dependencia de FastAPI para obtener una sesión transaccional."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea todas las tablas (solo en dev; en producción usar Alembic)."""
    Base.metadata.create_all(bind=engine)
