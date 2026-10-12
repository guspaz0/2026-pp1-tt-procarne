"""Enumeraciones del Módulo II — Trazabilidad Comercial (ROCCA)."""

from __future__ import annotations

from enum import Enum


class TipoIngreso(str, Enum):
    """Tipo de ingreso de carne a la provincia."""

    INGRESO_EXTRAPROVINCIAL = "INGRESO_EXTRAPROVINCIAL"
    FAENA_PROVINCIAL = "FAENA_PROVINCIAL"


class Especie(str, Enum):
    """Especies de la cadena cárnica."""

    BOVINO = "BOVINO"
    OVINO = "OVINO"
    PORCINO = "PORCINO"
    CAMELIDO = "CAMELIDO"
    OTRO = "OTRO"


class TipoDestino(str, Enum):
    """Destino comercial de la mercadería."""

    CARNICERIA = "CARNICERIA"
    SUPERMERCADO = "SUPERMERCADO"
    DISTRIBUIDOR = "DISTRIBUIDOR"
    FRIGORIFICO = "FRIGORIFICO"
    MATADERO = "MATADERO"
    DESPOSTADERO = "DESPOSTADERO"
    CAMARA_FRIGORIFICA = "CAMARA_FRIGORIFICA"
    ELABORADOR_CHACINADOS = "ELABORADOR_CHACINADOS"
    EXPORTACION = "EXPORTACION"
    OTRO = "OTRO"


class EstadoTrazabilidad(str, Enum):
    """Estado del registro de trazabilidad."""

    REGISTRADO = "REGISTRADO"
    VALIDADO = "VALIDADO"
    RECHAZADO = "RECHAZADO"
