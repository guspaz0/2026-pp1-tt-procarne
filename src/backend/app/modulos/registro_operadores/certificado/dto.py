"""DTOs (schemas Pydantic) de ``Certificado``."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from modulos.registro_operadores.enums import EstadoCertificado


class CertificadoIn(BaseModel):
    """DTO de entrada para crear un certificado."""

    numero_certificado: str = Field(..., description="Número de certificado (ej: F-102-1001)")
    tipo_certificado: str = Field("HABILITACION", description="Tipo: HABILITACION, INSCRIPCION, etc.")
    fecha_emision: datetime = Field(..., description="Fecha de emisión")
    fecha_vencimiento: Optional[datetime] = Field(None, description="Fecha de vencimiento")
    actividades_economicas: Optional[str] = Field(None, description="Resumen (denormalizado) de actividades económicas, para el PDF")
    actividad_ids: Optional[list[int]] = Field(None, description="Ids del catálogo de actividades que habilita el certificado (N:M)")
    observaciones: Optional[str] = Field(None, description="Observaciones")


class CertificadoSuspenderIn(BaseModel):
    """DTO de entrada para suspender/reactivar un certificado (acción de supervisor)."""

    operador_id: int = Field(..., description="Id del operador")
    observaciones: Optional[str] = Field(None, description="Motivo de la suspensión")


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
    actividad_ids: list[int] = Field(default_factory=list, description="Ids del catálogo de actividades que habilita el certificado")
    observaciones: Optional[str]
    estado: str
    estado_efectivo: str = ""
    creado_en: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_certificado(cls, cert, actividad_ids: list[int] | None = None) -> "CertificadoOut":
        """Construye el DTO calculando el estado efectivo.

        Si el certificado está ACTIVO pero su fecha_vencimiento ya pasó,
        el estado efectivo se reporta como VENCIDO.

        ``actividad_ids`` son los ids del catálogo que habilita el certificado
        (N:M); se pasan desde el servicio vía el DAO.
        """
        estado = cert.estado
        estado_efectivo = estado
        if estado == EstadoCertificado.ACTIVO.value and cert.fecha_vencimiento is not None:
            venc = cert.fecha_vencimiento
            # Normalizar a aware UTC para la comparación
            if venc.tzinfo is None:
                venc = venc.replace(tzinfo=timezone.utc)
            if venc < datetime.now(timezone.utc):
                estado_efectivo = EstadoCertificado.VENCIDO.value

        return cls(
            id=cert.id,
            operador_id=cert.operador_id,
            numero_certificado=cert.numero_certificado,
            tipo_certificado=cert.tipo_certificado,
            fecha_emision=cert.fecha_emision,
            fecha_vencimiento=cert.fecha_vencimiento,
            actividades_economicas=cert.actividades_economicas,
            actividad_ids=actividad_ids or [],
            observaciones=cert.observaciones,
            estado=estado,
            estado_efectivo=estado_efectivo,
            creado_en=cert.creado_en,
        )
