"""Clase base abstracta para todas las entidades de dominio genéricas.

Proporciona un identificador único y un método de serialización a
diccionario. Las subclases concretas definen sus campos específicos.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import uuid4


class Entidad(ABC):
    """Clase base abstracta para todas las entidades del dominio."""

    def __init__(self) -> None:
        self.id: str = uuid4().hex

    @abstractmethod
    def to_dict(self) -> dict:
        """Serializa la entidad a un diccionario plano."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
