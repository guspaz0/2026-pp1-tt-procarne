"""Entidad de dominio: Persona (física o jurídica).

Representa a una persona en el sistema, con sus datos identificatorios
(documento, nombre/razón social) y domicilio.
"""

from __future__ import annotations

from core.base import Entidad
from core.enums import TipoPersona


class Persona(Entidad):
    """Persona física o jurídica.

    Campos:
        tipo: ``FISICA`` o ``JURIDICA``.
        tipo_documento: tipo de documento (DNI, CUIT, etc.).
        identificador: número de documento.
        nombre: nombre (persona física) o razón social (persona jurídica).
    """

    def __init__(
        self,
        tipo: TipoPersona | str,
        tipo_documento: str,
        identificador: str,
        nombre: str,
    ) -> None:
        super().__init__()
        self.tipo = tipo
        self.tipo_documento = tipo_documento
        self.identificador = identificador
        self.nombre = nombre

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo,
            "tipo_documento": self.tipo_documento,
            "identificador": self.identificador,
            "nombre": self.nombre,
        }


class PersonaFisica(Persona):
    """Persona física (nombre y apellido, documento)."""

    def __init__(
        self,
        apellido: str,
        nombre: str,
        tipo_documento: str = "DNI",
        identificador: str = "",
    ) -> None:
        super().__init__(
            tipo=TipoPersona.FISICA,
            tipo_documento=tipo_documento,
            identificador=identificador,
            nombre=f"{apellido}, {nombre}",
        )
        self.apellido = apellido
        self.nombre_pila = nombre


class PersonaJuridica(Persona):
    """Persona jurídica (razón social, CUIT)."""

    def __init__(
        self,
        razon_social: str,
        cuit: str,
    ) -> None:
        super().__init__(
            tipo=TipoPersona.JURIDICA,
            tipo_documento="CUIT",
            identificador=cuit,
            nombre=razon_social,
        )
        self.razon_social = razon_social
        self.cuit = cuit
