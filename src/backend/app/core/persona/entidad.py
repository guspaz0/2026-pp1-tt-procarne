"""Entidades de persona del módulo genérico.

Define :class:`Persona` (clase abstracta) y sus subclases concretas:

- :class:`PersonaFisica` — identificada por DNI, puede tener CUIT
  (por ejemplo, monotributistas)
- :class:`PersonaJuridica` — identificada únicamente por CUIT
"""

from __future__ import annotations

from typing import Optional

from ..base import Entidad
from ..enums import TipoPersona


class Persona(Entidad):
    """Clase abstracta de una persona (física o jurídica).

    Es la entidad base de cualquier actor del sistema que no sea un
    operador de la cadena cárnica (por ejemplo, usuarios del sistema o
    terceros de otros módulos).
    """

    @property
    def tipo(self) -> TipoPersona:
        """Tipo de persona (física o jurídica)."""
        raise NotImplementedError

    @property
    def identificador(self) -> str:
        """Documento que identifica a la persona (DNI o CUIT)."""
        raise NotImplementedError

    def __init__(
        self,
        nombre: str,
        domicilio: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.nombre = nombre
        self.domicilio = domicilio
        self.telefono = telefono
        self.email = email

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "identificador": self.identificador,
            "nombre": self.nombre,
            "domicilio": self.domicilio,
            "telefono": self.telefono,
            "email": self.email,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} nombre={self.nombre!r}>"


class PersonaFisica(Persona):
    """Persona física, identificada por su DNI.

    Puede además tener un CUIT (por ejemplo, monotributistas o
    responsables inscriptos en AFIP).
    """

    tipo = TipoPersona.PF

    def __init__(
        self,
        dni: str,
        nombre: str,
        cuit: Optional[str] = None,
        domicilio: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        super().__init__(nombre, domicilio, telefono, email)
        self.dni = dni
        self.cuit = cuit

    @property
    def identificador(self) -> str:
        return self.dni

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["dni"] = self.dni
        base["cuit"] = self.cuit
        return base


class PersonaJuridica(Persona):
    """Persona jurídica, identificada únicamente por su CUIT."""

    tipo = TipoPersona.PJ

    def __init__(
        self,
        cuit: str,
        nombre: str,
        domicilio: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        super().__init__(nombre, domicilio, telefono, email)
        self.cuit = cuit

    @property
    def identificador(self) -> str:
        return self.cuit

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["cuit"] = self.cuit
        return base
