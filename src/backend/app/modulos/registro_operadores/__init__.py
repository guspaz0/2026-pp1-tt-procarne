"""Módulo I — Registro Provincial de Operadores (ROCCA).

Contiene:
- :mod:`enums` — tipos de operador, estado registral, etc.
- :mod:`dao` — ORM y DAO (ROCCAOperador, Habilitacion, Inscripcion,
  DomicilioOperativo)
- :mod:`schema` — DTOs de entrada/salida
- :mod:`servicio` — casos de uso
- :mod:`controlador` — router API
- :mod:`registro_operadores` — composición del módulo (inyección de
  dependencias)
"""

from .controlador import crear_router
from .dao import (
    DomicilioOperativo,
    Habilitacion,
    Inscripcion,
    ROCCAOperador,
    ROCCAOperadorDAO,
)
from .enums import EstadoRegistral, TipoDomicilio, TipoInscripcion, TipoOperador
from .registro_operadores import RegistroOperadoresModulo
from .schema import (
    DomicilioOperativoIn,
    DomicilioOperativoOut,
    HabilitacionIn,
    HabilitacionOut,
    InscripcionIn,
    InscripcionOut,
    ROCCAOperadorIn,
    ROCCAOperadorOut,
)
from .servicio import ROCCAOperadorError, ROCCAOperadorService

__all__ = [
    "DomicilioOperativo",
    "DomicilioOperativoIn",
    "DomicilioOperativoOut",
    "EstadoRegistral",
    "Habilitacion",
    "HabilitacionIn",
    "HabilitacionOut",
    "Inscripcion",
    "InscripcionIn",
    "InscripcionOut",
    "ROCCAOperador",
    "ROCCAOperadorDAO",
    "ROCCAOperadorError",
    "ROCCAOperadorIn",
    "ROCCAOperadorOut",
    "ROCCAOperadorService",
    "RegistroOperadoresModulo",
    "TipoDomicilio",
    "TipoInscripcion",
    "TipoOperador",
    "crear_router",
]
