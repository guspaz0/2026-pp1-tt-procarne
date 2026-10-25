"""ORM y DAO de la tabla de situaciones (catálogo).

Las situaciones definen el estado de una inscripción de un operador
en una categoría (ACTIVO, INACTIVO, EXCLUIDO, ...).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Situacion(Base):
    """Catálogo de situaciones para inscripciones de operadores."""

    __tablename__ = "situaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Situacion id={self.id} descripcion={self.descripcion!r}>"


class SituacionDAO:
    """DAO de :class:`Situacion`."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar(self) -> list[Situacion]:
        with self._session_factory() as session:
            stmt = select(Situacion).order_by(Situacion.id)
            return list(session.execute(stmt).scalars().all())

    def obtener_por_id(self, situacion_id: int) -> Optional[Situacion]:
        with self._session_factory() as session:
            return session.get(Situacion, situacion_id)

    def obtener_por_descripcion(self, descripcion: str) -> Optional[Situacion]:
        with self._session_factory() as session:
            stmt = select(Situacion).where(Situacion.descripcion == descripcion)
            return session.execute(stmt).scalar_one_or_none()
