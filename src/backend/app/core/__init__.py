"""Núcleo de dominio compartido por todos los módulos de ROCCA.

Contiene:
- :mod:`base` — clase base abstracta para entidades.
- :mod:`contracts` — protocolos (interfaces) para inyección de
  dependencias entre módulos.
- :mod:`enums` — enumeraciones compartidas (tipo de persona).
- :mod:`persona` — submódulo de la persona (física o jurídica).
- :mod:`mercaderia` — submódulo de la mercadería (catálogo genérico).
"""

from .base import Entidad
from .contracts import DatabaseDAO as DatabaseDAOProtocol
from .contracts import MercaderiaDAO as MercaderiaDAOProtocol
from .contracts import MercaderiaRef
from .contracts import PersonaDAO as PersonaDAOProtocol
from .contracts import PersonaRef
from .enums import TipoPersona
from .mercaderia import (
    Mercaderia,
    Mercaderia as MercaderiaORM,
    MercaderiaDAO,
    MercaderiaError,
    MercaderiaIn,
    MercaderiaOut,
    MercaderiaService,
)
from .persona import (
    Persona,
    Persona as PersonaORM,
    PersonaDAO,
    PersonaError,
    PersonaFisica,
    PersonaIn,
    PersonaJuridica,
    PersonaOut,
    PersonaService,
)

__all__ = [
    "Entidad",
    "TipoPersona",
    "Persona",
    "PersonaFisica",
    "PersonaJuridica",
    "PersonaORM",
    "PersonaDAO",
    "PersonaIn",
    "PersonaOut",
    "PersonaService",
    "PersonaError",
    "Mercaderia",
    "MercaderiaORM",
    "MercaderiaDAO",
    "MercaderiaIn",
    "MercaderiaOut",
    "MercaderiaService",
    "MercaderiaError",
    "DatabaseDAOProtocol",
    "PersonaDAOProtocol",
    "MercaderiaDAOProtocol",
    "PersonaRef",
    "MercaderiaRef",
]
