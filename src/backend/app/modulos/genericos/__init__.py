"""Módulo de datos genéricos compartidos por los demás módulos.

Contiene las entidades transversales del dominio:

- :class:`Persona` (clase abstracta) y sus subclases
  :class:`PersonaFisica` / :class:`PersonaJuridica`.
- :class:`Mercaderia` — catálogo de códigos de mercadería.

Estructura::

    modulos/genericos/
    ├── __init__.py
    ├── base.py          # Entidad (ABC)
    ├── enums.py         # TipoPersona
    ├── persona/         # Persona: entidad, DAO, schema, servicio
    └── mercaderia/      # Mercadería: entidad, DAO, schema, servicio
"""

from .base import Entidad
from .enums import TipoPersona
from .persona import (
    Persona,
    PersonaFisica,
    PersonaJuridica,
    PersonaDAO,
    PersonaIn,
    PersonaOut,
    PersonaService,
    PersonaError,
)
from .mercaderia import (
    Mercaderia,
    MercaderiaDAO,
    MercaderiaIn,
    MercaderiaOut,
    MercaderiaService,
    MercaderiaError,
)

__all__ = [
    # Base
    "Entidad",
    # Enums
    "TipoPersona",
    # Persona
    "Persona",
    "PersonaFisica",
    "PersonaJuridica",
    "PersonaDAO",
    "PersonaIn",
    "PersonaOut",
    "PersonaService",
    "PersonaError",
    # Mercadería
    "Mercaderia",
    "MercaderiaDAO",
    "MercaderiaIn",
    "MercaderiaOut",
    "MercaderiaService",
    "MercaderiaError",
]
