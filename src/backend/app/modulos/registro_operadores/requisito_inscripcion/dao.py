"""DAO y modelo ORM de ``RequisitoInscripcion``.

Cada requisito puede ser general (común a todas las categorías) o
específico (vinculado a una categoría de operador).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class RequisitoInscripcion(Base):
    """Modelo ORM de requisito de inscripción cumplido por un operador."""

    __tablename__ = "requisitos_inscripcion"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    codigo: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    es_general: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cumplido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_cumplimiento: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador: Mapped["Operador"] = relationship(back_populates="requisitos")

    def __repr__(self) -> str:
        return f"<RequisitoInscripcion id={self.id} operador_id={self.operador_id} codigo={self.codigo} cumplido={self.cumplido}>"


class RequisitoInscripcionDAO:
    """DAO de requisitos de inscripción."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener(self, requisito_id: int) -> RequisitoInscripcion | None:
        """Obtiene un requisito por su id, o ``None``."""
        with self._session_factory() as session:
            return session.get(RequisitoInscripcion, requisito_id)

    def listar_por_operador(self, operador_id: int) -> list[RequisitoInscripcion]:
        """Lista los requisitos de inscripción de un operador."""
        with self._session_factory() as session:
            return (
                session.query(RequisitoInscripcion)
                .filter_by(operador_id=operador_id)
                .all()
            )

    def actualizar_cumplimiento(self, requisito_id: int, cumplido: bool,
                                observaciones: str | None = None) -> RequisitoInscripcion | None:
        """Actualiza el estado de cumplimiento de un requisito."""
        with self._session_factory() as session:
            requisito = session.get(RequisitoInscripcion, requisito_id)
            if requisito is None:
                return None
            requisito.cumplido = cumplido
            if observaciones is not None:
                requisito.observaciones = observaciones
            if cumplido:
                requisito.fecha_cumplimiento = datetime.now(timezone.utc)
            else:
                requisito.fecha_cumplimiento = None
            session.commit()
            session.refresh(requisito)
            return requisito
