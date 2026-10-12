"""Entidad de mercadería del módulo genérico.

Define :class:`Mercaderia`, entidad concreta de dominio del catálogo
genérico de productos.
"""

from __future__ import annotations

from typing import Optional

from ..base import Entidad


class Mercaderia(Entidad):
    """Mercadería del catálogo genérico de productos.

    Representa un producto/ítem transportable identificado por un código
    de catálogo, con su descripción, unidad de medida y si exige datos de
    trazabilidad.
    """

    def __init__(
        self,
        codigo: str,
        descripcion: str,
        unidad_medida: Optional[str] = None,
        requiere_trazabilidad: bool = False,
        requiere_numero_tropa: bool = False,
    ) -> None:
        super().__init__()
        self.codigo = codigo
        self.descripcion = descripcion
        self.unidad_medida = unidad_medida
        self._requiere_trazabilidad = requiere_trazabilidad
        self._requiere_numero_tropa = requiere_numero_tropa

    @property
    def requiere_trazabilidad(self) -> bool:
        """Indica si la mercadería exige datos de trazabilidad."""
        return self._requiere_trazabilidad

    @property
    def requiere_numero_tropa(self) -> bool:
        """Indica si la mercadería exige el N° de tropa."""
        return self._requiere_numero_tropa

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "unidad_medida": self.unidad_medida,
            "requiere_trazabilidad": self.requiere_trazabilidad,
            "requiere_numero_tropa": self.requiere_numero_tropa,
        }
