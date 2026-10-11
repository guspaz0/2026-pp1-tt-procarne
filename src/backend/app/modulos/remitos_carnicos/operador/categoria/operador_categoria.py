"""ORM y DAO de la categoría de un operador dentro de una actividad (RFOCB).

Jerarquía:
    Operador (id, CUIT)
    └── Actividad (Bovino/Bubalino, Porcino, ...)
        └── CategoriaOperador (Productor/criador, Invernador, ...)
            ├── situacion (ACTIVO, EXCLUIDO, ...)
            ├── desde_fecha
            └── hasta_fecha
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class CategoriaOperador(Base):
    """Inscripción de un operador en una categoría de una actividad.

    Cada fila representa que un operador está inscripto en una categoría
    específica de una actividad ganadera, con su situación y período
    de vigencia.
    """

    __tablename__ = "operador_categorias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(ForeignKey("operadores.id"), nullable=False, index=True)
    actividad_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("actividades.id"), nullable=True, index=True
    )
    categoria: Mapped[str] = mapped_column(String(120), nullable=False)
    situacion: Mapped[str] = mapped_column(String(40), nullable=False)
    desde_fecha: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    hasta_fecha: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Relaciones
    operador: Mapped["Operador"] = relationship("Operador", back_populates="categorias")
    actividad: Mapped[Optional["Actividad"]] = relationship(
        "Actividad", back_populates="categorias"
    )

    def __repr__(self) -> str:
        return (
            f"<CategoriaOperador operador_id={self.operador_id} "
            f"actividad_id={self.actividad_id} "
            f"categoria={self.categoria!r} "
            f"situacion={self.situacion!r}>"
        )


class CategoriaOperadorDAO:
    """Data Access Object de :class:`CategoriaOperador`."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar_por_operador(self, operador_id: int) -> list[CategoriaOperador]:
        """Todas las categorías de un operador (todas las actividades)."""
        with self._session_factory() as session:
            stmt = select(CategoriaOperador).where(CategoriaOperador.operador_id == operador_id)
            return list(session.execute(stmt).scalars().all())

    def listar_activas_por_operador(self, operador_id: int) -> list[CategoriaOperador]:
        """Categorías activas de un operador."""
        with self._session_factory() as session:
            stmt = (
                select(CategoriaOperador)
                .where(CategoriaOperador.operador_id == operador_id)
                .where(CategoriaOperador.situacion == "ACTIVO")
            )
            return list(session.execute(stmt).scalars().all())

    def listar_por_operador_y_actividad(
        self, operador_id: int, actividad_id: int
    ) -> list[CategoriaOperador]:
        """Categorías de un operador en una actividad específica."""
        with self._session_factory() as session:
            stmt = (
                select(CategoriaOperador)
                .where(CategoriaOperador.operador_id == operador_id)
                .where(CategoriaOperador.actividad_id == actividad_id)
            )
            return list(session.execute(stmt).scalars().all())

    def listar_por_categoria(self, categoria: str, limite: int = 100, offset: int = 0) -> list[CategoriaOperador]:
        with self._session_factory() as session:
            stmt = (
                select(CategoriaOperador)
                .where(CategoriaOperador.categoria == categoria)
                .limit(limite)
                .offset(offset)
            )
            return list(session.execute(stmt).scalars().all())

    def guardar(self, cat: CategoriaOperador) -> CategoriaOperador:
        with self._session_factory() as session:
            session.add(cat)
            session.commit()
            session.refresh(cat)
            return cat

    def eliminar_por_operador(self, operador_id: int) -> int:
        from sqlalchemy import delete

        with self._session_factory() as session:
            result = session.execute(
                delete(CategoriaOperador).where(CategoriaOperador.operador_id == operador_id)
            )
            session.commit()
            return result.rowcount
