"""ORM y DAO del catálogo de categorías AFIP por actividad.

Las categorías son un catálogo fijo definido por normativa. Cada
actividad (Bovino/Bubalino, Porcino, ...) tiene su propio conjunto
de categorías. Los operadores se inscriben en una categoría
específica de una actividad.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class CategoriaAfip(Base):
    """Categoría del RFOCB para una actividad ganadera.

    Catálogo fijo de referencia. Ejemplos:
    - Bovino/Bubalino: "Productor/criador", "Invernador", "Feed lots"...
    - Porcino: "Productores/Criadores Comerciales", "Invernadores"...
    """

    __tablename__ = "categorias_afip"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actividad_id: Mapped[int] = mapped_column(ForeignKey("actividades.id"), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relación con la actividad
    actividad: Mapped["Actividad"] = relationship("Actividad", back_populates="categorias_afip")

    def __repr__(self) -> str:
        return f"<CategoriaAfip codigo={self.codigo!r} descripcion={self.descripcion!r}>"


class CategoriaAfipDAO:
    """Data Access Object de :class:`CategoriaAfip`."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar_por_actividad(self, actividad_id: int) -> list[CategoriaAfip]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = (
                select(CategoriaAfip)
                .where(CategoriaAfip.actividad_id == actividad_id)
                .order_by(CategoriaAfip.codigo)
            )
            return list(session.execute(stmt).scalars().all())

    def obtener_por_codigo(self, actividad_id: int, codigo: str) -> Optional[CategoriaAfip]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = (
                select(CategoriaAfip)
                .where(CategoriaAfip.actividad_id == actividad_id)
                .where(CategoriaAfip.codigo == codigo)
            )
            return session.execute(stmt).scalar_one_or_none()

    def listar(self) -> list[CategoriaAfip]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = select(CategoriaAfip).order_by(CategoriaAfip.actividad_id, CategoriaAfip.codigo)
            return list(session.execute(stmt).scalars().all())
