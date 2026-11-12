# """Schemas (DTOs) del Módulo III — Fiscalización."""

# from __future__ import annotations

# from datetime import datetime
# from decimal import Decimal
# from typing import Optional

# from pydantic import BaseModel, Field


# class InspeccionIn(BaseModel):
#     """DTO de entrada para crear una inspección."""

#     tipo: str = Field(..., description="Tipo de inspección (PROGRAMADA, INESPERADA, etc.)")
#     operador_cuit: str = Field(..., description="CUIT del operador inspeccionado")
#     fecha: datetime = Field(..., description="Fecha de la inspección")
#     inspector: str = Field(..., description="Nombre del inspector")
#     observaciones: Optional[str] = Field(None, description="Observaciones")


# class InspeccionOut(BaseModel):
#     """DTO de salida de una inspección."""

#     id: int
#     tipo: str
#     operador_cuit: str
#     fecha: datetime
#     inspector: str
#     resultado: Optional[str]
#     observaciones: Optional[str]
#     creado_en: datetime

#     model_config = {"from_attributes": True}


# class ActaIn(BaseModel):
#     """DTO de entrada para crear un acta."""

#     inspeccion_id: int = Field(..., description="ID de la inspección")
#     tipo: str = Field(..., description="Tipo de acta (INSPECCION, DECOMISO, etc.)")
#     numero: str = Field(..., description="Número de acta")
#     fecha: datetime = Field(..., description="Fecha del acta")
#     contenido: Optional[str] = Field(None, description="Contenido del acta")


# class ActaOut(BaseModel):
#     """DTO de salida de un acta."""

#     id: int
#     inspeccion_id: int
#     tipo: str
#     numero: str
#     fecha: datetime
#     estado: str
#     contenido: Optional[str]
#     firmado_por: Optional[str]
#     fecha_firma: Optional[datetime]

#     model_config = {"from_attributes": True}


# class InfraccionIn(BaseModel):
#     """DTO de entrada para crear una infracción."""

#     inspeccion_id: int = Field(..., description="ID de la inspección")
#     operador_cuit: str = Field(..., description="CUIT del operador infractor")
#     tipo: str = Field(..., description="Tipo de infracción")
#     gravedad: str = Field(..., description="Gravedad (LEVE, GRAVE, MUY_GRAVE)")
#     descripcion: str = Field(..., description="Descripción de la infracción")


# class InfraccionOut(BaseModel):
#     """DTO de salida de una infracción."""

#     id: int
#     inspeccion_id: int
#     operador_cuit: str
#     tipo: str
#     gravedad: str
#     descripcion: str
#     creado_en: datetime

#     model_config = {"from_attributes": True}


# class SancionIn(BaseModel):
#     """DTO de entrada para crear una sanción."""

#     infraccion_id: int = Field(..., description="ID de la infracción")
#     operador_cuit: str = Field(..., description="CUIT del operador sancionado")
#     tipo: str = Field(..., description="Tipo de sanción (AMONESTACION, MULTA, etc.)")
#     monto: Optional[Decimal] = Field(None, description="Monto de la multa")
#     observaciones: Optional[str] = Field(None, description="Observaciones")


# class SancionOut(BaseModel):
#     """DTO de salida de una sanción."""

#     id: int
#     infraccion_id: int
#     operador_cuit: str
#     tipo: str
#     monto: Optional[Decimal]
#     estado: str
#     fecha_notificacion: Optional[datetime]
#     fecha_pago: Optional[datetime]
#     observaciones: Optional[str]
#     creado_en: datetime

#     model_config = {"from_attributes": True}


# class DecomisoIn(BaseModel):
#     """DTO de entrada para crear un decomiso."""

#     inspeccion_id: int = Field(..., description="ID de la inspección")
#     mercaderia: str = Field(..., description="Descripción de la mercadería")
#     cantidad: Decimal = Field(..., description="Cantidad")
#     peso_kg: Decimal = Field(..., description="Peso en kilos")
#     motivo: Optional[str] = Field(None, description="Motivo del decomiso")


# class DecomisoOut(BaseModel):
#     """DTO de salida de un decomiso."""

#     id: int
#     inspeccion_id: int
#     mercaderia: str
#     cantidad: Decimal
#     peso_kg: Decimal
#     estado: str
#     motivo: Optional[str]
#     creado_en: datetime

#     model_config = {"from_attributes": True}


# class ReincidenciaIn(BaseModel):
#     """DTO de entrada para registrar una reincidencia."""

#     operador_cuit: str = Field(..., description="CUIT del operador")


# class ReincidenciaOut(BaseModel):
#     """DTO de salida de una reincidencia."""

#     id: int
#     operador_cuit: str
#     cantidad_infracciones: int
#     ultima_fecha: datetime
#     creado_en: datetime

#     model_config = {"from_attributes": True}
