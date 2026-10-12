"""Tests del Módulo III — Fiscalización."""

from __future__ import annotations

from datetime import date, datetime

import pytest
from sqlalchemy import select

from modulos.fiscalizacion.dao import (
    Acta,
    Decomiso,
    FiscalizacionDAO,
    Infraccion,
    Inspeccion,
    Reincidencia,
    Sancion,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def crear_inspeccion_test(
    session,
    inspector: str = "Inspector Test",
    operador_cuit: str = "30111111111",
    tipo: str = "RUTINA",
    resultado: str = "CONFORME",
    latitud: float = -27.79,
    longitud: float = -64.27,
    enviada: bool = False,
) -> Inspeccion:
    insp = Inspeccion(
        inspector=inspector,
        operador_cuit=operador_cuit,
        tipo=tipo,
        resultado=resultado,
        latitud=latitud,
        longitud=longitud,
        enviada=enviada,
    )
    session.add(insp)
    session.commit()
    session.refresh(insp)
    return insp


def crear_inspeccion_con_infraccion_test(
    session,
    inspector: str = "Inspector Test",
    operador_cuit: str = "30222222222",
    resultado: str = "NO_CONFORME",
    tipo_infraccion: str = "DOCUMENTACION",
    gravedad: str = "GRAVE",
    tipo_sancion: str = "MULTA",
    monto: float = 50000.0,
) -> Inspeccion:
    insp = Inspeccion(
        inspector=inspector,
        operador_cuit=operador_cuit,
        tipo="RUTINA",
        resultado=resultado,
        latitud=-27.80,
        longitud=-64.28,
    )
    session.add(insp)
    session.commit()
    session.refresh(insp)

    infraccion = Infraccion(
        inspeccion_id=insp.id,
        operador_cuit=operador_cuit,
        tipo=tipo_infraccion,
        gravedad=gravedad,
        descripcion="Falta de documentación de trazabilidad",
    )
    session.add(infraccion)
    session.commit()
    session.refresh(infraccion)

    sancion = Sancion(
        infraccion_id=infraccion.id,
        operador_cuit=operador_cuit,
        tipo=tipo_sancion,
        monto=monto,
        estado="PENDIENTE",
    )
    session.add(sancion)
    session.commit()
    session.refresh(sancion)

    return insp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fiscalizacion_dao(session_factory):
    return FiscalizacionDAO(session_factory)


@pytest.fixture()
def seed_fiscalizacion(session_factory):
    """Crea inspecciones de prueba."""
    with session_factory() as session:
        insp1 = crear_inspeccion_test(
            session,
            inspector="Inspector A",
            operador_cuit="30111111111",
            resultado="CONFORME",
        )
        insp2 = crear_inspeccion_con_infraccion_test(
            session,
            inspector="Inspector B",
            operador_cuit="30222222222",
            resultado="NO_CONFORME",
        )
        insp3 = crear_inspeccion_test(
            session,
            inspector="Inspector C",
            operador_cuit="30333333333",
            resultado="CON_OBSERVACIONES",
        )

    return {"id1": insp1.id, "id2": insp2.id, "id3": insp3.id}


# ---------------------------------------------------------------------------
# Tests del DAO
# ---------------------------------------------------------------------------


class TestFiscalizacionDAO:
    def test_guardar_y_obtener_inspeccion(self, fiscalizacion_dao, session_factory):
        with session_factory() as session:
            insp = crear_inspeccion_test(session, inspector="Inspector DAO")
            insp_id = insp.id

        guardada = fiscalizacion_dao.obtener_inspeccion(insp_id)
        assert guardada is not None
        assert guardada.inspector == "Inspector DAO"
        assert guardada.resultado == "CONFORME"
        assert guardada.latitud == -27.79

    def test_obtener_inspeccion_no_existe(self, fiscalizacion_dao):
        assert fiscalizacion_dao.obtener_inspeccion(9999) is None

    def test_listar_inspecciones(self, fiscalizacion_dao, seed_fiscalizacion):
        insps = fiscalizacion_dao.listar_inspecciones()
        assert len(insps) == 3

    def test_listar_filtrar_por_operador(self, fiscalizacion_dao, seed_fiscalizacion):
        insps = fiscalizacion_dao.listar_inspecciones(operador_cuit="30222222222")
        assert len(insps) == 1
        assert insps[0].inspector == "Inspector B"

    def test_listar_filtrar_por_resultado(self, fiscalizacion_dao, seed_fiscalizacion):
        insps = fiscalizacion_dao.listar_inspecciones(resultado="NO_CONFORME")
        assert len(insps) == 1
        assert insps[0].operador_cuit == "30222222222"

    def test_listar_paginado(self, fiscalizacion_dao, seed_fiscalizacion):
        insps = fiscalizacion_dao.listar_inspecciones(limite=2, offset=0)
        assert len(insps) == 2
        insps = fiscalizacion_dao.listar_inspecciones(limite=2, offset=2)
        assert len(insps) == 1

    def test_actualizar_inspeccion_enviada(self, fiscalizacion_dao, seed_fiscalizacion):
        insp = fiscalizacion_dao.obtener_inspeccion(seed_fiscalizacion["id1"])
        insp.enviada = True
        actualizada = fiscalizacion_dao.actualizar_inspeccion(insp)
        assert actualizada.enviada is True

    def test_eliminar_inspeccion(self, fiscalizacion_dao, seed_fiscalizacion):
        resultado = fiscalizacion_dao.eliminar_inspeccion(seed_fiscalizacion["id1"])
        assert resultado is True
        assert fiscalizacion_dao.obtener_inspeccion(seed_fiscalizacion["id1"]) is None

    def test_eliminar_inspeccion_no_existe(self, fiscalizacion_dao):
        resultado = fiscalizacion_dao.eliminar_inspeccion(9999)
        assert resultado is False

    def test_guardar_acta(self, fiscalizacion_dao, seed_fiscalizacion):
        acta = Acta(
            inspeccion_id=seed_fiscalizacion["id1"],
            tipo="CONSTATACION",
            numero="ACT-001",
            descripcion="Inspección rutinaria",
            estado="BORRADOR",
        )
        guardada = fiscalizacion_dao.guardar_acta(acta)
        assert guardada.id is not None
        assert guardada.numero == "ACT-001"
        assert guardada.estado == "BORRADOR"

    def test_guardar_decomiso(self, fiscalizacion_dao, seed_fiscalizacion):
        decomiso = Decomiso(
            inspeccion_id=seed_fiscalizacion["id1"],
            producto="Carne de res",
            cantidad=25.0,
            unidad="KG",
            motivo="Caducidad",
            estado="EN_CURSADO",
        )
        guardado = fiscalizacion_dao.guardar_decomiso(decomiso)
        assert guardado.id is not None
        assert guardado.producto == "Carne de res"
        assert guardado.cantidad == 25.0

    def test_guardar_infraccion(self, fiscalizacion_dao, seed_fiscalizacion):
        infraccion = Infraccion(
            inspeccion_id=seed_fiscalizacion["id1"],
            operador_cuit="30111111111",
            tipo="HIGIENE",
            gravedad="LEVE",
            descripcion="Deficiencia menor",
        )
        guardada = fiscalizacion_dao.guardar_infraccion(infraccion)
        assert guardada.id is not None
        assert guardada.tipo == "HIGIENE"
        assert guardada.gravedad == "LEVE"

    def test_listar_infracciones(self, fiscalizacion_dao, seed_fiscalizacion):
        infracciones = fiscalizacion_dao.listar_infracciones()
        assert len(infracciones) == 1
        assert infracciones[0].tipo == "DOCUMENTACION"

    def test_listar_infracciones_filtrar_por_operador(
        self, fiscalizacion_dao, seed_fiscalizacion
    ):
        infracciones = fiscalizacion_dao.listar_infracciones(
            operador_cuit="30222222222"
        )
        assert len(infracciones) == 1

        infracciones = fiscalizacion_dao.listar_infracciones(
            operador_cuit="30999999999"
        )
        assert len(infracciones) == 0

    def test_guardar_sancion(self, fiscalizacion_dao, seed_fiscalizacion):
        # Obtener la infracción existente
        infracciones = fiscalizacion_dao.listar_infracciones()
        infraccion_id = infracciones[0].id

        sancion = Sancion(
            infraccion_id=infraccion_id,
            operador_cuit="30222222222",
            tipo="MULTA",
            monto=100000.0,
            estado="PENDIENTE",
        )
        guardada = fiscalizacion_dao.guardar_sancion(sancion)
        assert guardada.id is not None
        assert guardada.monto == 100000.0

    def test_reincidencia_nueva(self, fiscalizacion_dao):
        rec = fiscalizacion_dao.incrementar_reincidencia(
            "30444444444", "Primera infracción grave"
        )
        assert rec.cantidad == 1
        assert "Primera infracción grave" in rec.observaciones

    def test_reincidencia_incremento(self, fiscalizacion_dao):
        fiscalizacion_dao.incrementar_reincidencia("30555555555", "Primera")
        rec = fiscalizacion_dao.incrementar_reincidencia(
            "30555555555", "Segunda"
        )
        assert rec.cantidad == 2

    def test_obtener_reincidencia(self, fiscalizacion_dao):
        fiscalizacion_dao.incrementar_reincidencia("30666666666", "Test")
        rec = fiscalizacion_dao.obtener_reincidencia("30666666666")
        assert rec is not None
        assert rec.cantidad == 1

    def test_obtener_reincidencia_no_existe(self, fiscalizacion_dao):
        assert fiscalizacion_dao.obtener_reincidencia("30999999999") is None

    def test_listar_reincidencias(self, fiscalizacion_dao):
        fiscalizacion_dao.incrementar_reincidencia("30777777777", "A")
        fiscalizacion_dao.incrementar_reincidencia("30888888888", "B")
        fiscalizacion_dao.incrementar_reincidencia("30888888888", "B2")
        recs = fiscalizacion_dao.listar_reincidencias()
        assert len(recs) == 2
        # Ordenado por cantidad descendente
        assert recs[0].operador_cuit == "30888888888"
        assert recs[0].cantidad == 2


# ---------------------------------------------------------------------------
# Tests del servicio
# ---------------------------------------------------------------------------


class TestFiscalizacionService:
    def _svc(self, fiscalizacion_dao):
        from modulos.fiscalizacion.servicio import FiscalizacionService

        return FiscalizacionService(fiscalizacion_dao)

    def test_registrar_inspeccion_conforme(self, fiscalizacion_dao):
        from modulos.fiscalizacion.schema import InspeccionIn

        svc = self._svc(fiscalizacion_dao)
        datos = InspeccionIn(
            inspector="Inspector Test",
            operador_cuit="30111111111",
            tipo="RUTINA",
            resultado="CONFORME",
            latitud=-27.79,
            longitud=-64.27,
        )
        resultado = svc.registrar_inspeccion(datos)
        assert resultado.id is not None
        assert resultado.inspector == "Inspector Test"
        assert resultado.resultado == "CONFORME"
        assert len(resultado.actas) == 0
        assert len(resultado.infracciones) == 0

    def test_registrar_inspeccion_con_infraccion_y_sancion(
        self, fiscalizacion_dao
    ):
        from modulos.fiscalizacion.schema import (
            InfraccionIn,
            InspeccionIn,
            SancionIn,
        )

        svc = self._svc(fiscalizacion_dao)
        datos = InspeccionIn(
            inspector="Inspector Test",
            operador_cuit="30222222222",
            tipo="PROGRAMADA",
            resultado="NO_CONFORME",
            infracciones=[
                InfraccionIn(
                    tipo="TRAZABILIDAD",
                    gravedad="GRAVE",
                    descripcion="Falta de trazabilidad",
                    sanciones=[
                        SancionIn(
                            tipo="MULTA",
                            monto=75000.0,
                            descripcion="Multa por falta de trazabilidad",
                        )
                    ],
                )
            ],
        )
        resultado = svc.registrar_inspeccion(datos)
        assert resultado.resultado == "NO_CONFORME"
        assert len(resultado.infracciones) == 1
        assert resultado.infracciones[0].tipo == "TRAZABILIDAD"
        assert len(resultado.infracciones[0].sanciones) == 1
        assert resultado.infracciones[0].sanciones[0].monto == 75000.0

    def test_registrar_inspeccion_con_decomiso(self, fiscalizacion_dao):
        from modulos.fiscalizacion.schema import DecomisoIn, InspeccionIn

        svc = self._svc(fiscalizacion_dao)
        datos = InspeccionIn(
            inspector="Inspector Test",
            operador_cuit="30333333333",
            tipo="RUTINA",
            resultado="CON_OBSERVACIONES",
            decomisos=[
                DecomisoIn(
                    producto="Carne de vacuno",
                    cantidad=15.5,
                    unidad="KG",
                    motivo="Caducidad",
                )
            ],
        )
        resultado = svc.registrar_inspeccion(datos)
        assert len(resultado.decomisos) == 1
        assert resultado.decomisos[0].producto == "Carne de vacuno"
        assert resultado.decomisos[0].cantidad == 15.5

    def test_registrar_inspeccion_no_conforme_sin_infracciones(
        self, fiscalizacion_dao
    ):
        from pydantic import ValidationError

        from modulos.fiscalizacion.schema import InspeccionIn

        with pytest.raises(ValidationError, match="al menos una infracción"):
            InspeccionIn(
                inspector="Inspector Test",
                operador_cuit="30111111111",
                resultado="NO_CONFORME",
            )

    def test_obtener_inspeccion(self, fiscalizacion_dao, seed_fiscalizacion):
        svc = self._svc(fiscalizacion_dao)
        insp = svc.obtener_inspeccion(seed_fiscalizacion["id1"])
        assert insp.inspector == "Inspector A"
        assert insp.resultado == "CONFORME"

    def test_obtener_inspeccion_no_existe(self, fiscalizacion_dao):
        from modulos.fiscalizacion.servicio import FiscalizacionError

        svc = self._svc(fiscalizacion_dao)
        with pytest.raises(FiscalizacionError, match="no encontrada"):
            svc.obtener_inspeccion(9999)

    def test_listar_inspecciones(self, fiscalizacion_dao, seed_fiscalizacion):
        from modulos.fiscalizacion.enums import ResultadoInspeccion

        svc = self._svc(fiscalizacion_dao)
        insps = svc.listar_inspecciones()
        assert len(insps) == 3

        insps = svc.listar_inspecciones(
            resultado=ResultadoInspeccion.NO_CONFORME
        )
        assert len(insps) == 1

    def test_marcar_enviada(self, fiscalizacion_dao, seed_fiscalizacion):
        svc = self._svc(fiscalizacion_dao)
        insp = svc.marcar_enviada(seed_fiscalizacion["id1"])
        assert insp.enviada is True

    def test_eliminar_inspeccion(self, fiscalizacion_dao, seed_fiscalizacion):
        svc = self._svc(fiscalizacion_dao)
        svc.eliminar_inspeccion(seed_fiscalizacion["id1"])
        with pytest.raises(Exception):
            svc.obtener_inspeccion(seed_fiscalizacion["id1"])

    def test_firmar_acta(self, fiscalizacion_dao, seed_fiscalizacion):
        from modulos.fiscalizacion.dao import Acta as ActaORM

        svc = self._svc(fiscalizacion_dao)
        with fiscalizacion_dao._session_factory() as session:
            acta = ActaORM(
                inspeccion_id=seed_fiscalizacion["id1"],
                tipo="CONSTATACION",
                estado="BORRADOR",
            )
            session.add(acta)
            session.commit()
            session.refresh(acta)
            acta_id = acta.id

        svc.firmar_acta(acta_id)

        with fiscalizacion_dao._session_factory() as session:
            acta = session.get(ActaORM, acta_id)
            assert acta.estado == "FIRMADA"
            assert acta.fecha_firma is not None

    def test_firmar_acta_no_existe(self, fiscalizacion_dao):
        from modulos.fiscalizacion.servicio import FiscalizacionError

        svc = self._svc(fiscalizacion_dao)
        with pytest.raises(FiscalizacionError, match="no encontrada"):
            svc.firmar_acta(9999)

    def test_listar_infracciones(self, fiscalizacion_dao, seed_fiscalizacion):
        from modulos.fiscalizacion.enums import GravedadInfraccion

        svc = self._svc(fiscalizacion_dao)
        infracciones = svc.listar_infracciones()
        assert len(infracciones) == 1

        infracciones = svc.listar_infracciones(
            gravedad=GravedadInfraccion.GRAVE
        )
        assert len(infracciones) == 1

    def test_actualizar_estado_sancion(self, fiscalizacion_dao, seed_fiscalizacion):
        from modulos.fiscalizacion.enums import EstadoSancion
        from modulos.fiscalizacion.dao import Sancion as SancionORM

        svc = self._svc(fiscalizacion_dao)

        # Obtener la sanción existente
        with fiscalizacion_dao._session_factory() as session:
            sancion = session.execute(
                select(SancionORM)
            ).scalars().first()
            sancion_id = sancion.id

        svc.actualizar_estado_sancion(sancion_id, EstadoSancion.CUMPLIDA)

        with fiscalizacion_dao._session_factory() as session:
            sancion = session.get(SancionORM, sancion_id)
            assert sancion.estado == "CUMPLIDA"
            assert sancion.fecha_cumplimiento is not None

    def test_registrar_reincidencia(self, fiscalizacion_dao):
        from modulos.fiscalizacion.schema import ReincidenciaIn

        svc = self._svc(fiscalizacion_dao)
        datos = ReincidenciaIn(
            operador_cuit="30999999999",
            observaciones="Infracción grave de trazabilidad",
        )
        rec = svc.registrar_reincidencia(datos)
        assert rec.cantidad == 1
        assert "Infracción grave" in rec.observaciones

    def test_reincidencia_incremento(self, fiscalizacion_dao):
        from modulos.fiscalizacion.schema import ReincidenciaIn

        svc = self._svc(fiscalizacion_dao)
        svc.registrar_reincidencia(
            ReincidenciaIn(operador_cuit="30888888888", observaciones="Primera")
        )
        rec = svc.registrar_reincidencia(
            ReincidenciaIn(operador_cuit="30888888888", observaciones="Segunda")
        )
        assert rec.cantidad == 2

    def test_obtener_reincidencia_no_existe(self, fiscalizacion_dao):
        from modulos.fiscalizacion.servicio import FiscalizacionError

        svc = self._svc(fiscalizacion_dao)
        with pytest.raises(FiscalizacionError, match="No hay reincidencias"):
            svc.obtener_reincidencia("30999999999")

    def test_listar_reincidencias(self, fiscalizacion_dao):
        from modulos.fiscalizacion.schema import ReincidenciaIn

        svc = self._svc(fiscalizacion_dao)
        svc.registrar_reincidencia(
            ReincidenciaIn(operador_cuit="30777777777", observaciones="A")
        )
        svc.registrar_reincidencia(
            ReincidenciaIn(operador_cuit="30888888888", observaciones="B")
        )
        svc.registrar_reincidencia(
            ReincidenciaIn(operador_cuit="30888888888", observaciones="B2")
        )
        recs = svc.listar_reincidencias()
        assert len(recs) == 2
        assert recs[0].operador_cuit == "30888888888"
        assert recs[0].cantidad == 2


# ---------------------------------------------------------------------------
# Tests de validación de schemas
# ---------------------------------------------------------------------------


class TestSchemas:
    def test_cuit_invalido(self):
        from pydantic import ValidationError

        from modulos.fiscalizacion.schema import InspeccionIn

        with pytest.raises(ValidationError, match="CUIT"):
            InspeccionIn(
                inspector="Inspector",
                operador_cuit="123",
            )

    def test_no_conforme_sin_infracciones(self):
        from pydantic import ValidationError

        from modulos.fiscalizacion.schema import InspeccionIn

        with pytest.raises(ValidationError, match="al menos una infracción"):
            InspeccionIn(
                inspector="Inspector",
                operador_cuit="30111111111",
                resultado="NO_CONFORME",
            )

    def test_latitud_invalida(self):
        from pydantic import ValidationError

        from modulos.fiscalizacion.schema import InspeccionIn

        with pytest.raises(ValidationError):
            InspeccionIn(
                inspector="Inspector",
                latitud=95.0,
            )

    def test_reincidencia_cuit_invalido(self):
        from pydantic import ValidationError

        from modulos.fiscalizacion.schema import ReincidenciaIn

        with pytest.raises(ValidationError, match="at least 11 characters"):
            ReincidenciaIn(operador_cuit="123")
