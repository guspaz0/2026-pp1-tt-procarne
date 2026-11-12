# """Schemas (DTOs) del operador de la cadena cárnica."""

# from __future__ import annotations

# from datetime import datetime
# from typing import Optional

# from pydantic import BaseModel, Field


# class RemitoOperadorIn(BaseModel):
#     """DTO de entrada para crear un operador de remitos."""

#     persona_id: int = Field(..., description="ID de la persona asociada")


# class RemitoOperadorOut(BaseModel):
#     """DTO de salida de un operador de remitos."""

#     id: int
#     persona_id: int
#     creado_en: datetime

#     model_config = {"from_attributes": True}
