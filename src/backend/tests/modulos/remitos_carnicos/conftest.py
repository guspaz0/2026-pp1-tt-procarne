"""Fixtures comunes para los tests de ROCCA.

Crea una base de datos SQLite en memoria para cada test,
de modo que no se afecte la BD de desarrollo.

Las fixtures de configuración de BD se reutilizan desde
:mod:`tests.fixtures`.
"""

from __future__ import annotations

import pytest
from sqlalchemy import insert

# Reutilizar fixtures de configuración compartidas
from tests.fixtures import db_engine, db_session_factory, db_dao  # noqa: F401

# Importar todos los modelos para que Base.metadata los conozca
from modulos.genericos.persona.dao import Persona
from modulos.genericos.mercaderia.dao import Mercaderia, MercaderiaDAO
from modulos.remitos_carnicos.operador.dao import Operador, OperadorDAO, operador_actividades
from modulos.remitos_carnicos.operador.categoria import (
    Actividad,
    ActividadDAO,
    CategoriaAfip,
    CategoriaAfipDAO,
    CategoriaOperador,
    CategoriaOperadorDAO,
)
from modulos.remitos_carnicos.remito.dao import RemitoCarnico, RemitoCarnicoDAO


# ---------------------------------------------------------------------------
# Aliases para compatibilidad (engine / session_factory)
# ---------------------------------------------------------------------------

@pytest.fixture()
def engine(db_engine):
    """Alias de :func:`db_engine` para compatibilidad."""
    return db_engine


@pytest.fixture()
def session_factory(db_session_factory):
    """Alias de :func:`db_session_factory` para compatibilidad."""
    return db_session_factory


# ---------------------------------------------------------------------------
# DAOs por entidad
# ---------------------------------------------------------------------------

@pytest.fixture()
def operador_dao(session_factory):
    """DAO de operadores."""
    return OperadorDAO(session_factory)


@pytest.fixture()
def actividad_dao(session_factory):
    """DAO de actividades."""
    return ActividadDAO(session_factory)


@pytest.fixture()
def categoria_afip_dao(session_factory):
    """DAO de categorías AFIP."""
    return CategoriaAfipDAO(session_factory)


@pytest.fixture()
def categoria_operador_dao(session_factory):
    """DAO de categorías de operador."""
    return CategoriaOperadorDAO(session_factory)


@pytest.fixture()
def mercaderia_dao(session_factory):
    """DAO de mercaderías."""
    return MercaderiaDAO(session_factory)


@pytest.fixture()
def remito_dao(session_factory):
    """DAO de remitos cárnicos."""
    return RemitoCarnicoDAO(session_factory)


# ---------------------------------------------------------------------------
# Seeds
# ---------------------------------------------------------------------------

def _crear_persona_juridica(session, cuit: str, nombre: str) -> Persona:
    """Crea una persona jurídica y la devuelve."""
    persona = Persona(
        tipo="PJ",
        identificador=cuit,
        nombre=nombre,
        cuit=cuit,
    )
    session.add(persona)
    session.commit()
    session.refresh(persona)
    return persona


def _crear_operador(session, persona_id: int) -> Operador:
    """Crea un operador referenciando a una persona."""
    op = Operador(
        persona_id=persona_id,
    )
    session.add(op)
    session.commit()
    session.refresh(op)
    return op


def crear_operador_test(session, cuit: str, razon_social: str) -> Operador:
    """Crea una persona jurídica y un operador asociado (helper para tests)."""
    persona = _crear_persona_juridica(session, cuit, razon_social)
    return _crear_operador(session, persona.id)


def obtener_operador_id_por_cuit(session, cuit: str) -> int:
    """Obtiene el id del operador a partir del CUIT (helper para tests)."""
    from sqlalchemy import select
    from modulos.genericos.persona.dao import Persona

    stmt = (
        select(Operador.id)
        .join(Operador.persona)
        .where(Persona.identificador == cuit)
    )
    return session.execute(stmt).scalar_one()


@pytest.fixture()
def seed_actividades(session_factory):
    """Carga actividades y categorías AFIP de referencia."""
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
    with session_factory() as session:
        persona = _crear_persona_juridica(session, "20123456789", "TEST OPERADOR S.A.")
        op = _crear_operador(session, persona.id)
        op_id = op.id

    # Agregar a actividad Bovino
    with session_factory() as session:
        session.execute(
            insert(operador_actividades).values(operador_id=op_id, actividad_id=1)
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
def seed_operadores(session_factory):
    """Crea operadores de prueba: titular, transportista, depositario, destinatario."""
    with session_factory() as session:
        p_titular = _crear_persona_juridica(session, "20111111111", "TITULAR TEST S.A.")
        p_transportista = _crear_persona_juridica(session, "20222222222", "TRANSPORTISTA TEST")
        p_depositario = _crear_persona_juridica(session, "20333333333", "DEPOSITARIO TEST")
        p_destinatario = _crear_persona_juridica(session, "20444444444", "DESTINATARIO TEST")

        op_titular = _crear_operador(session, p_titular.id)
        op_transportista = _crear_operador(session, p_transportista.id)
        op_depositario = _crear_operador(session, p_depositario.id)
        op_destinatario = _crear_operador(session, p_destinatario.id)

    return {
        "titular": "20111111111",
        "transportista": "20222222222",
        "depositario": "20333333333",
        "destinatario": "20444444444",
    }


@pytest.fixture()
def seed_mercaderias(session_factory):
    """Crea mercaderías de prueba (catálogo genérico)."""
    mercs = [
        Mercaderia(
            codigo="1101",
            descripcion="Carne de bovino fresca",
            requiere_trazabilidad=True,
            requiere_numero_tropa=True,
        ),
        Mercaderia(
            codigo="1102",
            descripcion="Carne de bovino congelada",
            requiere_trazabilidad=True,
            requiere_numero_tropa=False,
        ),
        Mercaderia(
            codigo="2101",
            descripcion="Carne de porcino fresca",
            requiere_trazabilidad=True,
            requiere_numero_tropa=True,
        ),
    ]
    with session_factory() as session:
        for m in mercs:
            session.add(m)
        session.commit()
    return [m.codigo for m in mercs]
