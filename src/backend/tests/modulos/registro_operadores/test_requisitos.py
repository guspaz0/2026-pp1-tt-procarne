"""Tests de requisitos de inscripción y categorías del Módulo I."""

from __future__ import annotations

import pytest

from modulos.registro_operadores.dao import OperadorDAO
from modulos.registro_operadores.enums import (
    CategoriaOperador,
    EstadoRegistral,
    RequisitoEspecifico,
    RequisitoGeneralOperador,
    TipoOperador,
)
from modulos.registro_operadores.schema import OperadorIn
from modulos.registro_operadores.servicio import (
    REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
    REQUISITOS_GENERALES,
    OperadorError,
    OperadorService,
)


@pytest.fixture()
def operador_dao(db_session_factory):
    return OperadorDAO(db_session_factory)


@pytest.fixture()
def operador_service(operador_dao, persona_service, session_factory):
    from modulos.registro_operadores.domicilio_operativo.dao import DomicilioOperativoDAO
    from modulos.registro_operadores.domicilio_operativo.servicio import DomicilioOperativoService
    from modulos.registro_operadores.habilitacion.dao import HabilitacionDAO
    from modulos.registro_operadores.habilitacion.servicio import HabilitacionService
    from modulos.registro_operadores.inscripcion.dao import InscripcionDAO
    from modulos.registro_operadores.inscripcion.servicio import InscripcionService
    from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
    from modulos.registro_operadores.requisito_inscripcion.servicio import RequisitoInscripcionService

    return OperadorService(
        operador_dao,
        persona_service=persona_service,
        habilitacion_service=HabilitacionService(HabilitacionDAO(session_factory)),
        inscripcion_service=InscripcionService(InscripcionDAO(session_factory)),
        domicilio_service=DomicilioOperativoService(DomicilioOperativoDAO(session_factory)),
        requisito_service=RequisitoInscripcionService(RequisitoInscripcionDAO(session_factory)),
    )


class TestCategorias:
    """Tests de la gestión de categorías de operador."""

    def test_crear_operador_con_categoria_sala_desposte(self, operador_service):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="SALA DE DESPOSTE TEST",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria == "SALA_DE_DESPOSTE"

    def test_crear_operador_con_categoria_carniceria(self, operador_service):
        data = OperadorIn(
            cuit="30222222222",
            razon_social="CARNICERIA LA BUENA",
            tipo=TipoOperador.CARNICERIA.value,
            categoria=CategoriaOperador.CARNICERIAS.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria == "CARNICERIAS"

    def test_crear_operador_con_categoria_transportista(self, operador_service):
        data = OperadorIn(
            cuit="30333333333",
            razon_social="TRANSPORTES DEL SUR",
            tipo=TipoOperador.TRANSPORTE.value,
            categoria=CategoriaOperador.TRANSPONEDOR.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria == "TRANSPONEDOR"

    def test_crear_operador_sin_categoria(self, operador_service):
        data = OperadorIn(
            cuit="30444444444",
            razon_social="OPERADOR SIN CATEGORIA",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria is None

    def test_crear_operador_categoria_invalida(self, operador_service):
        data = OperadorIn(
            cuit="30555555555",
            razon_social="OPERADOR INVALIDO",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="CATEGORIA_INEXISTENTE",
        )
        with pytest.raises(OperadorError, match="Categoría inválida"):
            operador_service.crear_operador(data)

    def test_listar_filtrar_por_categoria(self, operador_service):
        for i, cat in enumerate([
            CategoriaOperador.SALA_DE_DESPOSTE,
            CategoriaOperador.CARNICERIAS,
            CategoriaOperador.SALA_DE_DESPOSTE,
        ]):
            operador_service.crear_operador(
                OperadorIn(
                    cuit=f"3066666666{i}",
                    razon_social=f"OP {cat.value}",
                    tipo=TipoOperador.FRIGORIFICO.value,
                    categoria=cat.value,
                )
            )

        resultado = operador_service.listar(categoria=CategoriaOperador.SALA_DE_DESPOSTE.value)
        assert len(resultado) == 2
        assert all(op.categoria == "SALA_DE_DESPOSTE" for op in resultado)

        resultado = operador_service.listar(categoria=CategoriaOperador.CARNICERIAS.value)
        assert len(resultado) == 1

    def test_listar_filtrar_por_categoria_y_tipo(self, operador_service):
        operador_service.crear_operador(
            OperadorIn(
                cuit="30777777770",
                razon_social="FRIGO CARNICERIA",
                tipo=TipoOperador.CARNICERIA.value,
                categoria=CategoriaOperador.CARNICERIAS.value,
            )
        )
        operador_service.crear_operador(
            OperadorIn(
                cuit="30777777771",
                razon_social="FRIGO SALA",
                tipo=TipoOperador.FRIGORIFICO.value,
                categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
            )
        )

        resultado = operador_service.listar(
            tipo=TipoOperador.CARNICERIA.value,
            categoria=CategoriaOperador.CARNICERIAS.value,
        )
        assert len(resultado) == 1
        assert resultado[0].cuit == "30777777770"


class TestRequisitos:
    """Tests de la gestión de requisitos de inscripción."""

    def test_requisitos_generales_creados_al_alta(self, operador_service):
        data = OperadorIn(
            cuit="30888888880",
            razon_social="TEST REQUISITOS",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        # 2 generales + 5 específicos (SALA_DE_DESPOSTE) = 7 requisitos
        assert len(requisitos) == 7

        generales = [r for r in requisitos if r.es_general]
        especificos = [r for r in requisitos if not r.es_general]
        assert len(generales) == 2
        assert len(especificos) == 5

        codigos_generales = {r.codigo for r in generales}
        assert codigos_generales == {
            RequisitoGeneralOperador.AFIP_ULTIMO_PAGO.value,
            RequisitoGeneralOperador.REGIMEN_PROVISIONAL.value,
        }

    def test_requisitos_especificos_por_categoria_carniceria(self, operador_service):
        data = OperadorIn(
            cuit="30888888881",
            razon_social="CARNICERIA TEST",
            tipo=TipoOperador.CARNICERIA.value,
            categoria=CategoriaOperador.CARNICERIAS.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        especificos = [r for r in requisitos if not r.es_general]
        # CARNICERIAS: formulario_101, habilitacion_municipal, libreta_sanitaria
        assert len(especificos) == 3

    def test_requisitos_especificos_por_categoria_transportista(self, operador_service):
        data = OperadorIn(
            cuit="30888888882",
            razon_social="TRANSPORTES TEST",
            tipo=TipoOperador.TRANSPORTE.value,
            categoria=CategoriaOperador.TRANSPONEDOR.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        # TRANSPONEDOR no tiene específicos
        especificos = [r for r in requisitos if not r.es_general]
        assert len(especificos) == 0

    def test_requisitos_sin_categoria(self, operador_service):
        data = OperadorIn(
            cuit="30888888883",
            razon_social="SIN CATEGORIA",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        # Solo 2 generales, sin específicos
        assert len(requisitos) == 2
        assert all(r.es_general for r in requisitos)

    def test_actualizar_requisito_cumplido(self, operador_service):
        data = OperadorIn(
            cuit="30999999990",
            razon_social="TEST ACTUALIZAR",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        req_id = requisitos[0].id
        actualizado = operador_service.actualizar_requisito(creado.id, req_id, cumplido=True)
        assert actualizado.cumplido is True
        assert actualizado.fecha_cumplimiento is not None

    def test_actualizar_requisito_no_cumplido(self, operador_service):
        data = OperadorIn(
            cuit="30999999991",
            razon_social="TEST NO CUMPLIDO",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        req_id = requisitos[0].id
        actualizado = operador_service.actualizar_requisito(creado.id, req_id, cumplido=False)
        assert actualizado.cumplido is False
        assert actualizado.fecha_cumplimiento is None

    def test_requisitos_pendientes(self, operador_service):
        data = OperadorIn(
            cuit="30999999992",
            razon_social="TEST PENDIENTES",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)

        # Inicialmente todos están pendientes (2 generales + 5 específicos)
        pendientes = operador_service.obtener_requisitos_pendientes(creado.id)
        assert len(pendientes) == 7

        # Cumplir uno
        requisitos = operador_service.listar_requisitos(creado.id)
        operador_service.actualizar_requisito(creado.id, requisitos[0].id, cumplido=True)

        pendientes = operador_service.obtener_requisitos_pendientes(creado.id)
        assert len(pendientes) == 6

    def test_requisito_no_existente(self, operador_service):
        data = OperadorIn(
            cuit="30999999993",
            razon_social="TEST ERROR",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)

        with pytest.raises(OperadorError, match="No existe el requisito"):
            operador_service.actualizar_requisito(creado.id, 99999, cumplido=True)

    def test_catalogo_requisitos(self, operador_service):
        # Verificar que el catálogo tiene las 8 categorías
        assert len(REQUISITOS_ESPECIFICOS_POR_CATEGORIA) == 8

        # Verificar que hay 2 requisitos generales
        assert len(REQUISITOS_GENERALES) == 2

        # Verificar que las categorías con requisitos tienen al menos 1
        categorias_con_requisitos = {
            k: v for k, v in REQUISITOS_ESPECIFICOS_POR_CATEGORIA.items() if v
        }
        for categoria, requisitos in categorias_con_requisitos.items():
            assert len(requisitos) >= 1, f"Categoría {categoria} sin requisitos específicos"

    def test_validar_requisito_para_categoria(self, operador_service):
        """El método de validación devuelve True/False correctamente."""
        assert operador_service.validar_requisito_para_categoria(
            CategoriaOperador.SALA_DE_DESPOSTE.value, "habilitacion_municipal"
        )
        assert not operador_service.validar_requisito_para_categoria(
            CategoriaOperador.SALA_DE_DESPOSTE.value, "libreta_sanitaria"
        )
        assert operador_service.validar_requisito_para_categoria(
            CategoriaOperador.TRANSPONEDOR.value, "afip_ultimo_pago"
        )
