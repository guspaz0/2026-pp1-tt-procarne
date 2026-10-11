"""Fixtures comunes para los tests de ROCCA.

Crea una base de datos SQLite en memoria para cada test,
de modo que no se afecte la BD de desarrollo.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Asegurar que el paquete `app` esté en el path (mismo shim que app/__init__.py)
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_APP_DIR = _BACKEND_DIR / "app"
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from configs.db import Base
from configs.dao import SQLiteDAO

# Importar todos los modelos para que Base.metadata los conozca
from modulos.remitos_carnicos.operador.dao import Operador
from modulos.remitos_carnicos.operador.categoria import Actividad, CategoriaAfip, CategoriaOperador
from modulos.remitos_carnicos.mercaderia.dao import Mercaderia
from modulos.remitos_carnicos.remito.dao import RemitoCarnico


@pytest.fixture()
def engine():
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
def session_factory(engine):
    """Fábrica de sesiones vinculada al motor en memoria."""
    return sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


@pytest.fixture()
def db_dao(engine):
    """DAO de base de datos para inyección en módulos."""
    dao = SQLiteDAO("sqlite://")
    dao._engine = engine
    dao._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return dao


@pytest.fixture()
def operador_dao(session_factory):
    """DAO de operadores."""
    from modulos.remitos_carnicos.operador.dao import OperadorDAO
    return OperadorDAO(session_factory)


@pytest.fixture()
def actividad_dao(session_factory):
    """DAO de actividades."""
    from modulos.remitos_carnicos.operador.categoria import ActividadDAO
    return ActividadDAO(session_factory)


@pytest.fixture()
def categoria_afip_dao(session_factory):
    """DAO de categorías AFIP."""
    from modulos.remitos_carnicos.operador.categoria import CategoriaAfipDAO
    return CategoriaAfipDAO(session_factory)


@pytest.fixture()
def categoria_operador_dao(session_factory):
    """DAO de categorías de operador."""
    from modulos.remitos_carnicos.operador.categoria import CategoriaOperadorDAO
    return CategoriaOperadorDAO(session_factory)


@pytest.fixture()
def mercaderia_dao(session_factory):
    """DAO de mercaderías."""
    from modulos.remitos_carnicos.mercaderia.dao import MercaderiaDAO
    return MercaderiaDAO(session_factory)


@pytest.fixture()
def seed_actividades(session_factory):
    """Carga actividades y categorías AFIP de referencia."""
    from sqlalchemy import select

    with session_factory() as session:
        bov = Actividad(id=1, nombre="Bovino/Bubalino")
        por = Actividad(id=2, nombre="Porcino")
        session.add_all([bov, por])
        session.commit()

        cats_bov = [
            CategoriaAfip(actividad_id=1, codigo="B1", descripcion="Productor/criador"),
            CategoriaAfip(actividad_id=1, codigo="B2", descripcion="Matarifes abastecedores y carniceros"),
            CategoriaAfip(actividad_id=1, codigo="B3", descripcion="Feed lots"),
            CategoriaAfip(actividad_id=1, codigo="B4", descripcion="Invernador"),
        ]
        cats_por = [
            CategoriaAfip(actividad_id=2, codigo="P1", descripcion="Productores/Criadores Comerciales"),
            CategoriaAfip(actividad_id=2, codigo="P2", descripcion="Invernadores"),
        ]
        session.add_all(cats_bov + cats_por)
        session.commit()

    return {"bovino": 1, "porcino": 2}


@pytest.fixture()
def seed_operador(session_factory, seed_actividades):
    """Crea un operador de prueba con categorías."""
    op = Operador(
        cuit="20123456789",
        razon_social="TEST OPERADOR S.A.",
        situacion="ACTIVO",
    )
    with session_factory() as session:
        session.add(op)
        session.commit()
        session.refresh(op)
        op_id = op.id

    # Agregar a actividad Bovino
    from modulos.remitos_carnicos.operador.dao import operador_actividades
    from sqlalchemy import insert

    with session_factory() as session:
        session.execute(
            insert(operador_actividades).values(cuit="20123456789", actividad_id=1)
        )
        session.commit()

    # Agregar categorías
    cat1 = CategoriaOperador(
        operador_id=op_id,
        actividad_id=1,
        categoria="Productor/criador",
        situacion="ACTIVO",
        desde_fecha="01/01/2024",
    )
    cat2 = CategoriaOperador(
        operador_id=op_id,
        actividad_id=1,
        categoria="Invernador",
        situacion="ACTIVO",
        desde_fecha="15/06/2023",
    )
    with session_factory() as session:
        session.add_all([cat1, cat2])
        session.commit()

    return {"cuit": "20123456789", "id": op_id}


@pytest.fixture()
def client(engine):
    """Cliente HTTP de test para la API."""
    from fastapi.testclient import TestClient
    from app.app import crear_app

    # Usar la BD en memoria
    app = crear_app(database_url="sqlite://")
    # Reemplazar el engine del DAO con el de test
    return TestClient(app)
