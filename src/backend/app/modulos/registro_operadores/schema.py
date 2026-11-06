"""Schemas (DTOs) del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ROCCAOperadorIn(BaseModel):
    """DTO de entrada para crear un operador."""

    cuit: str = Field(..., description="CUIT del operador (13 dígitos)")
    razon_social: str = Field(..., description="Razón social")
    tipo: str = Field(..., description="Tipo de operador (PRODUCTOR, FRIGORIFICO, etc.)")
    categoria: Optional[str] = Field(None, description="Categoría según especificación (SALA_DE_DESPOSTE, CARNICERIAS, etc.)")
    domicilio: Optional[str] = Field(None, description="Domicilio")
    domicilio_fiscal: Optional[str] = Field(None, description="Domicilio fiscal")
    telefono: Optional[str] = Field(None, description="Teléfono")
    email: Optional[str] = Field(None, description="Email")


class ROCCAOperadorOut(BaseModel):
    """DTO de salida de un operador."""

    id: int
    cuit: str
    razon_social: str
    domicilio: Optional[str]
    domicilio_fiscal: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    tipo: str
    categoria: Optional[str]
    estado_registral: str
    alta_fecha: Optional[datetime]
    baja_fecha: Optional[datetime]
    creado_en: datetime

    model_config = {"from_attributes": True}


class HabilitacionIn(BaseModel):
    """DTO de entrada para crear una habilitación."""

    actividad: str = Field(..., description="Actividad habilitada")
    fecha_vencimiento: Optional[datetime] = Field(None, description="Fecha de vencimiento")


class HabilitacionOut(BaseModel):
    """DTO de salida de una habilitación."""

    id: int
    operador_id: int
    actividad: str
    estado: str
    fecha_habilitacion: Optional[datetime]
    fecha_vencimiento: Optional[datetime]

    model_config = {"from_attributes": True}


class InscripcionIn(BaseModel):
    """DTO de entrada para crear una inscripción."""

    tipo: str = Field("PRINCIPAL", description="Tipo de inscripción (PRINCIPAL, SECUNDARIA)")
    numero_inscripcion: Optional[str] = Field(None, description="Número de inscripción")


class InscripcionOut(BaseModel):
    """DTO de salida de una inscripción."""

    id: int
    operador_id: int
    tipo: str
    fecha_inscripcion: Optional[datetime]
    numero_inscripcion: Optional[str]

    model_config = {"from_attributes": True}


class DomicilioOperativoIn(BaseModel):
    """DTO de entrada para crear un domicilio operativo."""

    direccion: str = Field(..., description="Dirección")
    localidad: Optional[str] = Field(None, description="Localidad")
    provincia: Optional[str] = Field(None, description="Provincia")
    codigo_postal: Optional[str] = Field(None, description="Código postal")
    es_principal: bool = Field(False, description="¿Es el domicilio principal?")


class DomicilioOperativoOut(BaseModel):
    """DTO de salida de un domicilio operativo."""

    id: int
    operador_id: int
    tipo: str
    direccion: str
    localidad: Optional[str]
    provincia: Optional[str]
    codigo_postal: Optional[str]
    es_principal: bool

    model_config = {"from_attributes": True}


class RequisitoInscripcionIn(BaseModel):
    """DTO de entrada para registrar un requisito de inscripción."""

    codigo: str = Field(..., description="Código del requisito (ej: INGRESOS_BRUTOS, REGISTRO_NACIONAL_FRIGORIFICOS)")
    descripcion: Optional[str] = Field(None, description="Descripción del requisito")
    es_general: bool = Field(False, description="¿Es un requisito general (común a todas las categorías)?")
    cumplido: bool = Field(False, description="¿Está cumplido?")
    observaciones: Optional[str] = Field(None, description="Observaciones")


class RequisitoInscripcionOut(BaseModel):
    """DTO de salida de un requisito de inscripción."""

    id: int
    operador_id: int
    codigo: str
    descripcion: Optional[str]
    es_general: bool
    cumplido: bool
    fecha_cumplimiento: Optional[datetime]
    observaciones: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}
