"""Enums de codificación de valores AFIP para Remitos Electrónicos Cárnicos."""

from __future__ import annotations

from enum import Enum


class EstadoRemito(str, Enum):
    """Estados del Remito."""

    EMITIDO = "E"
    ANULADO = "AN"
    NO_UTILIZADO = "NU"


class TipoMovimiento(str, Enum):
    """Tipos de movimiento."""

    ENVIO_NORMAL = "ENV"
    RETIRO_EN_PLANTA = "PLA"
    REPARTO = "REP"
    REDESTINO = "RED"


class UnidadMedida(str, Enum):
    """Unidades de medida."""

    KILOGRAMOS = "1"
    UNIDADES = "7"


class CasoRemito(int, Enum):
    """Casos de remisión según el modelo oficial (modelos 01–07)."""

    CASO_01 = 1
    CASO_02 = 2
    CASO_03 = 3
    CASO_04 = 4
    CASO_05 = 5
    CASO_06 = 6
    CASO_07 = 7

    @property
    def es_reparto(self) -> bool:
        return self in (CasoRemito.CASO_04, CasoRemito.CASO_05, CasoRemito.CASO_06)

    @property
    def tiene_depositario(self) -> bool:
        return self in (CasoRemito.CASO_02, CasoRemito.CASO_03, CasoRemito.CASO_05, CasoRemito.CASO_06)

    @property
    def tiene_destinatario(self) -> bool:
        return not self.es_reparto and self != CasoRemito.CASO_07
