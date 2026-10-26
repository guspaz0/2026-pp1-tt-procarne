"""Enumeraciones del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from enum import Enum


class TipoOperador(str, Enum):
    """Tipo de operador de la cadena cárnica."""

    PRODUCTOR = "PRODUCTOR"
    FRIGORIFICO = "FRIGORIFICO"
    CARNICERIA = "CARNICERIA"
    COMERCIALIZADOR = "COMERCIALIZADOR"
    TRANSPORTE = "TRANSPORTE"
    DEPOSITO = "DEPOSITO"


class EstadoRegistral(str, Enum):
    """Estado registral del operador."""

    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    BAJADO = "BAJADO"


class TipoInscripcion(str, Enum):
    """Tipo de inscripción en el registro."""

    PRINCIPAL = "PRINCIPAL"
    SECUNDARIA = "SECUNDARIA"


class TipoDomicilio(str, Enum):
    """Tipo de domicilio del operador."""

    FISCAL = "FISCAL"
    OPERATIVO = "OPERATIVO"
