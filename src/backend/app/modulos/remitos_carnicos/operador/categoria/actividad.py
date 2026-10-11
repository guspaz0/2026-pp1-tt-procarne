"""ORM y DAO de la actividad ganadera (Bovino/Bubalino, Porcino, etc.).

Un operador puede pertenecer a una o más actividades. Cada actividad
tiene su propio conjunto de categorías (definidas por AFIP/RFOCB).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Actividad(Base):
    """Actividad ganadera del RFOCB.

    Ejemplos: Bovino/Bubalino, Porcino, Ovino, etc.
    """

    __tablename__ = "actividades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    # Relaciones
    operadores: Mapped[list["Operador"]] = relationship(
        "Operador", secondary="operador_actividades", back_populates="actividades"
    )
    categorias: Mapped[list["CategoriaOperador"]] = relationship(
        "CategoriaOperador", back_populates="actividad"
    )
    categorias_afip: Mapped[list["CategoriaAfip"]] = relationship(
        "CategoriaAfip", back_populates="actividad"
    )

    def __repr__(self) -> str:
        return f"<Actividad id={self.id} nombre={self.nombre!r}>"


class ActividadDAO:
    """Data Access Object de :class:`Actividad`."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, actividad_id: int) -> Optional[Actividad]:
        with self._session_factory() as session:
            return session.get(Actividad, actividad_id)

    def obtener_por_nombre(self, nombre: str) -> Optional[Actividad]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = select(Actividad).where(Actividad.nombre == nombre)
            return session.execute(stmt).scalar_one_or_none()

    def listar(self) -> list[Actividad]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = select(Actividad).order_by(Actividad.nombre)
            return list(session.execute(stmt).scalars().all())

    def guardar(self, actividad: Actividad) -> Actividad:
        with self._session_factory() as session:
            session.add(actividad)
            session.commit()
            session.refresh(actividad)
            return actividad
