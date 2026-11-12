# """Schemas (DTOs) del Remito Electrónico Cárnico."""

# from __future__ import annotations

# from datetime import datetime
# from decimal import Decimal
# from typing import Optional

# from pydantic import BaseModel, Field


# class RenglonRemitoIn(BaseModel):
#     """DTO de entrada para un renglón de remito."""

#     codigo_afip: str = Field(..., description="Código AFIP de la mercadería")
#     unidades: Decimal = Field(..., description="Cantidad de unidades")
#     kilos: Decimal = Field(..., description="Peso en kilos")
#     numero_tropa: Optional[str] = Field(None, description="Número de tropa")
#     observaciones: Optional[str] = Field(None, description="Observaciones")


# class RenglonRemitoOut(BaseModel):
#     """DTO de salida de un renglón de remito."""

#     id: int
#     remito_id: int
#     codigo_afip: str
#     unidades: Decimal
#     kilos: Decimal
#     numero_tropa: Optional[str]
#     observaciones: Optional[str]

#     model_config = {"from_attributes": True}


# class ParticipanteOut(BaseModel):
#     """DTO de salida de un participante del remito."""

#     cuit: str
#     razon_social: Optional[str] = None


# class RemitoCarnicoIn(BaseModel):
#     """DTO de entrada para crear un remito electrónico cárnico."""

#     punto_emision: str = Field(..., description="Punto de emisión (4 dígitos)")
#     numero_comprobante: str = Field(..., description="Número de comprobante (10 dígitos)")
#     caso: str = Field(..., description="Caso de remito (01-06)")
#     tipo_movimiento: str = Field(..., description="Tipo de movimiento")
#     fecha_emision: datetime = Field(..., description="Fecha de emisión")
#     fecha_vencimiento: datetime = Field(..., description="Fecha de vencimiento")
#     titular_cuit: str = Field(..., description="CUIT del titular")
#     transportista_cuit: str = Field(..., description="CUIT del transportista")
#     destinatario_cuit: Optional[str] = Field(None, description="CUIT del destinatario")
#     depositario_cuit: Optional[str] = Field(None, description="CUIT del depositario")
#     chofer_apellido_nombre: Optional[str] = Field(None, description="Apellido y nombre del chofer")
#     chofer_documento: Optional[str] = Field(None, description="Documento del chofer")
#     dominio_vehiculo: Optional[str] = Field(None, description="Dominio del vehículo")
#     observaciones: Optional[str] = Field(None, description="Observaciones")
#     renglones: list[RenglonRemitoIn] = Field(..., description="Renglones del remito")


# class RemitoCarnicoOut(BaseModel):
#     """DTO de salida de un remito electrónico cárnico."""

#     id: int
#     punto_emision: str
#     numero_comprobante: str
#     caso: str
#     tipo_movimiento: str
#     estado: str
#     fecha_emision: datetime
#     fecha_vencimiento: datetime
#     fecha_entrega: Optional[datetime]
#     titular_cuit: str
#     transportista_cuit: str
#     destinatario_cuit: Optional[str]
#     depositario_cuit: Optional[str]
#     chofer_apellido_nombre: Optional[str]
#     chofer_documento: Optional[str]
#     dominio_vehiculo: Optional[str]
#     observaciones: Optional[str]
#     creado_en: datetime
#     renglones: list[RenglonRemitoOut] = []

#     model_config = {"from_attributes": True}
