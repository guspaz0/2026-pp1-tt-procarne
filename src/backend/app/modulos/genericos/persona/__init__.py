"""Submódulo de la persona (física o jurídica)."""

from .entidad import Persona, PersonaFisica, PersonaJuridica
from .dao import Persona as PersonaORM, PersonaDAO
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
