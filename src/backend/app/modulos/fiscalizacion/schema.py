"""Schemas (DTOs) del Módulo III — Fiscalización (ROCCA)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .enums import (
    EstadoActa,
    EstadoDecomiso,
    EstadoSancion,
    GravedadInfraccion,
    ResultadoInspeccion,
    TipoActa,
    TipoInfraccion,
    TipoInspeccion,
    TipoSancion,
)


# ---------------------------------------------------------------------------
# Entradas anidadas
# ---------------------------------------------------------------------------


class ActaIn(BaseModel):
    """Acta levantada durante la inspección."""

    tipo: TipoActa
    numero: Optional[str] = None
    descripcion: Optional[str] = None
    estado: EstadoActa = EstadoActa.BORRADOR


class DecomisoIn(BaseModel):
    """Decomiso de mercadería."""

    producto: str = Field(min_length=1, max_length=255)
    cantidad: float = Field(gt=0)
    unidad: str = "KG"
    motivo: Optional[str] = None
    destino: Optional[str] = None
    estado: EstadoDecomiso = EstadoDecomiso.EN_CURSADO


class InfraccionIn(BaseModel):
    """Infracción detectada."""

    tipo: TipoInfraccion
    gravedad: GravedadInfraccion = GravedadInfraccion.LEVE
    descripcion: Optional[str] = None
    sanciones: list["SancionIn"] = Field(default_factory=list)


class SancionIn(BaseModel):
    """Sanción aplicada por infracción."""

    tipo: TipoSancion
    monto: Optional[float] = Field(default=None, gt=0)
    descripcion: Optional[str] = None
    estado: EstadoSancion = EstadoSancion.PENDIENTE


InfraccionIn.model_rebuild()


# ---------------------------------------------------------------------------
# Inspección
# ---------------------------------------------------------------------------


class InspeccionIn(BaseModel):
    """Datos de entrada para registrar una inspección."""

    inspector: str = Field(min_length=1, max_length=120)
    operador_cuit: Optional[str] = Field(default=None, max_length=13)
    tipo: TipoInspeccion = TipoInspeccion.RUTINA
    resultado: ResultadoInspeccion = ResultadoInspeccion.CONFORME
    latitud: Optional[float] = Field(default=None, ge=-90, le=90)
    longitud: Optional[float] = Field(default=None, ge=-180, le=180)
    observaciones: Optional[str] = None
    actas: list[ActaIn] = Field(default_factory=list)
    decomisos: list[DecomisoIn] = Field(default_factory=list)
    infracciones: list[InfraccionIn] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validar_cuit(self) -> "InspeccionIn":
        if self.operador_cuit is not None:
            if not self.operador_cuit.isdigit() or len(self.operador_cuit) != 11:
                raise ValueError("El CUIT del operador debe tener 11 dígitos")
        return self

    @model_validator(mode="after")
    def _validar_resultado_conformidad(self) -> "InspeccionIn":
        if self.resultado is ResultadoInspeccion.NO_CONFORME and not self.infracciones:
            raise ValueError(
                "Una inspección NO_CONFORME debe incluir al menos una infracción"
            )
        return self


class InspeccionOut(BaseModel):
    """DTO de salida de la inspección."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    inspector: str
    operador_cuit: Optional[str] = None
    fecha: datetime
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    tipo: TipoInspeccion
    resultado: ResultadoInspeccion
    observaciones: Optional[str] = None
    enviada: bool
    actas: list["ActaOut"] = Field(default_factory=list)
    decomisos: list["DecomisoOut"] = Field(default_factory=list)
    infracciones: list["InfraccionOut"] = Field(default_factory=list)

    @classmethod
    def from_orm(cls, inspeccion) -> "InspeccionOut":
        return cls(
            id=inspeccion.id,
            inspector=inspeccion.inspector,
            operador_cuit=inspeccion.operador_cuit,
            fecha=inspeccion.fecha,
            latitud=inspeccion.latitud,
            longitud=inspeccion.longitud,
            tipo=TipoInspeccion(inspeccion.tipo),
            resultado=ResultadoInspeccion(inspeccion.resultado),
            observaciones=inspeccion.observaciones,
            enviada=inspeccion.enviada,
            actas=[ActaOut.from_orm(a) for a in inspeccion.actas],
            decomisos=[DecomisoOut.from_orm(d) for d in inspeccion.decomisos],
            infracciones=[InfraccionOut.from_orm(i) for i in inspeccion.infracciones],
        )


# ---------------------------------------------------------------------------
# Acta
# ---------------------------------------------------------------------------


class ActaOut(BaseModel):
    """DTO de salida del acta."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    inspeccion_id: int
    tipo: TipoActa
    numero: Optional[str] = None
    descripcion: Optional[str] = None
    estado: EstadoActa
    fecha_firma: Optional[datetime] = None

    @classmethod
    def from_orm(cls, acta) -> "ActaOut":
        return cls(
            id=acta.id,
            inspeccion_id=acta.inspeccion_id,
            tipo=TipoActa(acta.tipo),
            numero=acta.numero,
            descripcion=acta.descripcion,
            estado=EstadoActa(acta.estado),
            fecha_firma=acta.fecha_firma,
        )


# ---------------------------------------------------------------------------
# Decomiso
# ---------------------------------------------------------------------------


class DecomisoOut(BaseModel):
    """DTO de salida del decomiso."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    inspeccion_id: int
    producto: str
    cantidad: float
    unidad: str
    motivo: Optional[str] = None
    destino: Optional[str] = None
    estado: EstadoDecomiso

    @classmethod
    def from_orm(cls, decomiso) -> "DecomisoOut":
        return cls(
            id=decomiso.id,
            inspeccion_id=decomiso.inspeccion_id,
            producto=decomiso.producto,
            cantidad=decomiso.cantidad,
            unidad=decomiso.unidad,
            motivo=decomiso.motivo,
            destino=decomiso.destino,
            estado=EstadoDecomiso(decomiso.estado),
        )


# ---------------------------------------------------------------------------
# Infracción
# ---------------------------------------------------------------------------


class InfraccionOut(BaseModel):
    """DTO de salida de la infracción."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    inspeccion_id: int
    operador_cuit: Optional[str] = None
    tipo: TipoInfraccion
    gravedad: GravedadInfraccion
    descripcion: Optional[str] = None
    fecha: date
    sanciones: list["SancionOut"] = Field(default_factory=list)

    @classmethod
    def from_orm(cls, infraccion) -> "InfraccionOut":
        return cls(
            id=infraccion.id,
            inspeccion_id=infraccion.inspeccion_id,
            operador_cuit=infraccion.operador_cuit,
            tipo=TipoInfraccion(infraccion.tipo),
            gravedad=GravedadInfraccion(infraccion.gravedad),
            descripcion=infraccion.descripcion,
            fecha=infraccion.fecha,
            sanciones=[SancionOut.from_orm(s) for s in infraccion.sanciones],
        )


# ---------------------------------------------------------------------------
# Sanción
# ---------------------------------------------------------------------------


class SancionOut(BaseModel):
    """DTO de salida de la sanción."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    infraccion_id: int
    operador_cuit: Optional[str] = None
    tipo: TipoSancion
    monto: Optional[float] = None
    descripcion: Optional[str] = None
    estado: EstadoSancion
    fecha_aplicacion: date
    fecha_cumplimiento: Optional[date] = None

    @classmethod
    def from_orm(cls, sancion) -> "SancionOut":
        return cls(
            id=sancion.id,
            infraccion_id=sancion.infraccion_id,
            operador_cuit=sancion.operador_cuit,
            tipo=TipoSancion(sancion.tipo),
            monto=sancion.monto,
            descripcion=sancion.descripcion,
            estado=EstadoSancion(sancion.estado),
            fecha_aplicacion=sancion.fecha_aplicacion,
            fecha_cumplimiento=sancion.fecha_cumplimiento,
        )


# ---------------------------------------------------------------------------
# Reincidencia
# ---------------------------------------------------------------------------


class ReincidenciaOut(BaseModel):
    """DTO de salida de la reincidencia."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    operador_cuit: str
    cantidad: int
    ultima_fecha: date
    observaciones: Optional[str] = None

    @classmethod
    def from_orm(cls, rec) -> "ReincidenciaOut":
        return cls(
            id=rec.id,
            operador_cuit=rec.operador_cuit,
            cantidad=rec.cantidad,
            ultima_fecha=rec.ultima_fecha,
            observaciones=rec.observaciones,
        )


class ReincidenciaIn(BaseModel):
    """Datos de entrada para registrar una reincidencia."""

    operador_cuit: str = Field(min_length=11, max_length=11)
    observaciones: Optional[str] = None

    @model_validator(mode="after")
    def _validar_cuit(self) -> "ReincidenciaIn":
        if not self.operador_cuit.isdigit():
            raise ValueError("El CUIT debe tener 11 dígitos")
        return self
