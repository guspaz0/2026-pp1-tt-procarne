"""Submódulo de la persona (física o jurídica)."""

from .dao import Persona as PersonaORM
from .dao import PersonaDAO
from .entidad import Persona, PersonaFisica, PersonaJuridica
from .schema import PersonaIn, PersonaOut
from .servicio import PersonaError, PersonaService

__all__ = [
    "Persona",
    "PersonaFisica",
    "PersonaJuridica",
    "PersonaORM",
    "PersonaDAO",
    "PersonaIn",
    "PersonaOut",
    "PersonaService",
    "PersonaError",
]
