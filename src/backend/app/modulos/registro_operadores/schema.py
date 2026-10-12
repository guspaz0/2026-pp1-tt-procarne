"""Schemas (DTOs) del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import EstadoRegistral, TipoDomicilio, TipoInscripcion, TipoOperador


# ---------------------------------------------------------------------------
# Entradas (anidadas)
# ---------------------------------------------------------------------------


class HabilitacionIn(BaseModel):
    """Datos de una habilitación del operador."""

    tipo: str = Field(description="Tipo de habilitación (ej. 'Sanitaria', 'Comercial')")
    numero: Optional[str] = None
    autoridad: Optional[str] = Field(
        default=None, description="Autoridad que la emite (ej. 'ProCarne Fiscalización')"
    )
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: str = "VIGENTE"


class InscripcionIn(BaseModel):
    """Datos de una inscripción nacional o provincial."""

    tipo: TipoInscripcion
    organismo: str = Field(description="Ej. 'RFOCB', 'ARCA', 'SIGSA', 'DGAyG'")
    numero: Optional[str] = None
    fecha_inscripcion: Optional[date] = None
    estado: str = "ACTIVA"


class DomicilioOperativoIn(BaseModel):
    """Datos de un domicilio operativo."""

    tipo: TipoDomicilio = TipoDomicilio.PRINCIPAL
    calle: str
    numero: Optional[str] = None
    localidad: Optional[str] = None
    departamento: Optional[str] = None
    provincia: Optional[str] = "Santiago del Estero"
    codigo_postal: Optional[str] = None
    activo: bool = True


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------


class ROCCAOperadorIn(BaseModel):
    """Datos de entrada para registrar un operador en el ROCCA."""

    cuit: str = Field(description="CUIT de 11 dígitos")
    razon_social: str
    tipo: TipoOperador
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    estado_registral: EstadoRegistral = EstadoRegistral.ACTIVO
    observaciones: Optional[str] = None
    habilitaciones: list[HabilitacionIn] = []
    inscripciones: list[InscripcionIn] = []
    domicilios: list[DomicilioOperativoIn] = []

    @model_validator(mode="after")
    def _validar_cuit(self) -> "ROCCAOperadorIn":
        if not self.cuit.isdigit() or len(self.cuit) != 11:
            raise ValueError("El CUIT debe tener 11 dígitos")
        return self

    @model_validator(mode="after")
    def _validar_domicilios(self) -> "ROCCAOperadorIn":
        principales = [
            d for d in self.domicilios if d.tipo is TipoDomicilio.PRINCIPAL and d.activo
        ]
        if len(principales) > 1:
            raise ValueError("Solo se admite un domicilio operativo principal activo")
        return self


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------


class HabilitacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    numero: Optional[str] = None
    autoridad: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: str


class InscripcionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoInscripcion
    organismo: str
    numero: Optional[str] = None
    fecha_inscripcion: Optional[date] = None
    estado: str


class DomicilioOperativoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoDomicilio
    calle: str
    numero: Optional[str] = None
    localidad: Optional[str] = None
    departamento: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    activo: bool


class ROCCAOperadorOut(BaseModel):
    """DTO de salida del operador del Registro Provincial."""

    id: int
    cuit: str
    razon_social: str
    tipo: TipoOperador
    estado_registral: EstadoRegistral
    fecha_inscripcion: date
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    observaciones: Optional[str] = None
    habilitaciones: list[HabilitacionOut] = []
    inscripciones: list[InscripcionOut] = []
    domicilios: list[DomicilioOperativoOut] = []

    @classmethod
    def from_orm(cls, operador) -> "ROCCAOperadorOut":
        return cls(
            id=operador.id,
            cuit=operador.cuit,
            razon_social=operador.razon_social,
            tipo=TipoOperador(operador.tipo),
            estado_registral=EstadoRegistral(operador.estado_registral),
            fecha_inscripcion=operador.fecha_inscripcion,
            domicilio=operador.domicilio,
            telefono=operador.telefono,
            email=operador.email,
            observaciones=operador.observaciones,
            habilitaciones=[
                HabilitacionOut.model_validate(h) for h in operador.habilitaciones
            ],
            inscripciones=[
                InscripcionOut.model_validate(i) for i in operador.inscripciones
            ],
            domicilios=[
                DomicilioOperativoOut.model_validate(d) for d in operador.domicilios
            ],
        )
