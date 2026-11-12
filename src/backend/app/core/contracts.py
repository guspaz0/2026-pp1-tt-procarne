"""Contratos (interfaces) para inyección de dependencias entre módulos.

Definidos como ``Protocol`` (typing) para que los módulos genéricos
puedan depender de abstracciones, no de implementaciones concretas.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class DatabaseDAO(Protocol):
    """Interfaz mínima que debe cumplir un DAO de base de datos."""

    def obtener_sesion(self):
        """Devuelve un contexto manager que produce una sesión."""
        ...

    def crear_tablas(self) -> None:
        """Crea todas las tablas definidas en ``Base.metadata``."""
        ...


@runtime_checkable
class PersonaDAO(Protocol):
    """Interfaz mínima para acceso a personas (físicas o jurídicas)."""

    def obtener_por_id(self, persona_id: int):
        """Devuelve la persona con el id dado, o ``None``."""
        ...

    def obtener_por_documento(self, tipo: str, identificador: str):
        """Devuelve la persona con el documento dado, o ``None``."""
        ...


# @runtime_checkable
# class MercaderiaDAO(Protocol):
#     """Interfaz mínima para acceso al catálogo de mercaderías."""

#     def obtener_por_codigo_afip(self, codigo: str):
#         """Devuelve la mercadería con el código AFIP dado, o ``None``."""
#         ...


class PersonaRef:
    """Referencia inmutable a una persona (para transferir entre módulos)."""

    def __init__(self, id: int, tipo: str, identificador: str, nombre: str) -> None:
        self.id = id
        self.tipo = tipo
        self.identificador = identificador
        self.nombre = nombre


# class MercaderiaRef:
#     """Referencia inmutable a una mercadería (para transferir entre módulos)."""

#     def __init__(self, id: int, codigo: str, descripcion: str) -> None:
#         self.id = id
#         self.codigo = codigo
#         self.descripcion = descripcion
