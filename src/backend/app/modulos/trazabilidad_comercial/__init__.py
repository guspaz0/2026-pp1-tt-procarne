"""Módulo II — Trazabilidad Comercial (ROCCA).

Contiene:
- :mod:`enums` — tipo de ingreso, especie, destino, estado
- :mod:`dao` — ORM y DAO (RegistroTrazabilidad)
- :mod:`schema` — DTOs de entrada/salida
- :mod:`servicio` — casos de uso
- :mod:`controlador` — router API
- :mod:`trazabilidad_comercial` — composición del módulo
"""

from .controlador import crear_router
from .dao import RegistroTrazabilidad, RegistroTrazabilidadDAO
from .enums import Especie, EstadoTrazabilidad, TipoDestino, TipoIngreso
from .schema import RegistroTrazabilidadIn, RegistroTrazabilidadOut
from .servicio import TrazabilidadComercialError, TrazabilidadComercialService
from .trazabilidad_comercial import TrazabilidadComercialModulo

__all__ = [
    "Especie",
    "EstadoTrazabilidad",
    "RegistroTrazabilidad",
    "RegistroTrazabilidadDAO",
    "RegistroTrazabilidadIn",
    "RegistroTrazabilidadOut",
    "TrazabilidadComercialError",
    "TrazabilidadComercialModulo",
    "TrazabilidadComercialService",
    "TipoDestino",
    "TipoIngreso",
    "crear_router",
]
