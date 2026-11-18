"""Modelo ORM de OperadorRequisito.

Representa el estado de cumplimiento de un requisito (vinculado a una
categoría) por parte de un operador específico.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class OperadorRequisito(Base):
    """Modelo ORM de operador_requisitos (estado de cumplimiento)."""

    __tablename__ = "operador_requisitos"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requisito_categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categoria_requisitos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador: Mapped["Operador"] = relationship(back_populates="requisitos")
    requisito_categoria: Mapped["CategoriaRequisito"] = relationship()
    documentos: Mapped[list["DocumentoRequisito"]] = relationship(
        back_populates="operador_requisito", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<OperadorRequisito id={self.id} op={self.operador_id} req_cat={self.requisito_categoria_id} estado={self.estado}>"


class OperadorRequisitoDAO:
    """DAO de operador_requisitos."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, id: int) -> Optional[OperadorRequisito]:
        """Obtiene un operador_requisito por su id."""
        with self._session_factory() as session:
            return session.get(OperadorRequisito, id)

    def listar_por_operador(self, operador_id: int) -> list[OperadorRequisito]:
        """Lista todos los requisitos de un operador."""
        with self._session_factory() as session:
            return (
                session.query(OperadorRequisito)
                .filter_by(operador_id=operador_id)
                .all()
            )

    def crear(self, operador_id: int, requisito_categoria_id: int,
              estado: str = "PENDIENTE") -> OperadorRequisito:
        """Crea y persiste un operador_requisito nuevo."""
        with self._session_factory() as session:
            or_ = OperadorRequisito(
                operador_id=operador_id,
                requisito_categoria_id=requisito_categoria_id,
                estado=estado,
            )
            session.add(or_)
            session.commit()
            session.refresh(or_)
            return or_

    def actualizar_estado(self, id: int, estado: str) -> Optional[OperadorRequisito]:
        """Actualiza el estado de un operador_requisito."""
        with self._session_factory() as session:
            or_ = session.get(OperadorRequisito, id)
            if or_ is None:
                return None
            or_.estado = estado
            session.commit()
            session.refresh(or_)
            return or_

    def eliminar(self, id: int) -> bool:
        """Elimina un operador_requisito."""
        with self._session_factory() as session:
            or_ = session.get(OperadorRequisito, id)
            if or_ is None:
                return False
            session.delete(or_)
            session.commit()
            return True
