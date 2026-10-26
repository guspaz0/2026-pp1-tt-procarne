"""Enumeraciones del Módulo II — Trazabilidad Comercial."""

from __future__ import annotations

from enum import Enum


class TipoIngreso(str, Enum):
    """Tipo de ingreso de mercadería."""

    PRODUCCION_PROPIA = "PRODUCCION_PROPIA"
    COMPRA = "COMPRA"
    CONSIGNACION = "CONSIGNACION"
    DEVOLUCION = "DEVOLUCION"
    TRASLADO = "TRASLADO"


class Especie(str, Enum):
    """Especie animal."""

    BOVINO = "BOVINO"
    PORCINO = "PORCINO"
    OVINO = "OVINO"
    CAPRINO = "CAPRINO"
    EQUINO = "EQUINO"


class TipoDestino(str, Enum):
    """Tipo de destino de la mercadería."""

    FRIGORIFICO = "FRIGORIFICO"
    CARNICERIA = "CARNICERIA"
    COMERCIALIZADOR = "COMERCIALIZADOR"
    EXPORTACION = "EXPORTACION"
    OTRO = "OTRO"


class EstadoTrazabilidad(str, Enum):
    """Estado del registro de trazabilidad."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    ANULADO = "ANULADO"
