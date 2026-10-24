"""Núcleo del dominio: contratos (tipos) y datos transversales.

Este paquete contiene lo que **no** es un módulo de negocio de la
especificación (Módulos I–VII), pero que varios módulos necesitan:

- **Contratos (tipos)** — :class:`DatabaseDAO`, :class:`PersonaRef`,
  :class:`MercaderiaRef`, :class:`PersonaDAO` (Protocol).
- **Persona** — entidad, ORM/DAO, schemas y servicio (física/jurídica).
- **Mercadería** — entidad, ORM/DAO, schemas y servicio (catálogo de
  códigos de mercadería, p. ej. códigos AFIP).

Los módulos de negocio dependen de estos componentes solo por sus
**tipos** (o por su ORM en el punto único de persistencia), sin acoplar
sus casos de uso.
"""

from .base import Entidad
from .contracts import DatabaseDAO, MercaderiaRef, PersonaDAO, PersonaRef
from .enums import TipoPersona
from .mercaderia import (
    Mercaderia,
    MercaderiaDAO,
    MercaderiaError,
    MercaderiaIn,
    MercaderiaOut,
    MercaderiaService,
)
from .persona import (
    Persona,
    PersonaDAO,
    PersonaError,
    PersonaFisica,
    PersonaIn,
    PersonaJuridica,
    PersonaOut,
    PersonaService,
)

# Colisión de nombres: ``PersonaDAO`` y ``MercaderiaDAO`` existen como
# Protocol en :mod:`core.contracts` y como clase concreta en los
# submódulos. Se exporta la clase concreta (la más usada); el Protocol
# sigue disponible como ``core.contracts.PersonaDAO``.
from .persona import PersonaDAO  # noqa: F811  (clase concreta, reemplaza al Protocol)
from .mercaderia import MercaderiaDAO  # noqa: F811

__all__ = [
    # Base
    "Entidad",
    # Contratos
    "DatabaseDAO",
    "PersonaRef",
    "MercaderiaRef",
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
