"""ORM y DAO del operador de la cadena cárnica."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Table, Column, ForeignKey, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from configs.db import Base

# Tabla intermedia operador <-> actividad (many-to-many)
operador_actividades = Table(
    "operador_actividades",
    Base.metadata,
    Column("cuit", String(13), ForeignKey("operadores.cuit"), primary_key=True),
    Column("actividad_id", Integer, ForeignKey("actividades.id"), primary_key=True),
)


class Operador(Base):
    """Operador de la cadena cárnica (padrón AFIP)."""

    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cuit: Mapped[str] = mapped_column(String(13), unique=True, index=True, nullable=False)
    razon_social: Mapped[str] = mapped_column(String(255), nullable=False)
    domicilio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domicilio_fiscal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    categoria: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    situacion: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)

    # Relaciones
    categorias: Mapped[list["CategoriaOperador"]] = relationship(
        "CategoriaOperador", back_populates="operador", cascade="all, delete-orphan"
    )
    actividades: Mapped[list["Actividad"]] = relationship(
        "Actividad",
        secondary=operador_actividades,
        back_populates="operadores",
    )

    def __repr__(self) -> str:
        return f"<Operador cuit={self.cuit!r} razon_social={self.razon_social!r}>"


def _eager_options():
    """Opciones de carga eager (se resuelven en tiempo de consulta)."""
    from modulos.remitos_carnicos.operador.categoria import Actividad
    return [
        selectinload(Operador.categorias),
        selectinload(Operador.actividades).selectinload(Actividad.categorias_afip),
    ]


class OperadorDAO:
    """Data Access Object del operador."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_cuit(self, cuit: str) -> Optional[Operador]:
        with self._session_factory() as session:
            stmt = select(Operador).where(Operador.cuit == cuit).options(*_eager_options())
            return session.execute(stmt).unique().scalar_one_or_none()

    def obtener_por_id(self, operador_id: int) -> Optional[Operador]:
        with self._session_factory() as session:
            return session.get(Operador, operador_id, options=_eager_options())

    def listar(self, limite: int = 100, offset: int = 0) -> list[Operador]:
        with self._session_factory() as session:
            stmt = select(Operador).options(*_eager_options()).limit(limite).offset(offset)
            return list(session.execute(stmt).unique().scalars().all())

    def listar_por_actividad(self, actividad_id: int, limite: int = 100, offset: int = 0) -> list[Operador]:
        with self._session_factory() as session:
            stmt = (
                select(Operador)
                .join(Operador.actividades)
                .where(Operador.actividades.any(id=actividad_id))
                .options(*_eager_options())
                .limit(limite)
                .offset(offset)
            )
            return list(session.execute(stmt).unique().scalars().all())

    def guardar(self, operador: Operador) -> Operador:
        with self._session_factory() as session:
            session.add(operador)
            session.commit()
            operador_id = operador.id
        # Recargar con relaciones eager
        return self.obtener_por_id(operador_id)

    def actualizar(self, operador: Operador) -> Operador:
        with self._session_factory() as session:
            session.merge(operador)
            session.commit()
            operador_id = operador.id
        # Recargar con relaciones eager
        return self.obtener_por_id(operador_id)
