"""Entidad de dominio: Mercadería (catálogo genérico).

Representa un producto del catálogo (código AFIP, descripción,
unidad de medida) con banderas de trazabilidad.
"""

from __future__ import annotations

from core.base import Entidad


class Mercaderia(Entidad):
    """Mercadería del catálogo genérico.

    Campos:
        codigo: código AFIP del producto.
        descripcion: descripción del producto.
        unidad_medida: unidad de medida (KG, UN, etc.).
        requiere_trazabilidad: si la mercadería requiere trazabilidad.
        requiere_numero_tropa: si requiere número de tropa.
    """

    def __init__(
        self,
        codigo: str,
        descripcion: str,
        unidad_medida: str | None = None,
        requiere_trazabilidad: bool = False,
        requiere_numero_tropa: bool = False,
    ) -> None:
        super().__init__()
        self.codigo = codigo
        self.descripcion = descripcion
        self.unidad_medida = unidad_medida
        self.requiere_trazabilidad = requiere_trazabilidad
        self.requiere_numero_tropa = requiere_numero_tropa

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "unidad_medida": self.unidad_medida,
            "requiere_trazabilidad": self.requiere_trazabilidad,
            "requiere_numero_tropa": self.requiere_numero_tropa,
        }
