"""Núcleo del dominio: contratos (tipos) compartidos entre módulos.

Este paquete contiene **solo tipos**: interfaces abstractas y protocolos
que los módulos de negocio dependen. No importa nada de ``configs`` ni de
otros módulos, por lo que cualquier módulo puede depender de ``core`` sin
crear acoplamientos circulares.

- :class:`DatabaseDAO` — interfaz de persistencia (Dependency Inversion).
- :class:`PersonaRef` / :class:`MercaderiaRef` — referencias de identidad
  que permiten a un módulo consultar datos de otro módulo sin importar su
  ORM (solo el tipo).
- :class:`PersonaDAO` (Protocolo) — contrato mínimo de consulta de personas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from sqlalchemy.orm import Session

__all__ = [
    "DatabaseDAO",
    "PersonaRef",
    "MercaderiaRef",
    "PersonaDAO",
]


class DatabaseDAO(ABC):
    """Interfaz abstracta de acceso a la base de datos.

    Cada implementación concreta encapsula la configuración del motor
    y la sesión para un motor específico (SQLite, PostgreSQL, ...).
    """

    @abstractmethod
    def __init__(self, url: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def crear_tablas(self) -> None:
        """Crea todas las tablas definidas en :class:`Base`."""
        raise NotImplementedError

    @abstractmethod
    def obtener_sesion(self) -> Session:
        """Devuelve una nueva sesión transaccional."""
        raise NotImplementedError

    @abstractmethod
    def cerrar(self) -> None:
        """Cierra el motor de base de datos."""
        raise NotImplementedError


@dataclass(frozen=True)
class PersonaRef:
    """Referencia de identidad a una persona (física o jurídica).

    Permite a un módulo crear o referenciar una persona de otro módulo
    sin importar su clase ORM: solo se necesita el identificador (DNI o
    CUIT) y el tipo.
    """

    tipo: str
    tipo_documento: str
    identificador: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    razon_social: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None


@dataclass(frozen=True)
class MercaderiaRef:
    """Referencia de identidad a una mercadería del catálogo genérico."""

    id: int
    codigo: str
    descripcion: str


@runtime_checkable
class PersonaDAO(Protocol):
    """Contrato mínimo de consulta de personas.

    Cualquier DAO de persona (el genérico ``core.persona``)
    lo satisface de forma estructural, sin necesidad de heredarlo.
    """

    def obtener_por_identificador(self, identificador: str) -> Optional[PersonaRef]:
        """Devuelve la referencia de la persona o ``None``."""
        ...

    def obtener_por_id(self, persona_id: int) -> Optional[PersonaRef]:
        """Devuelve la referencia de la persona por id o ``None``."""
        ...
