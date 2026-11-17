"""Paquete de validación de CUIT (padrón público vía IDFiscal)."""

from core.cuit.validator import CuitError, CuitValidator, validar_formato_cuit

__all__ = ["CuitError", "CuitValidator", "validar_formato_cuit"]
