"""Schemas (DTOs) del Módulo II — Trazabilidad Comercial (ROCCA)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import Especie, EstadoTrazabilidad, TipoDestino, TipoIngreso


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------


class RegistroTrazabilidadIn(BaseModel):
    """Datos de entrada para registrar un movimiento de trazabilidad."""

    tipo_ingreso: TipoIngreso = Field(
        description="Tipo de ingreso (INGRESO_EXTRAPROVINCIAL o FAENA_PROVINCIAL)"
    )
    cantidad_kg: float = Field(gt=0, description="Cantidad de kilogramos")
    especie: Especie = Field(description="Especie de la carne")

    # Origen
    origen_provincia: Optional[str] = Field(
        default=None, description="Provincia de origen (si es extraprovincial)"
    )
    origen_localidad: Optional[str] = None
    establecimiento_faena: Optional[str] = Field(
        default=None, description="Establecimiento de faena (nombre o código)"
    )

    # Documentos
    numero_dte: Optional[str] = Field(
        default=None, description="Número de Documento de Tránsito Electrónico"
    )
    numero_remito: Optional[str] = Field(
        default=None, description="Número de remito (REC)"
    )

    # Destino comercial
    destino_tipo: Optional[TipoDestino] = Field(
        default=None, description="Tipo de destino comercial"
    )
    destino_cuit: Optional[str] = Field(
        default=None, description="CUIT del operador destino"
    )
    destino_razon_social: Optional[str] = None

    # Metadatos
    fecha_ingreso: Optional[date] = Field(
        default=None, description="Fecha del ingreso (por defecto hoy)"
    )
    observaciones: Optional[str] = None

    @model_validator(mode="after")
    def _validar_destino_cuit(self) -> "RegistroTrazabilidadIn":
        if self.destino_cuit is not None:
            if not self.destino_cuit.isdigit() or len(self.destino_cuit) != 11:
                raise ValueError("El CUIT de destino debe tener 11 dígitos")
        return self

    @model_validator(mode="after")
    def _validar_ingreso_extraprovincial(self) -> "RegistroTrazabilidadIn":
        if self.tipo_ingreso is TipoIngreso.INGRESO_EXTRAPROVINCIAL:
            if self.origen_provincia is None:
                raise ValueError(
                    "El ingreso extraprovincial requiere indicar la provincia de origen"
                )
        return self


# ---------------------------------------------------------------------------
# Salidas
# ---------------------------------------------------------------------------


class RegistroTrazabilidadOut(BaseModel):
    """DTO de salida del registro de trazabilidad comercial."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_ingreso: TipoIngreso
    cantidad_kg: float
    especie: Especie

    origen_provincia: Optional[str] = None
    origen_localidad: Optional[str] = None
    establecimiento_faena: Optional[str] = None

    numero_dte: Optional[str] = None
    numero_remito: Optional[str] = None

    destino_tipo: Optional[TipoDestino] = None
    destino_cuit: Optional[str] = None
    destino_razon_social: Optional[str] = None

    estado: EstadoTrazabilidad
    fecha_registro: date
    fecha_ingreso: Optional[date] = None
    observaciones: Optional[str] = None
    creado_en: datetime

    @classmethod
    def from_orm(cls, registro) -> "RegistroTrazabilidadOut":
        return cls(
            id=registro.id,
            tipo_ingreso=TipoIngreso(registro.tipo_ingreso),
            cantidad_kg=registro.cantidad_kg,
            especie=Especie(registro.especie),
            origen_provincia=registro.origen_provincia,
            origen_localidad=registro.origen_localidad,
            establecimiento_faena=registro.establecimiento_faena,
            numero_dte=registro.numero_dte,
            numero_remito=registro.numero_remito,
            destino_tipo=(
                TipoDestino(registro.destino_tipo) if registro.destino_tipo else None
            ),
            destino_cuit=registro.destino_cuit,
            destino_razon_social=registro.destino_razon_social,
            estado=EstadoTrazabilidad(registro.estado),
            fecha_registro=registro.fecha_registro,
            fecha_ingreso=registro.fecha_ingreso,
            observaciones=registro.observaciones,
            creado_en=registro.creado_en,
        )
