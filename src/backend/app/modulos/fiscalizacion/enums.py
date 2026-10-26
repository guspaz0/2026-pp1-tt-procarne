"""Enumeraciones del Módulo III — Fiscalización."""

from __future__ import annotations

from enum import Enum


class TipoInspeccion(str, Enum):
    """Tipo de inspección."""

    PROGRAMADA = "PROGRAMADA"
    INESPERADA = "INESPERADA"
    REINSPECCION = "REINSPECCION"
    QUEJA = "QUEJA"


class ResultadoInspeccion(str, Enum):
    """Resultado de la inspección."""

    CONFORME = "CONFORME"
    NO_CONFORME = "NO_CONFORME"
    CON_OBSERVACIONES = "CON_OBSERVACIONES"


class TipoActa(str, Enum):
    """Tipo de acta."""

    INSPECCION = "INSPECCION"
    DECOMISO = "DECOMISO"
    INFRACCION = "INFRACCION"
    SANCION = "SANCION"


class EstadoActa(str, Enum):
    """Estado del acta."""

    BORRADOR = "BORRADOR"
    FIRMADA = "FIRMADA"
    ANULADA = "ANULADA"


class TipoInfraccion(str, Enum):
    """Tipo de infracción."""

    FALTA_DE_HABILITACION = "FALTA_DE_HABILITACION"
    INCUMPLIMIENTO_NORMAS = "INCUMPLIMIENTO_NORMAS"
    FALTA_DE_TRAZABILIDAD = "FALTA_DE_TRACABILIDAD"
    COMERCIALIZACION_ILICITA = "COMERCIALIZACION_ILICITA"
    OTRO = "OTRO"


class GravedadInfraccion(str, Enum):
    """Gravedad de la infracción."""

    LEVE = "LEVE"
    GRAVE = "GRAVE"
    MUY_GRAVE = "MUY_GRAVE"


class TipoSancion(str, Enum):
    """Tipo de sanción."""

    AMONESTACION = "AMONESTACION"
    MULTA = "MULTA"
    SUSPENSION = "SUSPENSION"
    CIERRE = "CIERRE"


class EstadoSancion(str, Enum):
    """Estado de la sanción."""

    PENDIENTE = "PENDIENTE"
    NOTIFICADA = "NOTIFICADA"
    PAGADA = "PAGADA"
    APELADA = "APELADA"
    CANCELADA = "CANCELADA"


class EstadoDecomiso(str, Enum):
    """Estado del decomiso."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    DESTRUCCION = "DESTRUCCION"
    DONACION = "DONACION"
    REINTEGRACION = "REINTEGRACION"
