"""Configuración de base de datos de ROCCA.

Define la clase base declarativa de SQLAlchemy y los helpers para crear
el motor y la fábrica de sesiones.

Uso::

    from configs.db import Base, crear_engine, crear_session_factory
"""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM de ROCCA."""


def crear_engine(database_url: str, echo: bool = False):
    """Crea un motor SQLAlchemy para la URL dada.

    Para SQLite en memoria se usa ``StaticPool`` para que todas las
    conexiones compartan la misma base de datos.
    """
    kwargs: dict = {"echo": echo}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if database_url in ("sqlite://", "sqlite:///:memory:"):
            from sqlalchemy.pool import StaticPool

            kwargs["poolclass"] = StaticPool
    return create_engine(database_url, **kwargs)


def crear_session_factory(engine) -> sessionmaker[Session]:
    """Crea la fábrica de sesiones vinculada a un motor."""
    return sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
    )


@contextmanager
def sesion_de(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Context manager que abre y cierra una sesión de base de datos."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
