"""DTOs (schemas Pydantic) de ``Operador``.

- ``OperadorIn``  — request (creación de un operador).
- ``OperadorOut`` — response (representación de salida).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field, model_validator


class DomicilioIn(BaseModel):
    """DTO de entrada para un domicilio estructurado."""

    id: Optional[int] = Field(None, description="ID de un domicilio existente (si se reutiliza)")
    calle: str = Field(..., description="Nombre de la calle")
    numero: Optional[str] = Field(None, description="Número (puede ser rango: 433/59)")
    localidad: str = Field(..., description="Localidad")
    departamento: str = Field(..., description="Departamento provincial")
    provincia: str = Field("Santiago del Estero", description="Provincia")
    codigo_postal: Optional[str] = Field(None, description="Código postal")


class OperadorIn(BaseModel):
    """DTO de entrada para crear un operador (sucursal/establecimiento).

    El CUIT vive en ``personas.identificador``: si el alta no trae
    ``persona_id``, se crea/busa la persona titular por CUIT.
    """

    cuit: Optional[str] = Field(None, description="CUIT de la persona titular (13 dígitos); se usa solo para crear/resolver la persona si no se trae persona_id")
    establecimiento_fantasia: str = Field(..., description="Nombre de fantasía del establecimiento")
    persona_id: Optional[int] = Field(None, description="ID de la persona (entidad legal padre)")
    categoria: Optional[str] = Field(None, description="Categoría según especificación (SALA_DE_DESPOSTE, CARNICERIAS, etc.)")
    domicilio: Optional[DomicilioIn] = Field(None, description="Domicilio comercial de esta sucursal (estructurado)")
    tipos_carne: Optional[str] = Field(None, description="Tipos de carne comercializada (separados por comas: Bovina, Porcina, Ovino, etc.)")
    telefono: Optional[str] = Field(None, description="Teléfono")
    email: Optional[str] = Field(None, description="Email de contacto de la persona titular (se guarda en personas.email)")
    actividad_ids: Optional[list[int]] = Field(None, description="Ids del catálogo de actividades económicas que realiza el operador (N:M)")
    codigo_dgr: Optional[list[str]] = Field(None, description="Códigos DGR del catálogo (actividades_economicas.codigo) que realiza el operador; se resuelven a ids")
    codigo_afip: Optional[list[str]] = Field(None, description="Códigos AFIP/DGR enviados por el frontend (alias de codigo_dgr); se resuelven a ids")
    crear_cuenta: bool = Field(False, description="Si es True, se crea una cuenta de login para la persona con contraseña por defecto (CUIT/DNI). Solo para admin.")
    tipo_documento: Optional[str] = Field("CUIT", description="Tipo de documento de la persona: 'CUIT' o 'DNI'")
    documento_requisitos: Optional[list[str]] = Field(None, description="Lista de códigos de requisitos marcados como cumplidos por el operador.")


class DomicilioOut(BaseModel):
    """DTO de salida de un domicilio estructurado."""

    id: int
    calle: str
    numero: Optional[str]
    localidad: str
    departamento: str
    provincia: str
    codigo_postal: Optional[str]

    model_config = {"from_attributes": True}


class ArchivoOut(BaseModel):
    """DTO de salida de un archivo (documento subido)."""

    id: int
    nombre: str
    url: Optional[str] = Field(None, description="URL pública del archivo en storage")
    mime_type: str
    size_bytes: int

    model_config = {"from_attributes": True}


class RequisitoOperadorOut(BaseModel):
    """DTO de salida de un requisito de un operador (con estado y documentos)."""

    id: int
    requisito_categoria_id: int
    codigo: Optional[str] = Field(None, description="Código del requisito (ej: 'REQ_01')")
    nombre: Optional[str] = Field(None, description="Nombre del requisito")
    estado: str
    documentos: list[ArchivoOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class OperadorOut(BaseModel):
    """DTO de salida de un operador (sucursal/establecimiento).

    El CUIT no se guarda en ``operadores``: se infiere de
    ``persona.identificador`` vía la relación ``persona_id``
    (1 persona : N operadores, el identificador es único por persona).
    """

    id: int
    persona_id: int
    establecimiento_fantasia: Optional[str]
    domicilio: Optional[DomicilioOut] = Field(None, description="Domicilio comercial (estructurado)")
    domicilio_comercial: Optional[str] = Field(None, description="Domicilio comercial legible, construido por el DAO")
    tipos_carne: Optional[str] = Field(None, description="Tipos de carne comercializada (separados por comas)")
    telefono: Optional[str]
    categoria: Optional[str]
    estado_registral: str
    alta_fecha: Optional[datetime]
    baja_fecha: Optional[datetime]
    creado_en: datetime

    cuit: Optional[str] = Field(None, description="CUIT, inferido de persona.identificador")
    actividad_ids: list[int] = Field(default_factory=list, description="Ids del catálogo de actividades que realiza el operador (N:M)")
    requisitos: list[RequisitoOperadorOut] = Field(default_factory=list, description="Requisitos del operador con estado y documentos")

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _inferir_cuit(cls, data):
        """Infere el CUIT desde la relación ``persona`` del objeto ORM.

        El CUIT no se guarda en ``operadores``: vive en
        ``personas.identificador``. Si el input es un objeto ORM con la
        relación ``persona`` cargada, se extrae el identificador. Si el
        input es un dict que contiene una relación ``persona``, también
        se extrae. Si la relación no está cargada, se deja en ``None``.
        """
        if isinstance(data, dict):
            persona = data.get("persona")
            if persona is not None:
                identificador = getattr(persona, "identificador", None)
                if identificador is not None:
                    data["cuit"] = identificador
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
