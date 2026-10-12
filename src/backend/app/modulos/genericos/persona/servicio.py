"""Servicio de negocio de la persona."""

from __future__ import annotations

from .dao import Persona, PersonaDAO
from .schema import PersonaIn, PersonaOut


class PersonaError(Exception):
    """Error de negocio del módulo de personas."""


class PersonaService:
    """Caso de uso: gestión de personas (físicas y jurídicas)."""

    def __init__(self, dao: PersonaDAO) -> None:
        self._dao = dao

    def crear(self, datos: PersonaIn) -> PersonaOut:
        existente = self._dao.obtener_por_identificador(datos.identificador)
        if existente is not None:
            raise PersonaError(
                f"Persona ya existe: {datos.tipo.value} {datos.identificador}"
            )

        persona = Persona(
            tipo=datos.tipo.value,
            identificador=datos.identificador,
            nombre=datos.nombre,
            cuit=datos.cuit,
            domicilio=datos.domicilio,
            telefono=datos.telefono,
            email=datos.email,
        )
        guardado = self._dao.guardar(persona)
        return PersonaOut.model_validate(guardado)

    def obtener(self, identificador: str) -> PersonaOut:
        persona = self._dao.obtener_por_identificador(identificador)
        if persona is None:
            raise PersonaError(f"Persona no encontrada: {identificador}")
        return PersonaOut.model_validate(persona)

    def listar(self, limite: int = 200, offset: int = 0) -> list[PersonaOut]:
        personas = self._dao.listar(limite=limite, offset=offset)
        return [PersonaOut.model_validate(p) for p in personas]
