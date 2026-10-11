"""Tests del módulo de operadores."""

from __future__ import annotations

import pytest


class TestOperadorDAO:
    """Tests del DAO de operadores."""

    def test_crear_operador(self, operador_dao):
        from modulos.remitos_carnicos.operador.dao import Operador

        op = Operador(
            cuit="30111111111",
            razon_social="PRUEBA CREADA S.A.",
            domicilio="Av. Siempreviva 742",
            situacion="ACTIVO",
        )
        guardado = operador_dao.guardar(op)

        assert guardado.id is not None
        assert guardado.cuit == "30111111111"
        assert guardado.razon_social == "PRUEBA CREADA S.A."

    def test_obtener_por_cuit(self, operador_dao, seed_operador):
        op = operador_dao.obtener_por_cuit("20123456789")
        assert op is not None
        assert op.razon_social == "TEST OPERADOR S.A."
        assert op.situacion == "ACTIVO"

    def test_obtener_por_cuit_no_existe(self, operador_dao):
        op = operador_dao.obtener_por_cuit("99999999999")
        assert op is None

    def test_obtener_por_id(self, operador_dao, seed_operador):
        op = operador_dao.obtener_por_id(seed_operador["id"])
        assert op is not None
        assert op.cuit == "20123456789"

    def test_listar(self, operador_dao, seed_operador):
        ops = operador_dao.listar(limite=10)
        assert len(ops) == 1
        assert ops[0].cuit == "20123456789"

    def test_listar_por_actividad(self, operador_dao, seed_operador):
        ops = operador_dao.listar_por_actividad(actividad_id=1)
        assert len(ops) == 1
        assert ops[0].cuit == "20123456789"

    def test_listar_por_actividad_sin_resultados(self, operador_dao, seed_operador):
        ops = operador_dao.listar_por_actividad(actividad_id=2)
        assert len(ops) == 0

    def test_operador_tiene_categorias(self, operador_dao, seed_operador):
        op = operador_dao.obtener_por_cuit("20123456789")
        assert op is not None
        assert len(op.categorias) == 2
        cats = {c.categoria for c in op.categorias}
        assert "Productor/criador" in cats
        assert "Invernador" in cats

    def test_operador_tiene_actividades(self, operador_dao, seed_operador):
        op = operador_dao.obtener_por_cuit("20123456789")
        assert op is not None
        assert len(op.actividades) == 1
        assert op.actividades[0].nombre == "Bovino/Bubalino"

    def test_actualizar_operador(self, operador_dao, seed_operador):
        op = operador_dao.obtener_por_cuit("20123456789")
        op.email = "nuevo@test.com"
        actualizado = operador_dao.actualizar(op)
        assert actualizado.email == "nuevo@test.com"


class TestOperadorService:
    """Tests del servicio de operadores."""

    def test_crear(self, operador_dao):
        from modulos.remitos_carnicos.operador.servicio import OperadorService
        from modulos.remitos_carnicos.operador.schema import OperadorIn

        svc = OperadorService(operador_dao)
        datos = OperadorIn(
            cuit="30222222222",
            razon_social="SERVICIO TEST S.R.L.",
        )
        resultado = svc.crear(datos)
        assert resultado.cuit == "30222222222"
        assert resultado.razon_social == "SERVICIO TEST S.R.L."

    def test_crear_duplicado(self, operador_dao, seed_operador):
        from modulos.remitos_carnicos.operador.servicio import OperadorService, OperadorError
        from modulos.remitos_carnicos.operador.schema import OperadorIn

        svc = OperadorService(operador_dao)
        datos = OperadorIn(cuit="20123456789", razon_social="DUPLICADO")
        with pytest.raises(OperadorError, match="ya existe"):
            svc.crear(datos)

    def test_obtener(self, operador_dao, seed_operador):
        from modulos.remitos_carnicos.operador.servicio import OperadorService

        svc = OperadorService(operador_dao)
        resultado = svc.obtener("20123456789")
        assert resultado.cuit == "20123456789"
        assert len(resultado.actividades) == 1

    def test_obtener_no_existe(self, operador_dao):
        from modulos.remitos_carnicos.operador.servicio import OperadorService, OperadorError

        svc = OperadorService(operador_dao)
        with pytest.raises(OperadorError, match="no encontrado"):
            svc.obtener("00000000000")

    def test_listar(self, operador_dao, seed_operador):
        from modulos.remitos_carnicos.operador.servicio import OperadorService

        svc = OperadorService(operador_dao)
        resultados = svc.listar()
        assert len(resultados) == 1


class TestOperadorSchema:
    """Tests de serialización del DTO."""

    def test_operador_out_incluye_actividades(self, operador_dao, seed_operador):
        from modulos.remitos_carnicos.operador.schema import OperadorOut

        op = operador_dao.obtener_por_cuit("20123456789")
        dto = OperadorOut.from_orm(op)

        assert dto.cuit == "20123456789"
        assert len(dto.actividades) == 1
        act = dto.actividades[0]
        assert act.nombre == "Bovino/Bubalino"
        assert len(act.categorias) == 2

    def test_operador_out_categorias_por_actividad(self, operador_dao, seed_operador):
        from modulos.remitos_carnicos.operador.schema import OperadorOut

        op = operador_dao.obtener_por_cuit("20123456789")
        dto = OperadorOut.from_orm(op)

        act = dto.actividades[0]
        cat_nombres = {c.categoria for c in act.categorias}
        assert cat_nombres == {"Productor/criador", "Invernador"}

    def test_operador_out_json(self, operador_dao, seed_operador):
        from modulos.remitos_carnicos.operador.schema import OperadorOut
        import json

        op = operador_dao.obtener_por_cuit("20123456789")
        dto = OperadorOut.from_orm(op)
        data = json.loads(dto.model_dump_json())

        assert data["cuit"] == "20123456789"
        assert "actividades" in data
        assert data["actividades"][0]["id"] == 1
