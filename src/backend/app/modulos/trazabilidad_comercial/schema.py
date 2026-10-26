"""Schemas (DTOs) del Módulo II — Trazabilidad Comercial."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class RegistroTrazabilidadIn(BaseModel):
    """DTO de entrada para crear un registro de trazabilidad."""

    tipo_ingreso: str = Field(..., description="Tipo de ingreso (PRODUCCION_PROPIA, COMPRA, etc.)")
    especie: str = Field(..., description="Especie animal (BOVINO, PORCINO, etc.)")
    cantidad: Decimal = Field(..., description="Cantidad de unidades")
    peso_kg: Decimal = Field(..., description="Peso en kilos")
    origen_cuit: str = Field(..., description="CUIT del origen")
    destino_cuit: str = Field(..., description="CUIT del destino")
    tipo_destino: str = Field(..., description="Tipo de destino (FRIGORIFICO, CARNICERIA, etc.)")
    fecha_ingreso: datetime = Field(..., description="Fecha de ingreso")
    numero_remito: Optional[str] = Field(None, description="Número de remito")
    numero_dte: Optional[str] = Field(None, description="Número de DTE")
    observaciones: Optional[str] = Field(None, description="Observaciones")


class RegistroTrazabilidadOut(BaseModel):
    """DTO de salida de un registro de trazabilidad."""

    id: int
    tipo_ingreso: str
    especie: str
    cantidad: Decimal
    peso_kg: Decimal
    origen_cuit: str
    destino_cuit: str
    tipo_destino: str
    estado: str
    fecha_ingreso: datetime
    numero_remito: Optional[str]
    numero_dte: Optional[str]
    observaciones: Optional[str]
    creado_en: datetime

    model_config = {"from_attributes": True}
