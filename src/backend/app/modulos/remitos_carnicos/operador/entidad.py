"""Entidades de operador de la cadena cárnica.

Define :class:`Operador` (clase base) y sus participantes del traslado
(:class:`Titular`, :class:`Depositario`, :class:`Destinatario`,
:class:`Transportista`) como subclases de :class:`ParticipanteRemito`.
"""

from __future__ import annotations

from typing import Optional

from ..base import Entidad
from modulos.genericos.persona.entidad import PersonaJuridica


class Operador(PersonaJuridica):
    """Operador de la cadena cárnica (padrón AFIP).

    Extiende :class:`PersonaJuridica` (identificado por su CUIT) y le
    añade el campo ``razon_social`` y el domicilio fiscal. Puede cumplir
    distintos roles en un remito: titular de la mercadería,
    depositario/autorizante, destinatario o transportista.
    """

    def __init__(
        self,
        cuit: str,
        razon_social: str,
        domicilio: Optional[str] = None,
        domicilio_fiscal: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        super().__init__(
            cuit=cuit,
            nombre=razon_social,
            domicilio=domicilio,
            telefono=telefono,
            email=email,
        )
        self.razon_social = razon_social
        self.domicilio_fiscal = domicilio_fiscal

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["razon_social"] = self.razon_social
        base["domicilio_fiscal"] = self.domicilio_fiscal
        return base

    def __repr__(self) -> str:
        return f"<Operador cuit={self.cuit} razon_social={self.razon_social!r}>"


class ParticipanteRemito(Entidad):
    """Clase abstracta de un participante del traslado.

    Envuelve un :class:`Operador` y le asigna un rol dentro del remito
    (titular, depositario, destinatario o transportista).
    """

    def __init__(self, operador: Operador) -> None:
        super().__init__()
        self.operador = operador

    @property
    def cuit(self) -> str:
        return self.operador.cuit

    @property
    def razon_social(self) -> str:
        return self.operador.razon_social

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "rol": self.__class__.__name__,
            "operador": self.operador.to_dict(),
        }


class Titular(ParticipanteRemito):
    """Titular de la mercadería (sector B)."""

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["rol"] = "TITULAR"
        return base


class Depositario(ParticipanteRemito):
    """Depositario/autorizante (sector C). Presente en casos 02, 03, 05, 06."""

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["rol"] = "DEPOSITARIO"
        return base


class Destinatario(ParticipanteRemito):
    """Destinatario (sector D). Ausente en casos de reparto (04–06) y 07."""

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["rol"] = "DESTINATARIO"
        return base


class Transportista(ParticipanteRemito):
    """Transportista (sector E). Siempre presente; incluye datos de chofer y vehículo."""

    def __init__(
        self,
        operador: Operador,
        chofer_apellido_nombre: Optional[str] = None,
        chofer_documento: Optional[str] = None,
        dominio_vehiculo: Optional[str] = None,
    ) -> None:
        super().__init__(operador)
        self.chofer_apellido_nombre = chofer_apellido_nombre
        self.chofer_documento = chofer_documento
        self.dominio_vehiculo = dominio_vehiculo

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["rol"] = "TRANSPORTISTA"
        base["chofer_apellido_nombre"] = self.chofer_apellido_nombre
        base["chofer_documento"] = self.chofer_documento
        base["dominio_vehiculo"] = self.dominio_vehiculo
        return base
