"""Enumeraciones del módulo de Remitos Electrónicos Cárnicos."""

from __future__ import annotations

from enum import Enum


class CasoRemito(str, Enum):
    """Casos de remito según la normativa."""

    CASO_01 = "01"  # Envío normal con destinatario
    CASO_02 = "02"  # Envío a consignatario
    CASO_03 = "03"  # Devolución
    CASO_04 = "04"  # Traslado interno
    CASO_05 = "05"  # Exportación
    CASO_06 = "06"  # Importación


class TipoMovimiento(str, Enum):
    """Tipo de movimiento del remito."""

    ENVIO_NORMAL = "ENVIO_NORMAL"
    ENVIO_CONSIGNACION = "ENVIO_CONSIGNACION"
    DEVOLUCION = "DEVOLUCION"
    TRASLADO_INTERNO = "TRASLADO_INTERNO"
    EXPORTACION = "EXPORTACION"
    IMPORTACION = "IMPORTACION"


class EstadoRemito(str, Enum):
    """Estado del remito."""

    EMITIDO = "EMITIDO"
    EN_TRANSITO = "EN_TRANSITO"
    ENTREGADO = "ENTREGADO"
    ANULADO = "ANULADO"
    VENCIDO = "VENCIDO"


class UnidadMedida(str, Enum):
    """Unidad de medida de la mercadería."""

    KG = "KG"
    UN = "UN"
    CAJA = "CAJA"
    BULTO = "BULTO"
