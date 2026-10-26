"""Tests del submódulo de operador (cadena cárnica)."""

from __future__ import annotations

import pytest

from modulos.remitos_carnicos.operador.dao import Operador, OperadorDAO
from modulos.remitos_carnicos.operador.schema import OperadorIn, OperadorOut
from modulos.remitos_carnicos.operador.servicio import OperadorError, OperadorService
from core.persona.dao import Persona


@pytest.fixture()
def operador_service(operador_dao):
    return OperadorService(operador_dao)


@pytest.fixture()
def seed_persona(session_factory):
    """Crea una persona jurídica de prueba y devuelve su id."""
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
        return persona.id


class TestOperadorDAO:
    """Tests del DAO de operadores."""

    def test_crear(self, operador_dao, seed_persona):
        op = operador_dao.crear(persona_id=seed_persona)
        assert op.id is not None
        assert op.persona_id == seed_persona

    def test_obtener_por_id(self, operador_dao, seed_persona):
        op = operador_dao.crear(persona_id=seed_persona)
        obtenido = operador_dao.obtener_por_id(op.id)
        assert obtenido is not None
        assert obtenido.id == op.id

    def test_obtener_por_persona(self, operador_dao, seed_persona):
        op = operador_dao.crear(persona_id=seed_persona)
        obtenido = operador_dao.obtener_por_persona(seed_persona)
        assert obtenido is not None
        assert obtenido.id == op.id

    def test_listar(self, operador_dao, session_factory):
        # Crear dos personas
        with session_factory() as session:
            p1 = Persona(tipo="JURIDICA", tipo_documento="CUIT", identificador="30111111111", nombre="OP1")
            p2 = Persona(tipo="JURIDICA", tipo_documento="CUIT", identificador="30222222222", nombre="OP2")
            session.add_all([p1, p2])
            session.commit()
            session.refresh(p1)
            session.refresh(p2)

        operador_dao.crear(persona_id=p1.id)
        operador_dao.crear(persona_id=p2.id)

        operadores = operador_dao.listar()
        assert len(operadores) == 2


class TestOperadorService:
    """Tests del servicio de operadores."""

    def test_crear_operador(self, operador_service, seed_persona):
        data = OperadorIn(persona_id=seed_persona)
        resultado = operador_service.crear_operador(data)
        assert resultado.id is not None
        assert resultado.persona_id == seed_persona

    def test_crear_operador_duplicado(self, operador_service, seed_persona):
        data = OperadorIn(persona_id=seed_persona)
        operador_service.crear_operador(data)
        with pytest.raises(OperadorError):
            operador_service.crear_operador(data)

    def test_obtener_por_id(self, operador_service, seed_persona):
        data = OperadorIn(persona_id=seed_persona)
        creado = operador_service.crear_operador(data)
        obtenido = operador_service.obtener_por_id(creado.id)
        assert obtenido is not None
        assert obtenido.id == creado.id

    def test_listar(self, operador_service, session_factory):
        # Crear dos personas
        with session_factory() as session:
            p1 = Persona(tipo="JURIDICA", tipo_documento="CUIT", identificador="30111111111", nombre="OP1")
            p2 = Persona(tipo="JURIDICA", tipo_documento="CUIT", identificador="30222222222", nombre="OP2")
            session.add_all([p1, p2])
            session.commit()
            session.refresh(p1)
            session.refresh(p2)

        operador_service.crear_operador(OperadorIn(persona_id=p1.id))
        operador_service.crear_operador(OperadorIn(persona_id=p2.id))

        operadores = operador_service.listar()
        assert len(operadores) == 2
