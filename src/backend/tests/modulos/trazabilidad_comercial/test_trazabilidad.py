"""Tests del Módulo II — Trazabilidad Comercial."""

from __future__ import annotations

from datetime import date

import pytest

from modulos.trazabilidad_comercial.dao import (
    RegistroTrazabilidad,
    RegistroTrazabilidadDAO,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def crear_registro_trazabilidad_test(
    session,
    tipo_ingreso: str = "INGRESO_EXTRAPROVINCIAL",
    especie: str = "BOVINO",
    cantidad_kg: float = 500.0,
    origen_provincia: str = "Córdoba",
    numero_dte: str = "DTE-001",
    numero_remito: str = "REC-001",
    destino_cuit: str = "30111111111",
    estado: str = "REGISTRADO",
) -> RegistroTrazabilidad:
    reg = RegistroTrazabilidad(
        tipo_ingreso=tipo_ingreso,
        especie=especie,
        cantidad_kg=cantidad_kg,
        origen_provincia=origen_provincia,
        establecimiento_faena="FRIGORIFICO CORDOBA S.A.",
        numero_dte=numero_dte,
        numero_remito=numero_remito,
        destino_cuit=destino_cuit,
        destino_tipo="FRIGORIFICO",
        destino_razon_social="FRIGORIFICO TEST S.A.",
        estado=estado,
        fecha_ingreso=date(2026, 1, 15),
    )
    session.add(reg)
    session.commit()
    session.refresh(reg)
    return reg


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def trazabilidad_dao(session_factory):
    return RegistroTrazabilidadDAO(session_factory)


@pytest.fixture()
def seed_trazabilidad(session_factory):
    """Crea registros de prueba."""
    with session_factory() as session:
        reg1 = crear_registro_trazabilidad_test(
            session,
            tipo_ingreso="INGRESO_EXTRAPROVINCIAL",
            especie="BOVINO",
            cantidad_kg=500.0,
            origen_provincia="Córdoba",
            numero_dte="DTE-001",
            numero_remito="REC-001",
            destino_cuit="30111111111",
        )
        reg2 = crear_registro_trazabilidad_test(
            session,
            tipo_ingreso="FAENA_PROVINCIAL",
            especie="OVINO",
            cantidad_kg=120.0,
            origen_provincia=None,
            numero_dte="DTE-002",
            numero_remito="REC-002",
            destino_cuit="30222222222",
            estado="VALIDADO",
        )
        reg3 = crear_registro_trazabilidad_test(
            session,
            tipo_ingreso="INGRESO_EXTRAPROVINCIAL",
            especie="PORCINO",
            cantidad_kg=300.0,
            origen_provincia="Buenos Aires",
            numero_dte="DTE-003",
            numero_remito="REC-003",
            destino_cuit="30333333333",
            estado="RECHAZADO",
        )

    return {"id1": reg1.id, "id2": reg2.id, "id3": reg3.id}


# ---------------------------------------------------------------------------
# Tests del DAO
# ---------------------------------------------------------------------------


class TestRegistroTrazabilidadDAO:
    def test_guardar_y_obtener(self, trazabilidad_dao, session_factory):
        with session_factory() as session:
            reg = crear_registro_trazabilidad_test(
                session, numero_dte="DTE-100", numero_remito="REC-100"
            )
            reg_id = reg.id

        guardado = trazabilidad_dao.obtener_por_id(reg_id)
        assert guardado is not None
        assert guardado.numero_dte == "DTE-100"
        assert guardado.numero_remito == "REC-100"
        assert guardado.cantidad_kg == 500.0
        assert guardado.especie == "BOVINO"

    def test_obtener_por_dte(self, trazabilidad_dao, seed_trazabilidad):
        reg = trazabilidad_dao.obtener_por_dte("DTE-001")
        assert reg is not None
        assert reg.numero_remito == "REC-001"
        assert reg.origen_provincia == "Córdoba"

    def test_obtener_por_remito(self, trazabilidad_dao, seed_trazabilidad):
        reg = trazabilidad_dao.obtener_por_remito("REC-002")
        assert reg is not None
        assert reg.numero_dte == "DTE-002"
        assert reg.especie == "OVINO"

    def test_obtener_por_dte_no_existe(self, trazabilidad_dao):
        assert trazabilidad_dao.obtener_por_dte("DTE-999") is None

    def test_listar(self, trazabilidad_dao, seed_trazabilidad):
        regs = trazabilidad_dao.listar()
        assert len(regs) == 3

    def test_listar_filtrar_por_tipo_ingreso(self, trazabilidad_dao, seed_trazabilidad):
        regs = trazabilidad_dao.listar(tipo_ingreso="FAENA_PROVINCIAL")
        assert len(regs) == 1
        assert regs[0].especie == "OVINO"

    def test_listar_filtrar_por_especie(self, trazabilidad_dao, seed_trazabilidad):
        regs = trazabilidad_dao.listar(especie="PORCINO")
        assert len(regs) == 1
        assert regs[0].origen_provincia == "Buenos Aires"

    def test_listar_filtrar_por_estado(self, trazabilidad_dao, seed_trazabilidad):
        regs = trazabilidad_dao.listar(estado="VALIDADO")
        assert len(regs) == 1
        assert regs[0].numero_dte == "DTE-002"

    def test_listar_filtrar_por_origen(self, trazabilidad_dao, seed_trazabilidad):
        regs = trazabilidad_dao.listar(origen_provincia="Córdoba")
        assert len(regs) == 1
        assert regs[0].numero_dte == "DTE-001"

    def test_listar_filtrar_por_destino_cuit(self, trazabilidad_dao, seed_trazabilidad):
        regs = trazabilidad_dao.listar(destino_cuit="30222222222")
        assert len(regs) == 1
        assert regs[0].especie == "OVINO"

    def test_listar_paginado(self, trazabilidad_dao, seed_trazabilidad):
        regs = trazabilidad_dao.listar(limite=2, offset=0)
        assert len(regs) == 2
        regs = trazabilidad_dao.listar(limite=2, offset=2)
        assert len(regs) == 1

    def test_actualizar_estado(self, trazabilidad_dao, seed_trazabilidad):
        reg = trazabilidad_dao.obtener_por_id(seed_trazabilidad["id1"])
        reg.estado = "VALIDADO"
        actualizado = trazabilidad_dao.actualizar(reg)
        assert actualizado.estado == "VALIDADO"

    def test_eliminar(self, trazabilidad_dao, seed_trazabilidad):
        resultado = trazabilidad_dao.eliminar(seed_trazabilidad["id1"])
        assert resultado is True
        assert trazabilidad_dao.obtener_por_id(seed_trazabilidad["id1"]) is None

    def test_eliminar_no_existe(self, trazabilidad_dao):
        resultado = trazabilidad_dao.eliminar(9999)
        assert resultado is False


# ---------------------------------------------------------------------------
# Tests del servicio
# ---------------------------------------------------------------------------


class TestTrazabilidadComercialService:
    def _svc(self, trazabilidad_dao):
        from modulos.trazabilidad_comercial.servicio import (
            TrazabilidadComercialService,
        )

        return TrazabilidadComercialService(trazabilidad_dao)

    def test_registrar(self, trazabilidad_dao):
        from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn

        svc = self._svc(trazabilidad_dao)
        datos = RegistroTrazabilidadIn(
            tipo_ingreso="INGRESO_EXTRAPROVINCIAL",
            cantidad_kg=250.5,
            especie="BOVINO",
            origen_provincia="Tucumán",
            establecimiento_faena="FRIGORIFICO TUCUMAN",
            numero_dte="DTE-200",
            numero_remito="REC-200",
            destino_tipo="CARNICERIA",
            destino_cuit="30444444444",
            destino_razon_social="CARNICERIA EL ESTERO",
        )
        resultado = svc.registrar(datos)
        assert resultado.id is not None
        assert resultado.tipo_ingreso == "INGRESO_EXTRAPROVINCIAL"
        assert resultado.cantidad_kg == 250.5
        assert resultado.especie == "BOVINO"
        assert resultado.origen_provincia == "Tucumán"
        assert resultado.estado == "REGISTRADO"

    def test_registrar_duplicado_dte(self, trazabilidad_dao, seed_trazabilidad):
        from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn
        from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialError

        svc = self._svc(trazabilidad_dao)
        datos = RegistroTrazabilidadIn(
            tipo_ingreso="INGRESO_EXTRAPROVINCIAL",
            cantidad_kg=100.0,
            especie="BOVINO",
            origen_provincia="Córdoba",
            numero_dte="DTE-001",
        )
        with pytest.raises(TrazabilidadComercialError, match="DTE-001"):
            svc.registrar(datos)

    def test_registrar_duplicado_remito(self, trazabilidad_dao, seed_trazabilidad):
        from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn
        from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialError

        svc = self._svc(trazabilidad_dao)
        datos = RegistroTrazabilidadIn(
            tipo_ingreso="INGRESO_EXTRAPROVINCIAL",
            cantidad_kg=100.0,
            especie="OVINO",
            origen_provincia="Salta",
            numero_remito="REC-002",
        )
        with pytest.raises(TrazabilidadComercialError, match="REC-002"):
            svc.registrar(datos)

    def test_obtener(self, trazabilidad_dao, seed_trazabilidad):
        svc = self._svc(trazabilidad_dao)
        reg = svc.obtener(seed_trazabilidad["id1"])
        assert reg.numero_dte == "DTE-001"
        assert reg.cantidad_kg == 500.0

    def test_obtener_no_existe(self, trazabilidad_dao):
        from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialError

        svc = self._svc(trazabilidad_dao)
        with pytest.raises(TrazabilidadComercialError, match="no encontrado"):
            svc.obtener(9999)

    def test_listar_con_filtros(self, trazabilidad_dao, seed_trazabilidad):
        from modulos.trazabilidad_comercial.enums import Especie

        svc = self._svc(trazabilidad_dao)
        regs = svc.listar(especie=Especie.PORCINO)
        assert len(regs) == 1
        assert regs[0].origen_provincia == "Buenos Aires"

    def test_validar(self, trazabilidad_dao, seed_trazabilidad):
        svc = self._svc(trazabilidad_dao)
        reg = svc.validar(seed_trazabilidad["id1"])
        assert reg.estado == "VALIDADO"

    def test_validar_ya_validado(self, trazabilidad_dao, seed_trazabilidad):
        from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialError

        svc = self._svc(trazabilidad_dao)
        with pytest.raises(TrazabilidadComercialError, match="no está en estado REGISTRADO"):
            svc.validar(seed_trazabilidad["id2"])  # ya VALIDADO

    def test_rechazar(self, trazabilidad_dao, seed_trazabilidad):
        svc = self._svc(trazabilidad_dao)
        reg = svc.rechazar(seed_trazabilidad["id1"], motivo="Documentación incompleta")
        assert reg.estado == "RECHAZADO"
        assert "Documentación incompleta" in reg.observaciones

    def test_rechazar_no_existe(self, trazabilidad_dao):
        from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialError

        svc = self._svc(trazabilidad_dao)
        with pytest.raises(TrazabilidadComercialError):
            svc.rechazar(9999)

    def test_eliminar(self, trazabilidad_dao, seed_trazabilidad):
        svc = self._svc(trazabilidad_dao)
        svc.eliminar(seed_trazabilidad["id1"])
        with pytest.raises(Exception):
            svc.obtener(seed_trazabilidad["id1"])


# ---------------------------------------------------------------------------
# Tests de validación de schemas
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_cantidad_negativa(self):
        from pydantic import ValidationError

        from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn

        with pytest.raises(ValidationError, match="greater than"):
            RegistroTrazabilidadIn(
                tipo_ingreso="FAENA_PROVINCIAL",
                cantidad_kg=-10,
                especie="BOVINO",
            )

    def test_ingreso_extraprovincial_sin_origen(self):
        from pydantic import ValidationError

        from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn

        with pytest.raises(ValidationError, match="provincia de origen"):
            RegistroTrazabilidadIn(
                tipo_ingreso="INGRESO_EXTRAPROVINCIAL",
                cantidad_kg=100.0,
                especie="BOVINO",
            )

    def test_cuit_destino_invalido(self):
        from pydantic import ValidationError

        from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn

        with pytest.raises(ValidationError, match="CUIT"):
            RegistroTrazabilidadIn(
                tipo_ingreso="FAENA_PROVINCIAL",
                cantidad_kg=100.0,
                especie="BOVINO",
                destino_cuit="123",
            )

    def test_especie_invalida(self):
        from pydantic import ValidationError

        from modulos.trazabilidad_comercial.schema import RegistroTrazabilidadIn

        with pytest.raises(ValidationError):
            RegistroTrazabilidadIn(
                tipo_ingreso="FAENA_PROVINCIAL",
                cantidad_kg=100.0,
                especie="AVEROIDEA",
            )
