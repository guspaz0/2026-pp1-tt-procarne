"""DTOs (schemas Pydantic) de ``Categoria``.

- ``RequisitoOut`` — requisito de inscripción (definición única).
- ``CategoriaOut`` — categoría con sus requisitos anidados (para el
  select de categorías + checklist de papeleo del frontend).
"""

from __future__ import annotations

from pydantic import BaseModel


class RequisitoOut(BaseModel):
    """Requisito de inscripción (papeleo) de una categoría."""

    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None
    obligatorio: bool = True

    model_config = {"from_attributes": True}


class CategoriaOut(BaseModel):
    """Categoría de operador con sus requisitos de papeleo."""

    id: int
    nombre: str
    descripcion: str | None = None
    ciclo: str | None = None
    requisitos: list[RequisitoOut] = []

    model_config = {"from_attributes": True}
