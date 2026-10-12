"""Módulo III — Fiscalización (ROCCA).

Contiene:
- :mod:`enums` — tipos de inspección, acta, infracción, sanción, estado
- :mod:`dao` — ORM y DAO (Inspección, Acta, Decomiso, Infracción, Sanción, Reincidencia)
- :mod:`schema` — DTOs de entrada/salida
- :mod:`servicio` — casos de uso
- :mod:`controlador` — router API
- :mod:`fiscalizacion` — composición del módulo
"""

from .controlador import crear_router
from .dao import (
    Acta,
    Decomiso,
    FiscalizacionDAO,
    Infraccion,
    Inspeccion,
    Reincidencia,
    Sancion,
)
from .enums import (
    EstadoActa,
    EstadoDecomiso,
    EstadoSancion,
    GravedadInfraccion,
    ResultadoInspeccion,
    TipoActa,
    TipoInfraccion,
    TipoInspeccion,
    TipoSancion,
)
from .fiscalizacion import FiscalizacionModulo
from .schema import (
    ActaIn,
    ActaOut,
    DecomisoIn,
    DecomisoOut,
    InspeccionIn,
    InspeccionOut,
    InfraccionIn,
    InfraccionOut,
    ReincidenciaIn,
    ReincidenciaOut,
    SancionIn,
    SancionOut,
)
from .servicio import FiscalizacionError, FiscalizacionService

__all__ = [
    "Acta",
    "ActaIn",
    "ActaOut",
    "Decomiso",
    "DecomisoIn",
    "DecomisoOut",
    "EstadoActa",
    "EstadoDecomiso",
    "EstadoSancion",
    "FiscalizacionDAO",
    "FiscalizacionError",
    "FiscalizacionModulo",
    "FiscalizacionService",
    "GravedadInfraccion",
    "Infraccion",
    "InfraccionIn",
    "InfraccionOut",
    "Inspeccion",
    "InspeccionIn",
    "InspeccionOut",
    "Reincidencia",
    "ReincidenciaIn",
    "ReincidenciaOut",
    "ResultadoInspeccion",
    "Sancion",
    "SancionIn",
    "SancionOut",
    "TipoActa",
    "TipoInfraccion",
    "TipoInspeccion",
    "TipoSancion",
    "crear_router",
]
