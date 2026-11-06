"""Tests de requisitos de inscripción y categorías del Módulo I."""

from __future__ import annotations

import pytest

from modulos.registro_operadores.dao import ROCCAOperadorDAO
from modulos.registro_operadores.enums import (
    CategoriaOperador,
    EstadoRegistral,
    RequisitoEspecifico,
    RequisitoGeneral,
    TipoOperador,
)
from modulos.registro_operadores.schema import ROCCAOperadorIn
from modulos.registro_operadores.servicio import (
    REQUISITOS_ESPECIFICOS_POR_CATEGORIA,
    REQUISITOS_GENERALES,
    ROCCAOperadorError,
    ROCCAOperadorService,
)


@pytest.fixture()
def operador_dao(db_session_factory):
    return ROCCAOperadorDAO(db_session_factory)


@pytest.fixture()
def operador_service(operador_dao):
    return ROCCAOperadorService(operador_dao)


class TestCategorias:
    """Tests de la gestión de categorías de operador."""

    def test_crear_operador_con_categoria_sala_desposte(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30111111111",
            razon_social="SALA DE DESPOSTE TEST",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria == "SALA_DE_DESPOSTE"

    def test_crear_operador_con_categoria_carniceria(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30222222222",
            razon_social="CARNICERIA LA BUENA",
            tipo=TipoOperador.CARNICERIA.value,
            categoria=CategoriaOperador.CARNICERIAS.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria == "CARNICERIAS"

    def test_crear_operador_con_categoria_transportista(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30333333333",
            razon_social="TRANSPORTES DEL SUR",
            tipo=TipoOperador.TRANSPORTE.value,
            categoria=CategoriaOperador.TRANSPONEDOR.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria == "TRANSPONEDOR"

    def test_crear_operador_sin_categoria(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30444444444",
            razon_social="OPERADOR SIN CATEGORIA",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        resultado = operador_service.crear_operador(data)
        assert resultado.categoria is None

    def test_crear_operador_categoria_invalida(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30555555555",
            razon_social="OPERADOR INVALIDO",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="CATEGORIA_INEXISTENTE",
        )
        with pytest.raises(ROCCAOperadorError, match="Categoría inválida"):
            operador_service.crear_operador(data)

    def test_listar_filtrar_por_categoria(self, operador_service):
        # Crear operadores de distintas categorías
        for i, cat in enumerate([
            CategoriaOperador.SALA_DE_DESPOSTE,
            CategoriaOperador.CARNICERIAS,
            CategoriaOperador.SALA_DE_DESPOSTE,
        ]):
            operador_service.crear_operador(
                ROCCAOperadorIn(
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
            ROCCAOperadorIn(
                cuit="30777777770",
                razon_social="FRIGO CARNICERIA",
                tipo=TipoOperador.CARNICERIA.value,
                categoria=CategoriaOperador.CARNICERIAS.value,
            )
        )
        operador_service.crear_operador(
            ROCCAOperadorIn(
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
        data = ROCCAOperadorIn(
            cuit="30888888880",
            razon_social="TEST REQUISITOS",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        # 3 generales + 1 específico = 4 requisitos
        assert len(requisitos) == 4

        generales = [r for r in requisitos if r.es_general]
        especificos = [r for r in requisitos if not r.es_general]
        assert len(generales) == 3
        assert len(especificos) == 1

        # Verificar que los generales son los esperados
        codigos_generales = {r.codigo for r in generales}
        assert codigos_generales == {
            RequisitoGeneral.INGRESOS_BRUTOS.value,
            RequisitoGeneral.AFIP.value,
            RequisitoGeneral.REGIMEN_PROVISIONAL.value,
        }

        # Verificar que el específico es el de sala de desposte
        assert especificos[0].codigo == RequisitoEspecifico.REGISTRO_NACIONAL_FRIGORIFICOS.value

    def test_requisitos_especificos_por_categoria_carniceria(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30888888881",
            razon_social="CARNICERIA TEST",
            tipo=TipoOperador.CARNICERIA.value,
            categoria=CategoriaOperador.CARNICERIAS.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        especificos = [r for r in requisitos if not r.es_general]
        assert len(especificos) == 1
        assert especificos[0].codigo == RequisitoEspecifico.MATRICULA_MUNICIPAL_CARNICERIA.value

    def test_requisitos_especificos_por_categoria_transportista(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30888888882",
            razon_social="TRANSPORTES TEST",
            tipo=TipoOperador.TRANSPORTE.value,
            categoria=CategoriaOperador.TRANSPONEDOR.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        especificos = [r for r in requisitos if not r.es_general]
        assert len(especificos) == 1
        assert especificos[0].codigo == RequisitoEspecifico.REGISTRO_NACIONAL_TRANSPORTE.value

    def test_requisitos_sin_categoria(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30888888883",
            razon_social="SIN CATEGORIA",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        # Solo 3 generales, sin específicos
        assert len(requisitos) == 3
        assert all(r.es_general for r in requisitos)

    def test_actualizar_requisito_cumplido(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30999999990",
            razon_social="TEST ACTUALIZAR",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        # Marcar un requisito como cumplido
        req_id = requisitos[0].id
        actualizado = operador_service.actualizar_requisito(creado.id, req_id, cumplido=True)
        assert actualizado.cumplido is True
        assert actualizado.fecha_cumplimiento is not None

    def test_actualizar_requisito_no_cumplido(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30999999991",
            razon_social="TEST NO CUMPLIDO",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)
        requisitos = operador_service.listar_requisitos(creado.id)

        # Marcar como no cumplido (ya lo está)
        req_id = requisitos[0].id
        actualizado = operador_service.actualizar_requisito(creado.id, req_id, cumplido=False)
        assert actualizado.cumplido is False
        assert actualizado.fecha_cumplimiento is None

    def test_requisitos_pendientes(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30999999992",
            razon_social="TEST PENDIENTES",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria=CategoriaOperador.SALA_DE_DESPOSTE.value,
        )
        creado = operador_service.crear_operador(data)

        # Inicialmente todos están pendientes
        pendientes = operador_service.obtener_requisitos_pendientes(creado.id)
        assert len(pendientes) == 4

        # Cumplir uno
        requisitos = operador_service.listar_requisitos(creado.id)
        operador_service.actualizar_requisito(creado.id, requisitos[0].id, cumplido=True)

        pendientes = operador_service.obtener_requisitos_pendientes(creado.id)
        assert len(pendientes) == 3

    def test_requisito_no_existente(self, operador_service):
        data = ROCCAOperadorIn(
            cuit="30999999993",
            razon_social="TEST ERROR",
            tipo=TipoOperador.FRIGORIFICO.value,
        )
        creado = operador_service.crear_operador(data)

        with pytest.raises(ROCCAOperadorError, match="No existe el requisito"):
            operador_service.actualizar_requisito(creado.id, 99999, cumplido=True)

    def test_catalogo_requisitos(self, operador_service):
        # Verificar que el catálogo tiene las 7 categorías
        assert len(REQUISITOS_ESPECIFICOS_POR_CATEGORIA) == 7

        # Verificar que hay 3 requisitos generales
        assert len(REQUISITOS_GENERALES) == 3

        # Verificar que cada categoría tiene al menos 1 requisito específico
        for categoria, requisitos in REQUISITOS_ESPECIFICOS_POR_CATEGORIA.items():
            assert len(requisitos) >= 1, f"Categoría {categoria} sin requisitos específicos"


class TestAPIRequisitos:
    """Tests de la API para requisitos de inscripción."""

    @pytest.fixture()
    def api_client(self, db_engine):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from configs.dao import SQLiteDAO
        from modulos.registro_operadores.registro_operadores import RegistroOperadoresModulo
        from sqlalchemy.orm import sessionmaker

        app = FastAPI(title="ROCCA Test")

        dao = SQLiteDAO("sqlite://")
        dao._engine = db_engine
        dao._session_factory = sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False, bind=db_engine
        )

        modulo = RegistroOperadoresModulo(dao)
        modulo.registrar(app)

        return TestClient(app)

    def test_listar_requisitos(self, api_client):
        # Crear operador con categoría
        r = api_client.post("/api/registro-operadores", json={
            "cuit": "30111111111",
            "razon_social": "SALA TEST",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        })
        assert r.status_code == 201
        op_id = r.json()["id"]

        # Listar requisitos
        r = api_client.get(f"/api/registro-operadores/{op_id}/requisitos")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 4  # 3 generales + 1 específico

    def test_listar_requisitos_pendientes(self, api_client):
        r = api_client.post("/api/registro-operadores", json={
            "cuit": "30222222222",
            "razon_social": "CARNICERIA TEST",
            "tipo": "CARNICERIA",
            "categoria": "CARNICERIAS",
        })
        op_id = r.json()["id"]

        r = api_client.get(f"/api/registro-operadores/{op_id}/requisitos/pendientes")
        assert r.status_code == 200
        assert len(r.json()) == 4  # Todos pendientes inicialmente

    def test_actualizar_requisito_via_api(self, api_client):
        r = api_client.post("/api/registro-operadores", json={
            "cuit": "30333333333",
            "razon_social": "TRANSPORTES TEST",
            "tipo": "TRANSPORTE",
            "categoria": "TRANSPONEDOR",
        })
        op_id = r.json()["id"]

        # Obtener requisitos
        r = api_client.get(f"/api/registro-operadores/{op_id}/requisitos")
        req_id = r.json()[0]["id"]

        # Marcar como cumplido
        r = api_client.patch(
            f"/api/registro-operadores/{op_id}/requisitos/{req_id}",
            params={"cumplido": True},
        )
        assert r.status_code == 200
        assert r.json()["cumplido"] is True

    def test_catalogo_requisitos_endpoint(self, api_client):
        r = api_client.get("/api/registro-operadores/catalogo/requisitos")
        assert r.status_code == 200
        data = r.json()
        assert "generales" in data
        assert "especificos_por_categoria" in data
        assert len(data["generales"]) == 3
        assert len(data["especificos_por_categoria"]) == 7

    def test_listar_filtrar_por_categoria_api(self, api_client):
        # Crear operadores de distintas categorías
        api_client.post("/api/registro-operadores", json={
            "cuit": "30444444440",
            "razon_social": "SALA 1",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        })
        api_client.post("/api/registro-operadores", json={
            "cuit": "30444444441",
            "razon_social": "CARNICERIA 1",
            "tipo": "CARNICERIA",
            "categoria": "CARNICERIAS",
        })
        api_client.post("/api/registro-operadores", json={
            "cuit": "30444444442",
            "razon_social": "SALA 2",
            "tipo": "FRIGORIFICO",
            "categoria": "SALA_DE_DESPOSTE",
        })

        # Filtrar por categoría
        r = api_client.get("/api/registro-operadores", params={"categoria": "SALA_DE_DESPOSTE"})
        assert r.status_code == 200
        assert len(r.json()) == 2

        r = api_client.get("/api/registro-operadores", params={"categoria": "CARNICERIAS"})
        assert r.status_code == 200
        assert len(r.json()) == 1
