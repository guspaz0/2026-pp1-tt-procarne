"""Servicio de negocio de la persona.

Casos de uso:
- Crear una persona (física o jurídica).
- Buscar por documento.
- Listar personas.
"""

from __future__ import annotations

from core.persona.dao import Persona, PersonaDAO
from core.persona.schema import PersonaIn, PersonaOut


class PersonaError(Exception):
    """Error de negocio del servicio de personas."""


class PersonaService:
    """Servicio de negocio de personas."""

    def __init__(self, dao: PersonaDAO) -> None:
        self._dao = dao

    def crear_persona(self, data: PersonaIn) -> PersonaOut:
        """Crea una persona y devuelve su representación de salida."""
        existente = self._dao.obtener_por_documento(data.tipo_documento, data.identificador)
        if existente is not None:
            raise PersonaError(
                f"Ya existe una persona con documento {data.tipo_documento} {data.identificador}"
            )
        persona = self._dao.crear(
            tipo=data.tipo,
            tipo_documento=data.tipo_documento,
            identificador=data.identificador,
            nombre=data.nombre,
            domicilio=data.domicilio,
        )
        return PersonaOut.model_validate(persona)

    def obtener_por_documento(self, tipo_documento: str, identificador: str) -> PersonaOut | None:
        """Busca una persona por su documento."""
        persona = self._dao.obtener_por_documento(tipo_documento, identificador)
        return PersonaOut.model_validate(persona) if persona else None

    def listar(self) -> list[PersonaOut]:
        """Lista todas las personas."""
        return [PersonaOut.model_validate(p) for p in self._dao.listar()]
