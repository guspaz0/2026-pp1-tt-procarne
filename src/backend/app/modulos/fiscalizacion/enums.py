"""Enumeraciones del Módulo III — Fiscalización (ROCCA)."""

from __future__ import annotations

from enum import Enum


class TipoInspeccion(str, Enum):
    """Tipo de inspección realizada."""

    RUTINA = "RUTINA"
    PROGRAMADA = "PROGRAMADA"
    DENUNCIA = "DENUNCIA"
    CONTROLES_ESPECIALES = "CONTROLES_ESPECIALES"
    AUDITORIA = "AUDITORIA"


class ResultadoInspeccion(str, Enum):
    """Resultado de la inspección."""

    CONFORME = "CONFORME"
    NO_CONFORME = "NO_CONFORME"
    CON_OBSERVACIONES = "CON_OBSERVACIONES"


class TipoActa(str, Enum):
    """Tipo de acta levantada."""

    CONSTATAcion = "CONSTATACION"
    ADVERTENCIA = "ADVERTENCIA"
    DECOMISO = "DECOMISO"
    CIERRE = "CIERRE"
    OTRO = "OTRO"


class EstadoActa(str, Enum):
    """Estado del acta."""

    BORRADOR = "BORRADOR"
    FIRMADA = "FIRMADA"
    ANULADA = "ANULADA"


class TipoInfraccion(str, Enum):
    """Tipo de infracción detectada."""

    DOCUMENTACION = "DOCUMENTACION"
    TRAZABILIDAD = "TRAZABILIDAD"
    HIGIENE = "HIGIENE"
    TEMPERATURA = "TEMPERATURA"
    PESAJE = "PESAJE"
    ROTULACION = "ROTULACION"
    TRANSPORTE = "TRANSPORTE"
    OTRO = "OTRO"


class GravedadInfraccion(str, Enum):
    """Gravedad de la infracción."""

    LEVE = "LEVE"
    GRAVE = "GRAVE"
    MUY_GRAVE = "MUY_GRAVE"


class TipoSancion(str, Enum):
    """Tipo de sanción aplicada."""

    AMONESTACION = "AMONESTACION"
    MULTA = "MULTA"
    DECOMISO = "DECOMISO"
    SUSPENSION = "SUSPENSION"
    CIERRE = "CIERRE"


class EstadoSancion(str, Enum):
    """Estado de la sanción."""

    PENDIENTE = "PENDIENTE"
    NOTIFICADA = "NOTIFICADA"
    CUMPLIDA = "CUMPLIDA"
    ANULADA = "ANULADA"


class EstadoDecomiso(str, Enum):
    """Estado del decomiso."""

    EN_CURSADO = "EN_CURSADO"
    DESTINADO = "DESTINADO"
    DISTRIBUIDO = "DISTRIBUIDO"
    DESTRUIDO = "DESTRUIDO"
