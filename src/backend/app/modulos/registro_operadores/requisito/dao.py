"""Modelo ORM de Requisito y tabla intermedia CategoriaRequisito.

Los requisitos son definiciones únicas (no se duplican entre categorías).
La relación N:M se resuelve con la tabla intermedia ``categoria_requisitos``.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Requisito(Base):
    """Modelo ORM de requisito de inscripción (definición única)."""

    __tablename__ = "requisitos"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    categorias: Mapped[list["Categoria"]] = relationship(
        back_populates="requisitos",
        secondary="categoria_requisitos",
    )

    def __repr__(self) -> str:
        return f"<Requisito id={self.id} codigo={self.codigo}>"


class CategoriaRequisito(Base):
    """Tabla intermedia N:M entre categorias y requisitos."""

    __tablename__ = "categoria_requisitos"
    __table_args__ = (
        UniqueConstraint("categoria_id", "requisito_id", name="uq_cat_req"),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requisito_id: Mapped[int] = mapped_column(
        ForeignKey("requisitos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    obligatorio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<CategoriaRequisito cat={self.categoria_id} req={self.requisito_id}>"


class RequisitoDAO:
    """DAO de requisitos."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, requisito_id: int) -> Optional[Requisito]:
        """Obtiene un requisito por su id."""
        with self._session_factory() as session:
            return session.get(Requisito, requisito_id)

    def obtener_por_codigo(self, codigo: str) -> Optional[Requisito]:
        """Obtiene un requisito por su código."""
        with self._session_factory() as session:
            return session.query(Requisito).filter_by(codigo=codigo).first()

    def listar_por_categoria(self, categoria_id: int) -> list[Requisito]:
        """Lista los requisitos de una categoría (vía tabla intermedia)."""
        with self._session_factory() as session:
            return (
                session.query(Requisito)
                .join(CategoriaRequisito, CategoriaRequisito.requisito_id == Requisito.id)
                .filter(CategoriaRequisito.categoria_id == categoria_id)
                .order_by(Requisito.nombre)
                .all()
            )

    def crear(self, codigo: str, nombre: str,
              descripcion: str | None = None) -> Requisito:
        """Crea y persiste un requisito nuevo (definición única)."""
        with self._session_factory() as session:
            req = Requisito(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
            )
            session.add(req)
            session.commit()
            session.refresh(req)
            return req

    def vincular_categoria(self, categoria_id: int, requisito_id: int,
                          obligatorio: bool = True) -> None:
        """Vincula un requisito a una categoría (tabla intermedia)."""
        with self._session_factory() as session:
            existente = (
                session.query(CategoriaRequisito)
                .filter_by(categoria_id=categoria_id, requisito_id=requisito_id)
                .first()
            )
            if existente is None:
                session.add(CategoriaRequisito(
                    categoria_id=categoria_id,
                    requisito_id=requisito_id,
                    obligatorio=obligatorio,
                ))
                session.commit()

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
        """Elimina un requisito (las filas intermedias se borran por CASCADE)."""
        with self._session_factory() as session:
            req = session.get(Requisito, requisito_id)
            if req is None:
                return False
            session.delete(req)
            session.commit()
            return True
