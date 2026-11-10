"""Schemas (DTOs) del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ROCCAOperadorIn(BaseModel):
    """DTO de entrada para crear un operador (sucursal/establecimiento)."""

    cuit: str = Field(..., description="CUIT del operador (13 dígitos)")
    razon_social: str = Field(..., description="Razón social")
    tipo: str = Field(..., description="Tipo de operador (PRODUCTOR, FRIGORIFICO, etc.)")
    persona_id: Optional[int] = Field(None, description="ID de la persona (entidad legal padre)")
    categoria: Optional[str] = Field(None, description="Categoría según especificación (SALA_DE_DESPOSTE, CARNICERIAS, etc.)")
    domicilio_comercial: Optional[str] = Field(None, description="Domicilio comercial de esta sucursal")
    telefono: Optional[str] = Field(None, description="Teléfono")
    email: Optional[str] = Field(None, description="Email")


class ROCCAOperadorOut(BaseModel):
    """DTO de salida de un operador (sucursal/establecimiento)."""

    id: int
    persona_id: int
    cuit: str
    razon_social: str
    domicilio_comercial: Optional[str]
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


class CertificadoOut(BaseModel):
    """DTO de salida de un certificado de habilitación.

    ``estado`` es el estado almacenado en la base de datos.
    ``estado_efectivo`` es el estado calculado: si el certificado está ACTIVO
    pero su fecha_vencimiento ya pasó, se reporta como VENCIDO.
    """

    id: int
    operador_id: int
    numero_certificado: str
    tipo_certificado: str
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime]
    actividades_economicas: Optional[str]
    observaciones: Optional[str]
    estado: str
    estado_efectivo: str = ""
    creado_en: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_certificado(cls, cert) -> "CertificadoOut":
        """Construye el DTO calculando el estado efectivo.

        Si el certificado está ACTIVO pero su fecha_vencimiento ya pasó,
        el estado efectivo se reporta como VENCIDO.
        """
        from modulos.registro_operadores.enums import EstadoCertificado
        from datetime import datetime as dt, timezone as tz

        estado = cert.estado
        estado_efectivo = estado
        if estado == EstadoCertificado.ACTIVO.value and cert.fecha_vencimiento is not None:
            venc = cert.fecha_vencimiento
            # Normalizar a aware UTC para la comparación
            if venc.tzinfo is None:
                venc = venc.replace(tzinfo=tz.utc)
            if venc < dt.now(tz.utc):
                estado_efectivo = EstadoCertificado.VENCIDO.value

        return cls(
            id=cert.id,
            operador_id=cert.operador_id,
            numero_certificado=cert.numero_certificado,
            tipo_certificado=cert.tipo_certificado,
            fecha_emision=cert.fecha_emision,
            fecha_vencimiento=cert.fecha_vencimiento,
            actividades_economicas=cert.actividades_economicas,
            observaciones=cert.observaciones,
            estado=estado,
            estado_efectivo=estado_efectivo,
            creado_en=cert.creado_en,
        )


class CertificadoSuspenderIn(BaseModel):
    """DTO de entrada para suspender un certificado (acción de supervisor)."""

    observaciones: Optional[str] = Field(None, description="Motivo de la suspensión")


class GrupoActividadOut(BaseModel):
    """DTO de salida de un grupo de actividad económica."""

    id: int
    codigo: str
    descripcion: str

    model_config = {"from_attributes": True}


class SubgrupoActividadOut(BaseModel):
    """DTO de salida de un subgrupo de actividad económica."""

    id: int
    codigo: str
    descripcion: str
    grupo_id: int

    model_config = {"from_attributes": True}


class ActividadEconomicaOut(BaseModel):
    """DTO de salida de una actividad económica."""

    id: int
    codigo: str
    descripcion: str
    alicuota: Optional[float]
    grupo_id: int
    subgrupo_id: Optional[int]

    model_config = {"from_attributes": True}


class CertificadoIn(BaseModel):
    """DTO de entrada para crear un certificado."""

    numero_certificado: str = Field(..., description="Número de certificado (ej: F-102-1001)")
    tipo_certificado: str = Field("HABILITACION", description="Tipo: HABILITACION, INSCRIPCION, etc.")
    fecha_emision: datetime = Field(..., description="Fecha de emisión")
    fecha_vencimiento: Optional[datetime] = Field(None, description="Fecha de vencimiento")
    actividades_economicas: Optional[str] = Field(None, description="Códigos/descripciones de actividades económicas")
    observaciones: Optional[str] = Field(None, description="Observaciones")


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
