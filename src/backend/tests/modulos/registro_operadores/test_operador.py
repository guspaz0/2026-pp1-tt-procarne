"""Tests de los casos de uso del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

import pytest

from modulos.registro_operadores.dao import ROCCAOperadorDAO
from modulos.registro_operadores.enums import EstadoRegistral, TipoOperador
from modulos.registro_operadores.schema import (
    DomicilioOperativoIn,
    HabilitacionIn,
    InscripcionIn,
    ROCCAOperadorIn,
)
from modulos.registro_operadores.servicio import ROCCAOperadorError, ROCCAOperadorService


@pytest.fixture()
def operador_dao(db_session_factory):
    """DAO de operadores."""
    return ROCCAOperadorDAO(db_session_factory)


@pytest.fixture()
def operador_service(operador_dao):
    """Servicio de operadores."""
    return ROCCAOperadorService(operador_dao)


def crear_rocca_operador_test(session, cuit: str, razon_social: str, tipo: str = "FRIGORIFICO") -> int:
    """Crea un operador de prueba y devuelve su id."""
    from modulos.registro_operadores.dao import ROCCAOperador
    from datetime import datetime, timezone

    op = ROCCAOperador(
        cuit=cuit,
        razon_social=razon_social,
        tipo=tipo,
        alta_fecha=datetime.now(timezone.utc),
    )
    session.add(op)
    session.commit()
    session.refresh(op)
    return op.id


class TestROCCAOperadorService:
    """Tests del servicio de operadores."""

    def test_crear_operador(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.cuit == "30111111111"
        assert resultado.razon_social == "FRIGORIFICO TEST S.A."
        assert resultado.tipo == "FRIGORIFICO"
        assert resultado.estado_registral == "ACTIVO"

    def test_crear_operador_duplicado(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        operador_service.crear_operador(data)
        with pytest.raises(ROCCAOperadorError):
            operador_service.crear_operador(data)

    def test_obtener_por_cuit(self, operador_service):
        data = ROCCAOperadorIn(
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
                ROCCAOperadorIn(
                    cuit=f"3011111111{i}",
                    razon_social=f"OPERADOR {i}",
                    tipo=TipoOperador.FRIGORIFICO.value,
                )
            )
        resultado = operador_service.listar()
        assert len(resultado) == 3

    def test_listar_filtrar_por_tipo(self, operador_service):
        operador_service.crear_operador(
            ROCCAOperadorIn(cuit="30111111111", razon_social="FRIGORIFICO", tipo=TipoOperador.FRIGORIFICO.value)
        )
        operador_service.crear_operador(
            ROCCAOperadorIn(cuit="30111111112", razon_social="CARNICERIA", tipo=TipoOperador.CARNICERIA.value)
        )
        resultado = operador_service.listar(tipo=TipoOperador.FRIGORIFICO.value)
        assert len(resultado) == 1
        assert resultado[0].tipo == "FRIGORIFICO"

    def test_cambiar_estado(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)
        resultado = operador_service.cambiar_estado(creado.id, EstadoRegistral.SUSPENDIDO)
        assert resultado.estado_registral == "SUSPENDIDO"

    def test_agregar_habilitacion(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)
        habilitacion = operador_service.agregar_habilitacion(
            creado.id,
            HabilitacionIn(actividad="FAENA BOVINA"),
        )
        assert habilitacion.actividad == "FAENA BOVINA"
        assert habilitacion.estado == "ACTIVO"

    def test_agregar_inscripcion(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)
        inscripcion = operador_service.agregar_inscripcion(
            creado.id,
            InscripcionIn(tipo="PRINCIPAL", numero_inscripcion="ROCCA-001"),
        )
        assert inscripcion.tipo == "PRINCIPAL"
        assert inscripcion.numero_inscripcion == "ROCCA-001"

    def test_agregar_domicilio_operativo(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)
        domicilio = operador_service.agregar_domicilio_operativo(
            creado.id,
            DomicilioOperativoIn(
                direccion="Av. Siempreviva 742",
                localidad="Springfield",
                provincia="BA",
                es_principal=True,
            ),
        )
        assert domicilio.direccion == "Av. Siempreviva 742"
        assert domicilio.es_principal is True
