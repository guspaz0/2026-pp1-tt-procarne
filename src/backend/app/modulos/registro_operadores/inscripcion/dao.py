"""DAO y modelo ORM de ``Inscripcion``.

Inscripción de un operador en el registro.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base
from modulos.registro_operadores.enums import TipoInscripcion


class Inscripcion(Base):
    """Modelo ORM de inscripción de un operador en el registro."""

    __tablename__ = "inscripciones"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(
        String(20), default=TipoInscripcion.PRINCIPAL.value, nullable=False
    )
    fecha_inscripcion: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    numero_inscripcion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    operador: Mapped["Operador"] = relationship(back_populates="inscripciones")

    def __repr__(self) -> str:
        return f"<Inscripcion id={self.id} operador_id={self.operador_id}>"


class InscripcionDAO:
    """DAO de inscripciones."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, operador_id: int, tipo: str,
              fecha_inscripcion: datetime | None = None,
              numero_inscripcion: str | None = None) -> Inscripcion:
        """Crea y persiste una inscripción."""
        with self._session_factory() as session:
            inscripcion = Inscripcion(
                operador_id=operador_id,
                tipo=tipo,
                fecha_inscripcion=fecha_inscripcion,
                numero_inscripcion=numero_inscripcion,
            )
            session.add(inscripcion)
            session.commit()
            session.refresh(inscripcion)
            return inscripcion

    def listar_por_operador(self, operador_id: int) -> list[Inscripcion]:
        """Lista las inscripciones de un operador."""
        with self._session_factory() as session:
            return (
                session.query(Inscripcion)
                .filter_by(operador_id=operador_id)
                .all()
            )
