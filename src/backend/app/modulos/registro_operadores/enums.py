"""Enumeraciones del Módulo I — Registro Provincial de Operadores (ROCCA)."""

from __future__ import annotations

from enum import Enum


class TipoOperador(str, Enum):
    """Tipos de operadores alcanzados por el ROCCA.

    Corresponde al listado de "Operadores Alcanzados" del requerimiento
    oficial: todos los actores que intervienen en la cadena comercial
    de carnes de la provincia.
    """

    FRIGORIFICO = "FRIGORIFICO"
    MATADERO = "MATADERO"
    MATARIFE_ABASTECEDOR = "MATARIFE_ABASTECEDOR"
    ABASTECEDOR = "ABASTECEDOR"
    DISTRIBUIDOR = "DISTRIBUIDOR"
    TRANSPORTISTA = "TRANSPORTISTA"
    CARNICERIA = "CARNICERIA"
    SUPERMERCADO = "SUPERMERCADO"
    CAMARA_FRIGORIFICA = "CAMARA_FRIGORIFICA"
    ELABORADOR_CHACINADOS = "ELABORADOR_CHACINADOS"
    DESPOSTADERO = "DESPOSTADERO"
    OTRO = "OTRO"


class EstadoRegistral(str, Enum):
    """Estado registral del operador en el ROCCA."""

    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    BAJADO = "BAJADO"


class TipoInscripcion(str, Enum):
    """Ámbito de la inscripción del operador."""

    NACIONAL = "NACIONAL"
    PROVINCIAL = "PROVINCIAL"


class TipoDomicilio(str, Enum):
    """Tipo de domicilio operativo del operador."""

    PRINCIPAL = "PRINCIPAL"
    SECUNDARIO = "SECUNDARIO"
