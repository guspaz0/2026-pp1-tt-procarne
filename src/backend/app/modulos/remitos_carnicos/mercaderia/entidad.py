"""Entidades de mercadería del módulo de Remitos Electrónicos Cárnicos.

Define :class:`Mercaderia` (clase abstracta) y sus concretas según la
tabla de producción pública de AFIP:

- :class:`MercaderiaConHueso` — tablas 2, 3
- :class:`MercaderiaSinHueso` — tablas 4, 5, 6
- :class:`MercaderiaPorcina` — tabla 13
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional

from ..base import Entidad


class Mercaderia(Entidad, ABC):
    """Clase abstracta de la mercadería transportada (sector F)."""

    @abstractmethod
    def __init__(
        self,
        codigo_afip: str,
        descripcion: str,
        unidades: Decimal,
        kilos: Decimal,
    ) -> None:
        self.codigo_afip = codigo_afip
        self.descripcion = descripcion
        self.unidades = unidades
        self.kilos = kilos

    @property
    @abstractmethod
    def requiere_numero_tropa(self) -> bool:
        """Indica si el código de mercadería exige el N° de tropa."""
        raise NotImplementedError

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo_afip": self.codigo_afip,
            "descripcion": self.descripcion,
            "unidades": str(self.unidades),
            "kilos": str(self.kilos),
            "requiere_numero_tropa": self.requiere_numero_tropa,
        }


class MercaderiaConHueso(Mercaderia):
    """Mercadería con hueso (tablas 2, 3)."""

    def __init__(
        self,
        codigo_afip: str,
        descripcion: str,
        unidades: Decimal,
        kilos: Decimal,
        numero_tropa: Optional[str] = None,
    ) -> None:
        super().__init__(codigo_afip, descripcion, unidades, kilos)
        self.numero_tropa = numero_tropa

    @property
    def requiere_numero_tropa(self) -> bool:
        return True

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["numero_tropa"] = self.numero_tropa
        return base


class MercaderiaSinHueso(Mercaderia):
    """Mercadería sin hueso (tablas 4, 5, 6)."""

    _CODIGOS_CON_TROPA: frozenset[str] = frozenset(
        {
            "4.1",
            "5.21", "5.22", "5.23",
            "5.30", "5.31", "5.32", "5.33", "5.34", "5.35", "5.36", "5.37",
            "6.25",
            "6.43", "6.44", "6.45", "6.46",
        }
    )

    def __init__(
        self,
        codigo_afip: str,
        descripcion: str,
        unidades: Decimal,
        kilos: Decimal,
        numero_tropa: Optional[str] = None,
    ) -> None:
        super().__init__(codigo_afip, descripcion, unidades, kilos)
        self.numero_tropa = numero_tropa

    @property
    def requiere_numero_tropa(self) -> bool:
        return self.codigo_afip in self._CODIGOS_CON_TROPA

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["numero_tropa"] = self.numero_tropa
        return base


class MercaderiaPorcina(Mercaderia):
    """Mercadería porcina (tabla 13)."""

    _CODIGOS_CON_TROPA: frozenset[str] = frozenset({"13.18", "13.30"})

    def __init__(
        self,
        codigo_afip: str,
        descripcion: str,
        unidades: Decimal,
        kilos: Decimal,
        numero_tropa: Optional[str] = None,
    ) -> None:
        super().__init__(codigo_afip, descripcion, unidades, kilos)
        self.numero_tropa = numero_tropa

    @property
    def requiere_numero_tropa(self) -> bool:
        return self.codigo_afip in self._CODIGOS_CON_TROPA

    def to_dict(self) -> dict:
        base = super().to_dict()
        base["numero_tropa"] = self.numero_tropa
        return base
