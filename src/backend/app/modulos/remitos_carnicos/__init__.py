"""Módulo de Remitos Electrónicos Cárnicos (REC).

Aplica principios SOLID:

- **S**ingle **R**esponsibility: cada submódulo (operador, mercaderia,
  remito) tiene su propia entidad, DAO, schema y servicio.
- **O**pen/**C**losed: las reglas de validación son extensibles mediante
  subclases de :class:`ReglaValidacion`.
- **L**iskov **S**ubstitution: los DAOs son intercambiables.
- **I**nterface **S**egregation: interfaces pequeñas y específicas.
- **D**ependency **I**nversion: los servicios dependen de DAOs (abstracciones),
  no de SQLAlchemy directamente.

Estructura::

    modulos/remitos_carnicos/
    ├── __init__.py
    ├── base.py          # Entidad (ABC)
    ├── enums.py         # CasoRemito, TipoMovimiento, EstadoRemito, UnidadMedida
    ├── operador/        # Operador: entidad, DAO, schema, servicio
    ├── mercaderia/      # Mercadería: entidad, DAO, schema, servicio
    ├── remito/          # Remito: DAO, schema, validación, servicio
    └── renglon/         # (RenglonRemito está en remito/dao.py)
"""

from .enums import CasoRemito, EstadoRemito, TipoMovimiento, UnidadMedida
from .operador import (
    Operador,
    OperadorDAO,
    OperadorIn,
    OperadorOut,
    OperadorService,
    OperadorError,
)
from .mercaderia import (
    Mercaderia,
    MercaderiaDAO,
    MercaderiaIn,
    MercaderiaOut,
    MercaderiaService,
    MercaderiaError,
)
from .remito import (
    RemitoCarnico,
    RemitoCarnicoDAO,
    RemitoCarnicoIn,
    RemitoCarnicoOut,
    RemitoCarnicoService,
    RemitoCarnicoError,
    ValidadorRemito,
)
from .controlador import crear_router

__all__ = [
    # Enums
    "CasoRemito",
    "EstadoRemito",
    "TipoMovimiento",
    "UnidadMedida",
    # Operador
    "Operador",
    "OperadorDAO",
    "OperadorIn",
    "OperadorOut",
    "OperadorService",
    "OperadorError",
    # Mercadería
    "Mercaderia",
    "MercaderiaDAO",
    "MercaderiaIn",
    "MercaderiaOut",
    "MercaderiaService",
    "MercaderiaError",
    # Remito
    "RemitoCarnico",
    "RemitoCarnicoDAO",
    "RemitoCarnicoIn",
    "RemitoCarnicoOut",
    "RemitoCarnicoService",
    "RemitoCarnicoError",
    "ValidadorRemito",
    # Controlador
    "crear_router",
]
