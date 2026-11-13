"""Tests de los casos de uso del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

import pytest

from modulos.registro_operadores.enums import EstadoRegistral, TipoOperador
from modulos.registro_operadores.operador.dao import OperadorDAO
from modulos.registro_operadores.operador.dto import OperadorIn
from modulos.registro_operadores.errores import OperadorError


@pytest.fixture()
def operador_dao(db_session_factory):
    """DAO de operadores."""
    return OperadorDAO(db_session_factory)


@pytest.fixture()
def servicio(operador_service):
    """Alias para no depender del nombre de la fixture del conftest."""
    return operador_service


class TestOperadorService:
    """Tests del servicio de operadores."""

    def test_crear_operador(self, servicio):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="SALA_DE_DESPOSTE",
        )
        resultado = servicio.crear_operador(data)
        assert resultado.cuit == "30111111111"
        assert resultado.razon_social == "FRIGORIFICO TEST S.A."
        assert resultado.tipo == "FRIGORIFICO"
        assert resultado.categoria == "SALA_DE_DESPOSTE"
        assert resultado.estado_registral == "PENDIENTE"

    def test_crear_operador_misma_persona(self, servicio):
        """Crear dos operadores con el mismo CUIT es válido: misma persona, dos sucursales."""
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="SALA_DE_DESPOSTE",
        )
        primero = servicio.crear_operador(data)
        segundo = servicio.crear_operador(data)
        # Mismo CUIT → misma persona, pero dos operadores distintos
        assert primero.id != segundo.id
        assert primero.persona_id == segundo.persona_id

    def test_crear_operador_sin_persona_ni_cuit(self, servicio):
        """Sin persona_id ni CUIT no se puede identificar al titular."""
        data = OperadorIn(
            razon_social="SIN TITULAR",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="SALA_DE_DESPOSTE",
        )
        with pytest.raises(OperadorError, match="persona_id o cuit"):
            servicio.crear_operador(data)

    def test_crear_operador_categoria_invalida(self, servicio):
        data = OperadorIn(
            cuit="30555555555",
            razon_social="OPERADOR INVALIDO",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="CATEGORIA_INEXISTENTE",
        )
        with pytest.raises(OperadorError, match="Categoría inválida"):
            servicio.crear_operador(data)

    def test_obtener(self, servicio):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="SALA_DE_DESPOSTE",
        )
        creado = servicio.crear_operador(data)
        resultado = servicio.obtener(creado.id)
        assert resultado is not None
        assert resultado.razon_social == "FRIGORIFICO TEST S.A."
        assert resultado.cuit == "30111111111"

    def test_obtener_por_cuit(self, servicio):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="SALA_DE_DESPOSTE",
        )
        servicio.crear_operador(data)
        resultado = servicio.obtener_por_cuit("30111111111")
        assert resultado is not None
        assert resultado.razon_social == "FRIGORIFICO TEST S.A."

    def test_obtener_por_cuit_sin_resultado(self, servicio):
        assert servicio.obtener_por_cuit("30999999999") is None

    def test_listar(self, servicio):
        for i in range(3):
            servicio.crear_operador(
                OperadorIn(
                    cuit=f"3011111111{i}",
                    razon_social=f"OPERADOR {i}",
                    tipo=TipoOperador.FRIGORIFICO.value,
                    categoria="SALA_DE_DESPOSTE",
                )
            )
        resultado = servicio.listar()
        assert len(resultado) == 3

    def test_listar_filtrar_por_tipo(self, servicio):
        servicio.crear_operador(
            OperadorIn(
                cuit="30111111111",
                razon_social="FRIGORIFICO",
                tipo=TipoOperador.FRIGORIFICO.value,
                categoria="SALA_DE_DESPOSTE",
            )
        )
        servicio.crear_operador(
            OperadorIn(
                cuit="30111111112",
                razon_social="CARNICERIA",
                tipo=TipoOperador.CARNICERIA.value,
                categoria="CARNICERIAS",
            )
        )
        resultado = servicio.listar(tipo=TipoOperador.FRIGORIFICO.value)
        assert len(resultado) == 1
        assert resultado[0].tipo == "FRIGORIFICO"

    def test_listar_filtrar_por_categoria(self, servicio):
        for i, cat in enumerate(["SALA_DE_DESPOSTE", "CARNICERIAS", "SALA_DE_DESPOSTE"]):
            servicio.crear_operador(
                OperadorIn(
                    cuit=f"3066666666{i}",
                    razon_social=f"OP {cat}",
                    tipo=TipoOperador.FRIGORIFICO.value,
                    categoria=cat,
                )
            )
        resultado = servicio.listar(categoria="SALA_DE_DESPOSTE")
        assert len(resultado) == 2
        assert all(op.categoria == "SALA_DE_DESPOSTE" for op in resultado)

    def test_cambiar_estado(self, servicio):
        data = OperadorIn(
            cuit="30111111111",
            razon_social="FRIGORIFICO TEST S.A.",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="SALA_DE_DESPOSTE",
        )
        creado = servicio.crear_operador(data)
        resultado = servicio.cambiar_estado(creado.id, EstadoRegistral.SUSPENDIDO)
        assert resultado.estado_registral == "SUSPENDIDO"

    def test_cambiar_estado_no_existente(self, servicio):
        with pytest.raises(OperadorError, match="No existe"):
            servicio.cambiar_estado(99999, EstadoRegistral.ACTIVO)

    def test_actividades_economicas_n_m(self, servicio):
        """El alta con ``actividad_ids`` guarda la relación N:M."""
        from modulos.registro_operadores.actividad_economica.dao import (
            ActividadEconomica,
            CatalogoActividadesDAO,
        )

        catalogo = CatalogoActividadesDAO(servicio._dao._session_factory)
        with catalogo._session_factory() as session:
            act = ActividadEconomica(codigo="11110", grupo_id="A", descripcion="Faena de ganado")
            session.add(act)
            session.commit()
            actividad_id = act.id

        data = OperadorIn(
            cuit="30121212121",
            razon_social="FRIGO CON ACTIVIDAD",
            tipo=TipoOperador.FRIGORIFICO.value,
            categoria="SALA_DE_DESPOSTE",
            actividad_ids=[actividad_id],
        )
        creado = servicio.crear_operador(data)
        assert creado.actividad_ids == [actividad_id]
