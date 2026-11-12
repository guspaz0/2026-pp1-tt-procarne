"""Tests de los casos de uso del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

import pytest

from modulos.registro_operadores.dao import OperadorDAO
from modulos.registro_operadores.enums import EstadoRegistral, TipoOperador
from modulos.registro_operadores.schema import (
    OperadorIn,
)
from modulos.registro_operadores.servicio import OperadorError, OperadorService


@pytest.fixture()
def operador_dao(db_session_factory):
    """DAO de operadores."""
    return OperadorDAO(db_session_factory)


@pytest.fixture()
def operador_service(operador_dao, persona_service, session_factory):
    """Servicio de operadores con sus servicios delegados inyectados."""
    from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
    from modulos.registro_operadores.requisito_inscripcion.servicio import RequisitoInscripcionService

    return OperadorService(
        operador_dao,
        persona_service=persona_service,
        requisito_service=RequisitoInscripcionService(RequisitoInscripcionDAO(session_factory)),
    )


def crear_rocca_operador_test(session, cuit: str, razon_social: str, tipo: str = "FRIGORIFICO") -> int:
    """Crea un operador de prueba y devuelve su id.

    ``operadores.persona_id`` es NOT NULL: se crea (o reutiliza) la persona
    titular con el CUIT del operador.
    """
    from core.persona.dao import Persona
    from modulos.registro_operadores.dao import Operador
    from datetime import datetime, timezone

    persona = (
        session.query(Persona)
        .filter(Persona.identificador == cuit)
        .first()
    )
    if persona is None:
        persona = Persona(
            tipo="JURIDICA",
            tipo_documento="CUIT",
            identificador=cuit,
            nombre=razon_social,
        )
        session.add(persona)
        session.flush()

    op = Operador(
        razon_social=razon_social,
        tipo=tipo,
        persona_id=persona.id,
        alta_fecha=datetime.now(timezone.utc),
    )
    session.add(op)
    session.commit()
    session.refresh(op)
    return op.id


class TestOperadorService:
    """Tests del servicio de operadores."""

    def test_crear_operador(self, operador_service):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.cuit == "30111111111"
        assert resultado.razon_social == "FRIGORIFICO TEST S.A."
        assert resultado.tipo == "FRIGORIFICO"
        assert resultado.estado_registral == "PENDIENTE"

    def test_crear_operador_misma_persona(self, operador_service):
        """Crear dos operadores con el mismo CUIT es válido: misma persona, dos sucursales."""
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        primero = operador_service.crear_operador(data)
        segundo = operador_service.crear_operador(data)
        # Mismo CUIT → misma persona, pero dos operadores distintos
        assert primero.id != segundo.id
        assert primero.persona_id == segundo.persona_id

    def test_obtener_por_cuit(self, operador_service):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        operador_service.crear_operador(data)
        resultado = operador_service.obtener_por_cuit("30111111111")
        assert resultado is not None
        assert resultado.razon_social == "FRIGORIFICO TEST S.A."

    def test_listar(self, operador_service):
        for i in range(3):
            operador_service.crear_operador(
                OperadorIn(
                    cuit=f"3011111111{i}",
                    razon_social=f"OPERADOR {i}",
                    tipo=TipoOperador.FRIGORIFICO.value,
                )
            )
        resultado = operador_service.listar()
        assert len(resultado) == 3

    def test_listar_filtrar_por_tipo(self, operador_service):
        operador_service.crear_operador(
            OperadorIn(cuit="30111111111", razon_social="FRIGORIFICO", tipo=TipoOperador.FRIGORIFICO.value)
        )
        operador_service.crear_operador(
            OperadorIn(cuit="30111111112", razon_social="CARNICERIA", tipo=TipoOperador.CARNICERIA.value)
        )
        resultado = operador_service.listar(tipo=TipoOperador.FRIGORIFICO.value)
        assert len(resultado) == 1
        assert resultado[0].tipo == "FRIGORIFICO"

    def test_cambiar_estado(self, operador_service):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)
        resultado = operador_service.cambiar_estado(creado.id, EstadoRegistral.SUSPENDIDO)
        assert resultado.estado_registral == "SUSPENDIDO"


