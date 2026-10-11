"""Schemas (DTOs) del remito electrónico cárnico."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from ..enums import CasoRemito, TipoMovimiento


class RenglonRemitoIn(BaseModel):
    """Renglón de mercadería para la creación de un remito."""

    codigo_afip: str = Field(..., description="Código AFIP de la mercadería")
    unidades: Decimal = Field(default=Decimal("0"), ge=0)
    kilos: Decimal = Field(default=Decimal("0"), ge=0)
    numero_tropa: Optional[str] = Field(
        default=None, description="N° de tropa (obligatorio si la mercadería lo requiere)"
    )


class RemitoCarnicoIn(BaseModel):
    """Datos de entrada para la creación de un Remito Electrónico Cárnico."""

    punto_emision: str
    numero_comprobante: str
    caso: CasoRemito
    tipo_movimiento: TipoMovimiento
    fecha_emision: datetime
    fecha_vencimiento: datetime
    titular_cuit: str
    transportista_cuit: str
    depositario_cuit: Optional[str] = None
    destinatario_cuit: Optional[str] = None
    chofer_apellido_nombre: Optional[str] = None
    chofer_documento: Optional[str] = None
    dominio_vehiculo: Optional[str] = None
    renglones: list[RenglonRemitoIn] = Field(..., min_length=1)
    hoja: int = Field(default=1, ge=1)
    total_hojas: int = Field(default=1, ge=1)


class ParticipanteOut(BaseModel):
    """DTO de un participante del traslado."""

    rol: str
    cuit: str
    razon_social: str
    domicilio: Optional[str] = None


class RenglonRemitoOut(BaseModel):
    """DTO de salida de un renglón."""

    codigo_afip: str
    descripcion: str
    unidades: Decimal
    kilos: Decimal
    numero_tropa: Optional[str] = None


class RemitoCarnicoOut(BaseModel):
    """DTO de salida del remito electrónico cárnico."""

    id: Optional[int] = None
    codigo_remito: str
    caso: int
    tipo_movimiento: str
    estado: str
    fecha_emision: datetime
    fecha_vencimiento: datetime
    hoja: int
    total_hojas: int
    titular: ParticipanteOut
    depositario: Optional[ParticipanteOut] = None
    destinatario: Optional[ParticipanteOut] = None
    transportista: ParticipanteOut
    renglones: list[RenglonRemitoOut]
    total_kilos: Decimal
    total_unidades: Decimal
