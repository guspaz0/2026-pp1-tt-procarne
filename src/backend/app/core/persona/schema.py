"""Schemas (DTOs) de la persona."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from ..enums import TipoPersona


class PersonaIn(BaseModel):
    """Datos de entrada para crear una persona.

    ``tipo`` indica si es física (``identificador`` = DNI) o jurídica
    (``identificador`` = CUIT).
    """

    tipo: TipoPersona
    identificador: str
    nombre: str
    cuit: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

    @model_validator(mode="after")
    def _validar_identificador(self) -> "PersonaIn":
        if self.tipo is TipoPersona.PF and not self.identificador.isdigit():
            raise ValueError("El DNI debe ser numérico")
        if self.tipo is TipoPersona.PJ:
            if not self.identificador.isdigit():
                raise ValueError("El CUIT debe ser numérico")
            if len(self.identificador) != 11:
                raise ValueError("El CUIT debe tener 11 dígitos")
            if self.cuit is not None:
                raise ValueError("Una persona jurídica no admite campo cuit adicional")
        if self.tipo is TipoPersona.PF and self.cuit is not None:
            if not self.cuit.isdigit() or len(self.cuit) != 11:
                raise ValueError("El CUIT debe tener 11 dígitos")
        return self


class PersonaOut(BaseModel):
    """DTO de salida de la persona."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoPersona
    identificador: str
    nombre: str
    cuit: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
