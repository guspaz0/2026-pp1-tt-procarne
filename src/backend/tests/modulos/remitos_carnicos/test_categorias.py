"""Tests del submódulo de categorías (actividad, categoría AFIP, situación)."""

from __future__ import annotations

import pytest

from modulos.remitos_carnicos.operador.categoria import (
    Actividad,
    ActividadDAO,
    CategoriaAfip,
    CategoriaAfipDAO,
    CategoriaOperador,
    CategoriaOperadorDAO,
    Situcion,
    SitucionDAO,
)
from modulos.remitos_carnicos.operador.dao import OperadorORM
from core.persona.dao import Persona


@pytest.fixture()
def situacion_dao(session_factory):
    """DAO de situaciones."""
    return SitucionDAO(session_factory)


@pytest.fixture()
def seed_situaciones(session_factory):
    """Crea situaciones de prueba."""
    with session_factory() as session:
        s1 = Situcion(descripcion="ACTIVO")
        s2 = Situcion(descripcion="INACTIVO")
        s3 = Situcion(descripcion="EXCLUIDO")
        session.add_all([s1, s2, s3])
        session.commit()
        session.refresh(s1)
        session.refresh(s2)
        session.refresh(s3)
    return {"ACTIVO": s1.id, "INACTIVO": s2.id, "EXCLUIDO": s3.id}


@pytest.fixture()
def seed_operador(session_factory):
    """Crea un operador de prueba y devuelve su id."""
    with session_factory() as session:
        persona = Persona(
            tipo="JURIDICA",
            tipo_documento="CUIT",
            identificador="30111111111",
            nombre="OPERADOR TEST S.A.",
        )
        session.add(persona)
        session.commit()
        session.refresh(persona)

        op = OperadorORM(persona_id=persona.id)
        session.add(op)
        session.commit()
        session.refresh(op)
        return op.id


class TestActividadDAO:
    """Tests del DAO de actividades."""

    def test_listar(self, actividad_dao, session_factory):
        with session_factory() as session:
            a1 = Actividad(nombre="Bovino/Bubalino")
            a2 = Actividad(nombre="Porcino")
            session.add_all([a1, a2])
            session.commit()

        actividades = actividad_dao.listar()
        assert len(actividades) == 2

    def test_obtener_por_id(self, actividad_dao, session_factory):
        with session_factory() as session:
            a = Actividad(nombre="Bovino/Bubalino")
            session.add(a)
            session.commit()
            session.refresh(a)
            id_a = a.id

        obtenida = actividad_dao.obtener_por_id(id_a)
        assert obtenida is not None
        assert obtenida.nombre == "Bovino/Bubalino"


class TestCategoriaAfipDAO:
    """Tests del DAO de categorías AFIP."""

    def test_listar(self, categoria_afip_dao, session_factory):
        with session_factory() as session:
            actividad = Actividad(nombre="Bovino/Bubalino")
            session.add(actividad)
            session.commit()
            session.refresh(actividad)

            c1 = CategoriaAfip(actividad_id=actividad.id, codigo="B1", descripcion="Productor/criador")
            c2 = CategoriaAfip(actividad_id=actividad.id, codigo="B6", descripcion="Frigorífico")
            session.add_all([c1, c2])
            session.commit()

        categorias = categoria_afip_dao.listar()
        assert len(categorias) == 2

    def test_listar_por_actividad(self, categoria_afip_dao, session_factory):
        with session_factory() as session:
            a1 = Actividad(nombre="Bovino/Bubalino")
            a2 = Actividad(nombre="Porcino")
            session.add_all([a1, a2])
            session.commit()
            session.refresh(a1)
            session.refresh(a2)

            c1 = CategoriaAfip(actividad_id=a1.id, codigo="B1", descripcion="Productor")
            c2 = CategoriaAfip(actividad_id=a2.id, codigo="P1", descripcion="Productor porcino")
            session.add_all([c1, c2])
            session.commit()

        categorias = categoria_afip_dao.listar(actividad_id=a1.id)
        assert len(categorias) == 1
        assert categorias[0].codigo == "B1"

    def test_obtener_por_codigo(self, categoria_afip_dao, session_factory):
        with session_factory() as session:
            actividad = Actividad(nombre="Bovino/Bubalino")
            session.add(actividad)
            session.commit()
            session.refresh(actividad)

            c = CategoriaAfip(actividad_id=actividad.id, codigo="B1", descripcion="Productor/criador")
            session.add(c)
            session.commit()

        obtenida = categoria_afip_dao.obtener_por_codigo("B1")
        assert obtenida is not None
        assert obtenida.descripcion == "Productor/criador"


class TestSitucionDAO:
    """Tests del DAO de situaciones."""

    def test_listar(self, situacion_dao, seed_situaciones):
        situaciones = situacion_dao.listar()
        assert len(situaciones) == 3

    def test_obtener_por_id(self, situacion_dao, seed_situaciones):
        obtenida = situacion_dao.obtener_por_id(seed_situaciones["ACTIVO"])
        assert obtenida is not None
        assert obtenida.descripcion == "ACTIVO"


class TestCategoriaOperadorDAO:
    """Tests del DAO de categorías de operador."""

    def test_crear(self, categoria_operador_dao, seed_categorias, seed_situaciones, seed_operador):
        categoria = categoria_operador_dao.crear(
            operador_id=seed_operador,
            categoria_id=seed_categorias["B1"],
            situacion_id=seed_situaciones["ACTIVO"],
        )
        assert categoria.id is not None
        assert categoria.operador_id == seed_operador

    def test_listar_por_operador(self, categoria_operador_dao, seed_categorias, seed_situaciones, seed_operador):
        categoria_operador_dao.crear(
            operador_id=seed_operador,
            categoria_id=seed_categorias["B1"],
            situacion_id=seed_situaciones["ACTIVO"],
        )
        categoria_operador_dao.crear(
            operador_id=seed_operador,
            categoria_id=seed_categorias["B6"],
            situacion_id=seed_situaciones["ACTIVO"],
        )

        categorias = categoria_operador_dao.listar_por_operador(seed_operador)
        assert len(categorias) == 2

    def test_listar_por_categoria(self, categoria_operador_dao, seed_categorias, seed_situaciones, seed_operador):
        categoria_operador_dao.crear(
            operador_id=seed_operador,
            categoria_id=seed_categorias["B1"],
            situacion_id=seed_situaciones["ACTIVO"],
        )

        categorias = categoria_operador_dao.listar_por_categoria("B1")
        assert len(categorias) == 1
