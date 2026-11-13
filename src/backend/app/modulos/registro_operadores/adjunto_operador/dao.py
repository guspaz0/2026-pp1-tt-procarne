"""DAO y modelo ORM de ``AdjuntoOperador``.

Los adjuntos de operador son documentos específicos de la
categoría/actividad del operador (formulario 101, habilitación municipal,
etc.).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class AdjuntoOperador(Base):
    """Modelo ORM de adjunto (documento) de un operador."""

    __tablename__ = "adjuntos_operador"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requisito: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_original: Mapped[str] = mapped_column(String(255), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador: Mapped["Operador"] = relationship(back_populates="adjuntos_operador")

    def __repr__(self) -> str:
        return f"<AdjuntoOperador id={self.id} op={self.operador_id} req={self.requisito}>"


class AdjuntoOperadorDAO:
    """DAO de adjuntos de operador."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(
        self,
        operador_id: int,
        requisito: str,
        storage_key: str,
        content_type: str,
        size: int,
        nombre_original: str,
    ) -> AdjuntoOperador:
        """Crea y persiste un adjunto de operador."""
        with self._session_factory() as session:
            adjunto = AdjuntoOperador(
                operador_id=operador_id,
                requisito=requisito,
                storage_key=storage_key,
                content_type=content_type,
                size=size,
                nombre_original=nombre_original,
            )
            session.add(adjunto)
            session.commit()
            session.refresh(adjunto)
            return adjunto

    def listar_por_operador(self, operador_id: int) -> list[AdjuntoOperador]:
        """Lista todos los adjuntos de un operador."""
        with self._session_factory() as session:
            return (
                session.query(AdjuntoOperador)
                .filter_by(operador_id=operador_id)
                .all()
            )

    def obtener_por_id(self, adjunto_id: int) -> AdjuntoOperador | None:
        """Obtiene un adjunto por su id."""
        with self._session_factory() as session:
            return session.get(AdjuntoOperador, adjunto_id)

    def obtener_por_operador_y_requisito(
        self, operador_id: int, requisito: str
    ) -> AdjuntoOperador | None:
        """Obtiene el adjunto de un operador para un requisito específico."""
        with self._session_factory() as session:
            return (
                session.query(AdjuntoOperador)
                .filter_by(operador_id=operador_id, requisito=requisito)
                .first()
            )

    def eliminar(self, adjunto_id: int) -> bool:
        """Elimina un adjunto. Devuelve True si se eliminó."""
        with self._session_factory() as session:
            adjunto = session.get(AdjuntoOperador, adjunto_id)
            if adjunto is None:
                return False
            session.delete(adjunto)
            session.commit()
            return True
