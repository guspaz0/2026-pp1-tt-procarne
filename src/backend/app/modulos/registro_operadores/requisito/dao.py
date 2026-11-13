"""Modelo ORM de Requisito.

Cada requisito está ligado a una categoría (no a un operador).
El operador hereda los requisitos de su categoría.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Requisito(Base):
    """Modelo ORM de requisito de inscripción (ligado a categoría)."""

    __tablename__ = "requisitos"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    obligatorio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria: Mapped["Categoria"] = relationship(back_populates="requisitos")
    adjuntos: Mapped[list["Adjunto"]] = relationship(
        back_populates="requisito", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Requisito id={self.id} categoria_id={self.categoria_id} nombre={self.nombre}>"


class RequisitoDAO:
    """DAO de requisitos."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, requisito_id: int) -> Optional[Requisito]:
        """Obtiene un requisito por su id."""
        with self._session_factory() as session:
            return session.get(Requisito, requisito_id)

    def listar_por_categoria(self, categoria_id: int) -> list[Requisito]:
        """Lista los requisitos de una categoría."""
        with self._session_factory() as session:
            return (
                session.query(Requisito)
                .filter_by(categoria_id=categoria_id)
                .order_by(Requisito.nombre)
                .all()
            )

    def crear(self, categoria_id: int, nombre: str,
              descripcion: str | None = None,
              obligatorio: bool = True) -> Requisito:
        """Crea y persiste un requisito nuevo."""
        with self._session_factory() as session:
            req = Requisito(
                categoria_id=categoria_id,
                nombre=nombre,
                descripcion=descripcion,
                obligatorio=obligatorio,
            )
            session.add(req)
            session.commit()
            session.refresh(req)
            return req

    def actualizar(self, requisito_id: int, **kwargs) -> Optional[Requisito]:
        """Actualiza campos de un requisito."""
        with self._session_factory() as session:
            req = session.get(Requisito, requisito_id)
            if req is None:
                return None
            for k, v in kwargs.items():
                if hasattr(req, k):
                    setattr(req, k, v)
            session.commit()
            session.refresh(req)
            return req

    def eliminar(self, requisito_id: int) -> bool:
        """Elimina un requisito."""
        with self._session_factory() as session:
            req = session.get(Requisito, requisito_id)
            if req is None:
                return False
            session.delete(req)
            session.commit()
            return True
