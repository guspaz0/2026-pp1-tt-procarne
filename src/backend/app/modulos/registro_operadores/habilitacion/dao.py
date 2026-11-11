"""DAO y modelo ORM de ``Habilitacion``.

Habilitación de un operador para una actividad.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base
from modulos.registro_operadores.enums import EstadoRegistral


class Habilitacion(Base):
    """Modelo ORM de habilitación de un operador para una actividad."""

    __tablename__ = "habilitaciones"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actividad: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default=EstadoRegistral.ACTIVO.value, nullable=False
    )
    fecha_habilitacion: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    operador: Mapped["Operador"] = relationship(back_populates="habilitaciones")

    def __repr__(self) -> str:
        return f"<Habilitacion id={self.id} operador_id={self.operador_id} actividad={self.actividad}>"


class HabilitacionDAO:
    """DAO de habilitaciones."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, operador_id: int, actividad: str,
              fecha_habilitacion: datetime | None = None,
              fecha_vencimiento: datetime | None = None) -> Habilitacion:
        """Crea y persiste una habilitación."""
        with self._session_factory() as session:
            habilitacion = Habilitacion(
                operador_id=operador_id,
                actividad=actividad,
                fecha_habilitacion=fecha_habilitacion,
                fecha_vencimiento=fecha_vencimiento,
            )
            session.add(habilitacion)
            session.commit()
            session.refresh(habilitacion)
            return habilitacion

    def listar_por_operador(self, operador_id: int) -> list[Habilitacion]:
        """Lista las habilitaciones de un operador."""
        with self._session_factory() as session:
            return (
                session.query(Habilitacion)
                .filter_by(operador_id=operador_id)
                .all()
            )
