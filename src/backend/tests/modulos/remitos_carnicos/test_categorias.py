"""Tests del submódulo de categorías (actividades y categorías AFIP)."""

from __future__ import annotations

import pytest


class TestActividadDAO:
    """Tests del DAO de actividades."""

    def test_listar(self, actividad_dao, seed_actividades):
        actividades = actividad_dao.listar()
        assert len(actividades) == 2
        nombres = {a.nombre for a in actividades}
        assert "Bovino/Bubalino" in nombres
        assert "Porcino" in nombres

    def test_obtener_por_id(self, actividad_dao, seed_actividades):
        act = actividad_dao.obtener_por_id(1)
        assert act is not None
        assert act.nombre == "Bovino/Bubalino"

    def test_obtener_por_nombre(self, actividad_dao, seed_actividades):
        act = actividad_dao.obtener_por_nombre("Porcino")
        assert act is not None
        assert act.id == 2

    def test_obtener_por_nombre_no_existe(self, actividad_dao, seed_actividades):
        act = actividad_dao.obtener_por_nombre("Ovino")
        assert act is None

    def test_guardar(self, actividad_dao, seed_actividades):
        from modulos.remitos_carnicos.operador.categoria import Actividad

        nueva = Actividad(nombre="Ovino")
        guardada = actividad_dao.guardar(nueva)
        assert guardada.id is not None
        assert guardada.nombre == "Ovino"


class TestCategoriaAfipDAO:
    """Tests del DAO de categorías AFIP (catálogo)."""

    def test_listar_por_actividad_bovino(self, categoria_afip_dao, seed_actividades):
        cats = categoria_afip_dao.listar_por_actividad(1)
        assert len(cats) == 4
        codigos = {c.codigo for c in cats}
        assert codigos == {"B1", "B2", "B3", "B4"}

    def test_listar_por_actividad_porcino(self, categoria_afip_dao, seed_actividades):
        cats = categoria_afip_dao.listar_por_actividad(2)
        assert len(cats) == 2
        codigos = {c.codigo for c in cats}
        assert codigos == {"P1", "P2"}

    def test_obtener_por_codigo(self, categoria_afip_dao, seed_actividades):
        cat = categoria_afip_dao.obtener_por_codigo(1, "B1")
        assert cat is not None
        assert cat.descripcion == "Productor/criador"

    def test_obtener_por_codigo_no_existe(self, categoria_afip_dao, seed_actividades):
        cat = categoria_afip_dao.obtener_por_codigo(1, "P1")
        assert cat is None

    def test_listar_todas(self, categoria_afip_dao, seed_actividades):
        cats = categoria_afip_dao.listar()
        assert len(cats) == 6


class TestCategoriaOperadorDAO:
    """Tests del DAO de categorías de operador (inscripciones)."""

    def test_listar_por_operador(self, categoria_operador_dao, seed_operador):
        cats = categoria_operador_dao.listar_por_operador(seed_operador["id"])
        assert len(cats) == 2

    def test_listar_activas_por_operador(self, categoria_operador_dao, seed_operador):
        cats = categoria_operador_dao.listar_activas_por_operador(seed_operador["id"])
        assert len(cats) == 2
        assert all(c.situacion == "ACTIVO" for c in cats)

    def test_listar_por_operador_y_actividad(self, categoria_operador_dao, seed_operador):
        cats = categoria_operador_dao.listar_por_operador_y_actividad(
            seed_operador["id"], actividad_id=1
        )
        assert len(cats) == 2

    def test_listar_por_operador_y_actividad_vacia(self, categoria_operador_dao, seed_operador):
        cats = categoria_operador_dao.listar_por_operador_y_actividad(
            seed_operador["id"], actividad_id=2
        )
        assert len(cats) == 0

    def test_listar_por_categoria(self, categoria_operador_dao, seed_operador):
        cats = categoria_operador_dao.listar_por_categoria("Productor/criador")
        assert len(cats) == 1
        assert cats[0].operador_id == seed_operador["id"]

    def test_guardar(self, categoria_operador_dao, seed_operador):
        from modulos.remitos_carnicos.operador.categoria import CategoriaOperador

        nueva = CategoriaOperador(
            operador_id=seed_operador["id"],
            actividad_id=1,
            categoria="Feed lots",
            situacion="ACTIVO",
            desde_fecha="01/03/2025",
        )
        guardada = categoria_operador_dao.guardar(nueva)
        assert guardada.id is not None
        assert guardada.categoria == "Feed lots"

    def test_eliminar_por_operador(self, categoria_operador_dao, seed_operador):
        eliminadas = categoria_operador_dao.eliminar_por_operador(seed_operador["id"])
        assert eliminadas == 2

        cats = categoria_operador_dao.listar_por_operador(seed_operador["id"])
        assert len(cats) == 0


class TestRelaciones:
    """Tests de las relaciones entre entidades."""

    def test_operador_categorias(self, session_factory, seed_operador):
        from modulos.remitos_carnicos.operador.dao import Operador, _eager_options
        from modulos.genericos.persona.dao import Persona
        from sqlalchemy import select

        with session_factory() as session:
            op = session.execute(
                select(Operador)
                .join(Operador.persona)
                .where(Persona.identificador == "20123456789")
                .options(*_eager_options())
            ).unique().scalar_one()

            assert len(op.categorias) == 2
            assert all(c.operador_id == op.id for c in op.categorias)

    def test_operador_actividades(self, session_factory, seed_operador):
        from modulos.remitos_carnicos.operador.dao import Operador, _eager_options
        from modulos.genericos.persona.dao import Persona
        from sqlalchemy import select

        with session_factory() as session:
            op = session.execute(
                select(Operador)
                .join(Operador.persona)
                .where(Persona.identificador == "20123456789")
                .options(*_eager_options())
            ).unique().scalar_one()

            assert len(op.actividades) == 1
            assert op.actividades[0].nombre == "Bovino/Bubalino"

    def test_actividad_categorias_afip(self, session_factory, seed_actividades):
        from modulos.remitos_carnicos.operador.categoria import Actividad
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        with session_factory() as session:
            act = session.execute(
                select(Actividad)
                .where(Actividad.id == 1)
                .options(selectinload(Actividad.categorias_afip))
            ).scalar_one()

            assert len(act.categorias_afip) == 4

    def test_operador_en_ambas_actividades(self, session_factory, seed_operador, seed_actividades):
        """Un operador puede pertenecer a ambas actividades."""
        from modulos.remitos_carnicos.operador.dao import Operador, _eager_options, operador_actividades
        from modulos.remitos_carnicos.operador.categoria import CategoriaOperador
        from sqlalchemy import select, insert

        op_id = seed_operador["id"]

        # Agregar a actividad Porcino
        with session_factory() as session:
            session.execute(
                insert(operador_actividades).values(operador_id=op_id, actividad_id=2)
            )
            cat_por = CategoriaOperador(
                operador_id=op_id,
                actividad_id=2,
                categoria="Productores/Criadores Comerciales",
                situacion="ACTIVO",
                desde_fecha="01/01/2025",
            )
            session.add(cat_por)
            session.commit()

        # Verificar
        with session_factory() as session:
            op = session.execute(
                select(Operador).where(Operador.id == op_id).options(*_eager_options())
            ).unique().scalar_one()

            assert len(op.actividades) == 2
            nombres = {a.nombre for a in op.actividades}
            assert nombres == {"Bovino/Bubalino", "Porcino"}
            assert len(op.categorias) == 3
