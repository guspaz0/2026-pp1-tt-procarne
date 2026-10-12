"""Tests del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import insert

from modulos.genericos.persona.dao import Persona
from modulos.registro_operadores.dao import (
    DomicilioOperativo,
    Habilitacion,
    Inscripcion,
    ROCCAOperador,
    ROCCAOperadorDAO,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _crear_persona_juridica(session, cuit: str, nombre: str) -> Persona:
    persona = Persona(tipo="PJ", identificador=cuit, nombre=nombre, cuit=cuit)
    session.add(persona)
    session.commit()
    session.refresh(persona)
    return persona


def crear_rocca_operador_test(
    session,
    cuit: str,
    razon_social: str,
    tipo: str = "FRIGORIFICO",
    estado: str = "ACTIVO",
) -> ROCCAOperador:
    persona = _crear_persona_juridica(session, cuit, razon_social)
    op = ROCCAOperador(
        persona_id=persona.id,
        tipo=tipo,
        estado_registral=estado,
        fecha_inscripcion=date(2026, 1, 15),
    )
    session.add(op)
    session.commit()
    session.refresh(op)
    return op


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rocca_operador_dao(session_factory):
    return ROCCAOperadorDAO(session_factory)


@pytest.fixture()
def seed_rocca_operador(session_factory):
    """Crea un operador de prueba con habilitación, inscripción y domicilio."""
    with session_factory() as session:
        op = crear_rocca_operador_test(
            session, "30111111111", "FRIGORIFICO TEST S.A.", tipo="FRIGORIFICO"
        )
        op_id = op.id

        session.add(
            Habilitacion(
                operador_id=op_id,
                tipo="Sanitaria",
                numero="HAB-001",
                autoridad="ProCarne Fiscalización",
                fecha_emision=date(2026, 1, 15),
                estado="VIGENTE",
            )
        )
        session.add(
            Inscripcion(
                operador_id=op_id,
                tipo="NACIONAL",
                organismo="RFOCB",
                numero="RFOCB-12345",
                fecha_inscripcion=date(2025, 12, 1),
                estado="ACTIVA",
            )
        )
        session.add(
            DomicilioOperativo(
                operador_id=op_id,
                tipo="PRINCIPAL",
                calle="Av. San Martín",
                numero="1234",
                localidad="La Banda",
                departamento="Vergara",
                provincia="Santiago del Estero",
                codigo_postal="4400",
            )
        )
        session.commit()

    return {"cuit": "30111111111", "id": op_id}


# ---------------------------------------------------------------------------
# Tests del DAO
# ---------------------------------------------------------------------------


class TestROCCAOperadorDAO:
    def test_crear_operador(self, rocca_operador_dao, session_factory):
        with session_factory() as session:
            op = crear_rocca_operador_test(
                session, "30222222222", "CARNICERIA PRUEBA", tipo="CARNICERIA"
            )
            op_id = op.id

        guardado = rocca_operador_dao.obtener_por_id(op_id)
        assert guardado is not None
        assert guardado.cuit == "30222222222"
        assert guardado.razon_social == "CARNICERIA PRUEBA"
        assert guardado.tipo == "CARNICERIA"
        assert guardado.estado_registral == "ACTIVO"

    def test_obtener_por_cuit(self, rocca_operador_dao, seed_rocca_operador):
        op = rocca_operador_dao.obtener_por_cuit("30111111111")
        assert op is not None
        assert op.razon_social == "FRIGORIFICO TEST S.A."

    def test_obtener_por_cuit_no_existe(self, rocca_operador_dao):
        assert rocca_operador_dao.obtener_por_cuit("99999999999") is None

    def test_listar(self, rocca_operador_dao, session_factory, seed_rocca_operador):
        with session_factory() as session:
            crear_rocca_operador_test(session, "30333333333", "MATADERO PRUEBA", tipo="MATADERO")

        ops = rocca_operador_dao.listar()
        assert len(ops) == 2  # seed + matadero
        assert {o.cuit for o in ops} == {"30111111111", "30333333333"}

    def test_listar_filtrar_por_tipo(self, rocca_operador_dao, session_factory):
        with session_factory() as session:
            crear_rocca_operador_test(session, "30333333333", "CARNICERIA PRUEBA", tipo="CARNICERIA")

        ops = rocca_operador_dao.listar(tipo="CARNICERIA")
        assert len(ops) == 1
        assert ops[0].cuit == "30333333333"

    def test_listar_filtrar_por_estado(self, rocca_operador_dao, session_factory, seed_rocca_operador):
        with session_factory() as session:
            crear_rocca_operador_test(
                session, "30444444444", "DISTRIBUIDOR SUSPENDIDO", tipo="DISTRIBUIDOR", estado="SUSPENDIDO"
            )

        activos = rocca_operador_dao.listar(estado_registral="ACTIVO")
        assert {o.cuit for o in activos} == {"30111111111"}
        suspendidos = rocca_operador_dao.listar(estado_registral="SUSPENDIDO")
        assert {o.cuit for o in suspendidos} == {"30444444444"}

    def test_listar_paginado(self, rocca_operador_dao, session_factory, seed_rocca_operador):
        with session_factory() as session:
            for i in range(5):
                crear_rocca_operador_test(
                    session, f"3055555555{i}", f"OPERADOR PAG {i}", tipo="ABASTECEDOR"
                )

        ops = rocca_operador_dao.listar(limite=3, offset=0)
        assert len(ops) == 3
        ops = rocca_operador_dao.listar(limite=3, offset=3)
        assert len(ops) == 3

    def test_operador_con_habilitaciones_inscripciones_domicilios(
        self, rocca_operador_dao, seed_rocca_operador
    ):
        op = rocca_operador_dao.obtener_por_cuit("30111111111")
        assert len(op.habilitaciones) == 1
        assert op.habilitaciones[0].tipo == "Sanitaria"
        assert len(op.inscripciones) == 1
        assert op.inscripciones[0].organismo == "RFOCB"
        assert len(op.domicilios) == 1
        assert op.domicilios[0].localidad == "La Banda"

    def test_actualizar_estado(self, rocca_operador_dao, seed_rocca_operador):
        op = rocca_operador_dao.obtener_por_cuit("30111111111")
        op.estado_registral = "BAJADO"
        actualizado = rocca_operador_dao.actualizar(op)
        assert actualizado.estado_registral == "BAJADO"


# ---------------------------------------------------------------------------
# Tests del servicio
# ---------------------------------------------------------------------------


class TestROCCAOperadorService:
    def _svc(self, rocca_operador_dao):
        from modulos.registro_operadores.servicio import ROCCAOperadorService

        return ROCCAOperadorService(rocca_operador_dao)

    def test_registrar(self, rocca_operador_dao):
        from modulos.registro_operadores.schema import (
            DomicilioOperativoIn,
            HabilitacionIn,
            InscripcionIn,
            ROCCAOperadorIn,
        )

        svc = self._svc(rocca_operador_dao)
        datos = ROCCAOperadorIn(
            cuit="30666666666",
            razon_social="TRANSPORTISTA PRUEBA S.R.L.",
            tipo="TRANSPORTISTA",
            domicilio="Av. Belgrano 100",
            telefono="385-4400000",
            email="info@transporte.com",
            habilitaciones=[
                HabilitacionIn(tipo="Comercial", numero="HAB-999", autoridad="DGAyG")
            ],
            inscripciones=[
                InscripcionIn(tipo="PROVINCIAL", organismo="DGAyG", numero="PROV-001")
            ],
            domicilios=[
                DomicilioOperativoIn(
                    calle="Av. Belgrano",
                    numero="100",
                    localidad="Santiago del Estero",
                    departamento="Capital",
                )
            ],
        )
        resultado = svc.registrar(datos)
        assert resultado.cuit == "30666666666"
        assert resultado.tipo == "TRANSPORTISTA"
        assert resultado.estado_registral == "ACTIVO"
        assert len(resultado.habilitaciones) == 1
        assert len(resultado.inscripciones) == 1
        assert len(resultado.domicilios) == 1
        assert resultado.domicilios[0].localidad == "Santiago del Estero"

    def test_registrar_duplicado(self, rocca_operador_dao, seed_rocca_operador):
        from modulos.registro_operadores.schema import ROCCAOperadorIn
        from modulos.registro_operadores.servicio import ROCCAOperadorError

        svc = self._svc(rocca_operador_dao)
        datos = ROCCAOperadorIn(
            cuit="30111111111", razon_social="FRIGORIFICO TEST S.A.", tipo="FRIGORIFICO"
        )
        with pytest.raises(ROCCAOperadorError, match="ya inscripto"):
            svc.registrar(datos)

    def test_obtener(self, rocca_operador_dao, seed_rocca_operador):
        svc = self._svc(rocca_operador_dao)
        op = svc.obtener("30111111111")
        assert op.razon_social == "FRIGORIFICO TEST S.A."
        assert op.tipo == "FRIGORIFICO"

    def test_obtener_no_existe(self, rocca_operador_dao):
        from modulos.registro_operadores.servicio import ROCCAOperadorError

        svc = self._svc(rocca_operador_dao)
        with pytest.raises(ROCCAOperadorError, match="no encontrado"):
            svc.obtener("99999999999")

    def test_listar_con_filtros(self, rocca_operador_dao, session_factory):
        from modulos.registro_operadores.enums import TipoOperador

        svc = self._svc(rocca_operador_dao)
        with session_factory() as session:
            crear_rocca_operador_test(session, "30777777777", "MATARIFE PRUEBA", tipo="MATARIFE_ABASTECEDOR")

        ops = svc.listar(tipo=TipoOperador.MATARIFE_ABASTECEDOR)
        assert len(ops) == 1
        assert ops[0].cuit == "30777777777"

    def test_cambiar_estado(self, rocca_operador_dao, seed_rocca_operador):
        from modulos.registro_operadores.enums import EstadoRegistral

        svc = self._svc(rocca_operador_dao)
        op = svc.cambiar_estado("30111111111", EstadoRegistral.SUSPENDIDO)
        assert op.estado_registral == "SUSPENDIDO"

    def test_cambiar_estado_no_existe(self, rocca_operador_dao):
        from modulos.registro_operadores.enums import EstadoRegistral
        from modulos.registro_operadores.servicio import ROCCAOperadorError

        svc = self._svc(rocca_operador_dao)
        with pytest.raises(ROCCAOperadorError):
            svc.cambiar_estado("99999999999", EstadoRegistral.ACTIVO)


# ---------------------------------------------------------------------------
# Tests de validación de schemas
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_cuit_invalido(self):
        from pydantic import ValidationError

        from modulos.registro_operadores.schema import ROCCAOperadorIn

        with pytest.raises(ValidationError, match="CUIT"):
            ROCCAOperadorIn(cuit="123", razon_social="X", tipo="FRIGORIFICO")

    def test_dos_domicilios_principales(self):
        from pydantic import ValidationError

        from modulos.registro_operadores.schema import (
            DomicilioOperativoIn,
            ROCCAOperadorIn,
        )

        with pytest.raises(ValidationError, match="principal"):
            ROCCAOperadorIn(
                cuit="30888888888",
                razon_social="X",
                tipo="CARNICERIA",
                domicilios=[
                    DomicilioOperativoIn(calle="Calle A", tipo="PRINCIPAL"),
                    DomicilioOperativoIn(calle="Calle B", tipo="PRINCIPAL"),
                ],
            )

    def test_tipo_operador_invalido(self):
        from pydantic import ValidationError

        from modulos.registro_operadores.schema import ROCCAOperadorIn

        with pytest.raises(ValidationError):
            ROCCAOperadorIn(cuit="30999999999", razon_social="X", tipo="INVENTADO")
