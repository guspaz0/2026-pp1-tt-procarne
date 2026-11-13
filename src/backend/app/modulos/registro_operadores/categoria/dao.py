"""Modelo ORM de Categoría de operador.

Cada categoría (CARNICERÍA, FRÍFICO, TRANSPORTE, etc.) define un
conjunto de requisitos que sus operadores deben cumplir.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Categoria(Base):
    """Modelo ORM de categoría de operador."""

    __tablename__ = "categorias"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ciclo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    requisitos: Mapped[list["Requisito"]] = relationship(
        back_populates="categoria", cascade="all, delete-orphan"
    )
    operadores: Mapped[list["Operador"]] = relationship(
        back_populates="categoria"
    )

    def __repr__(self) -> str:
        return f"<Categoria id={self.id} nombre={self.nombre}>"


class CategoriaDAO:
    """DAO de categorías."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, categoria_id: int) -> Optional[Categoria]:
        """Obtiene una categoría por su id."""
        with self._session_factory() as session:
            return session.get(Categoria, categoria_id)

    def obtener_por_nombre(self, nombre: str) -> Optional[Categoria]:
        """Obtiene una categoría por su nombre."""
        with self._session_factory() as session:
            return (
                session.query(Categoria)
                .filter_by(nombre=nombre)
                .first()
            )

    def listar(self) -> list[Categoria]:
        """Lista todas las categorías."""
        with self._session_factory() as session:
            return list(session.query(Categoria).order_by(Categoria.nombre).all())

    def crear(self, nombre: str, descripcion: str | None = None,
              ciclo: str | None = None) -> Categoria:
        """Crea y persiste una categoría nueva."""
        with self._session_factory() as session:
            cat = Categoria(nombre=nombre, descripcion=descripcion, ciclo=ciclo)
            session.add(cat)
            session.commit()
            session.refresh(cat)
            return cat

    def actualizar(self, categoria_id: int, **kwargs) -> Optional[Categoria]:
        """Actualiza campos de una categoría."""
        with self._session_factory() as session:
            cat = session.get(Categoria, categoria_id)
            if cat is None:
                return None
            for k, v in kwargs.items():
                if hasattr(cat, k):
                    setattr(cat, k, v)
            session.commit()
            session.refresh(cat)
            return cat
