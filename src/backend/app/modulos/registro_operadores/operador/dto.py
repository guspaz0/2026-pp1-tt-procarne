"""DTOs (schemas Pydantic) de ``Operador``.

- ``OperadorIn``  — request (creación de un operador).
- ``OperadorOut`` — response (representación de salida).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field, model_validator


class OperadorIn(BaseModel):
    """DTO de entrada para crear un operador (sucursal/establecimiento).

    El CUIT vive en ``personas.identificador``: si el alta no trae
    ``persona_id``, se crea/busa la persona titular por CUIT.
    """

    cuit: Optional[str] = Field(None, description="CUIT de la persona titular (13 dígitos); se usa solo para crear/resolver la persona si no se trae persona_id")
    razon_social: str = Field(..., description="Razón social")
    tipo: str = Field(..., description="Tipo de operador (PRODUCTOR, FRIGORIFICO, etc.)")
    persona_id: Optional[int] = Field(None, description="ID de la persona (entidad legal padre)")
    categoria: Optional[str] = Field(None, description="Categoría según especificación (SALA_DE_DESPOSTE, CARNICERIAS, etc.)")
    domicilio_comercial: Optional[str] = Field(None, description="Domicilio comercial de esta sucursal")
    telefono: Optional[str] = Field(None, description="Teléfono")
    email: Optional[str] = Field(None, description="Email")


class OperadorOut(BaseModel):
    """DTO de salida de un operador (sucursal/establecimiento).

    El CUIT no se guarda en ``operadores``: se infiere de
    ``persona.identificador`` vía la relación ``persona_id``
    (1 persona : N operadores, el identificador es único por persona).
    """

    id: int
    persona_id: int
    razon_social: Optional[str]
    domicilio_comercial: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    tipo: str
    categoria: Optional[str]
    estado_registral: str
    alta_fecha: Optional[datetime]
    baja_fecha: Optional[datetime]
    creado_en: datetime

    cuit: Optional[str] = Field(None, description="CUIT, inferido de persona.identificador")

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _inferir_cuit(cls, data):
        """Infere el CUIT desde la relación ``persona`` del objeto ORM.

        El CUIT no se guarda en ``operadores``: vive en
        ``personas.identificador``. Si el input es un objeto ORM con la
        relación ``persona`` cargada, se extrae el identificador. Si la
        relación no está cargada (lazy load en instancia desvinculada),
        se deja el CUIT en ``None``.
        """
        if isinstance(data, dict):
            return data
        try:
            persona = data.persona
        except Exception:
            persona = None
        if persona is not None:
            identificador = getattr(persona, "identificador", None)
            if identificador is not None:
                attrs = {k: getattr(data, k, None) for k in cls.model_fields}
                attrs["cuit"] = identificador
                return attrs
        return data
