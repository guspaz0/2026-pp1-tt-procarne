"""Schemas (DTOs) del operador."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoriaAfipOut(BaseModel):
    """Categoría AFIP (catálogo)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    descripcion: str


class ActividadOut(BaseModel):
    """Actividad del operador con sus inscripciones en categorías."""

    id: int
    nombre: str
    categorias: list["CategoriaOperadorOut"] = []


class CategoriaOperadorOut(BaseModel):
    """Inscripción de un operador en una categoría."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    actividad_id: Optional[int] = None
    categoria: str
    situacion: str
    desde_fecha: Optional[str] = None
    hasta_fecha: Optional[str] = None


class OperadorIn(BaseModel):
    """Datos de entrada para crear un operador."""

    cuit: str
    razon_social: str
    domicilio: Optional[str] = None
    domicilio_fiscal: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    categoria: Optional[str] = None
    situacion: Optional[str] = None


class OperadorOut(BaseModel):
    """DTO de salida del operador.

    Estructura:
    - actividades: a qué actividades pertenece el operador
    - cada actividad.categorias: las categorías específicas en las que
      el operador está inscripto dentro de esa actividad
    """

    id: int
    cuit: str
    razon_social: str
    domicilio: Optional[str] = None
    domicilio_fiscal: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    categoria: Optional[str] = None
    situacion: Optional[str] = None
    actividades: list[ActividadOut] = []

    @classmethod
    def from_orm(cls, operador) -> "OperadorOut":
        # Agrupar categorías por actividad_id
        cats_por_actividad: dict[Optional[int], list[CategoriaOperadorOut]] = {}
        for c in operador.categorias:
            cats_por_actividad.setdefault(c.actividad_id, []).append(
                CategoriaOperadorOut(
                    id=c.id,
                    actividad_id=c.actividad_id,
                    categoria=c.categoria,
                    situacion=c.situacion,
                    desde_fecha=c.desde_fecha,
                    hasta_fecha=c.hasta_fecha,
                )
            )

        actividades = [
            ActividadOut(
                id=a.id,
                nombre=a.nombre,
                categorias=cats_por_actividad.get(a.id, []),
            )
            for a in operador.actividades
        ]

        return cls(
            id=operador.id,
            cuit=operador.cuit,
            razon_social=operador.razon_social,
            domicilio=operador.domicilio,
            domicilio_fiscal=operador.domicilio_fiscal,
            telefono=operador.telefono,
            email=operador.email,
            categoria=operador.categoria,
            situacion=operador.situacion,
            actividades=actividades,
        )
