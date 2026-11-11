"""DTOs (schemas Pydantic) de ``AdjuntoOperador``.

Los adjuntos se suben vía JSON (base64), no vía multipart; por eso el
"request" es un dict ya validado en el controlador. El response sí está
formalizado como DTO.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AdjuntoOperadorOut(BaseModel):
    """DTO de salida de un adjunto (documento) de operador."""

    id: int
    operador_id: int
    requisito: str
    storage_key: str
    content_type: str
    size: int
    nombre_original: str
    creado_en: Optional[datetime] = Field(None, description="Fecha de carga del adjunto")

    model_config = {"from_attributes": True}
