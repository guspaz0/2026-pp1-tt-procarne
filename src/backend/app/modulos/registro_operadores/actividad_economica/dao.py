"""DAO y modelos ORM del catálogo de actividades económicas (DGR Santiago).

- ``GrupoActividad`` — grupo de actividad económica (letra: A, B, C, ...).
- ``SubgrupoActividad`` — subgrupo de actividad económica.
- ``ActividadEconomica`` — actividad económica concreta (con alícuota).
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class GrupoActividad(Base):
    """Modelo ORM de grupo de actividad económica (letra: A, B, C, ...)."""

    __tablename__ = "grupos_actividad"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(1), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self) -> str:
        return f"<GrupoActividad {self.codigo} {self.descripcion[:40]}>"


class SubgrupoActividad(Base):
    """Modelo ORM de subgrupo de actividad económica."""

    __tablename__ = "subgrupos_actividad"
    __table_args__ = (
        UniqueConstraint("grupo_id", "codigo", name="uq_subgrupo_grupo_codigo"),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos_actividad.id"), nullable=False, index=True
    )

    grupo: Mapped["GrupoActividad"] = relationship()

    def __repr__(self) -> str:
        return f"<SubgrupoActividad {self.codigo} {self.descripcion[:40]}>"


class ActividadEconomica(Base):
    """Modelo ORM de actividad económica (DGR Santiago)."""

    __tablename__ = "actividades_economicas"
    __table_args__ = (
        UniqueConstraint("subgrupo_id", "codigo", name="uq_actividad_subgrupo_codigo"),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    alicuota: Mapped[Optional[float]] = mapped_column(nullable=True)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos_actividad.id"), nullable=False, index=True
    )
    subgrupo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("subgrupos_actividad.id"), nullable=True, index=True
    )

    grupo: Mapped["GrupoActividad"] = relationship()
    subgrupo: Mapped[Optional["SubgrupoActividad"]] = relationship()
    operadores: Mapped[list["OperadorActividad"]] = relationship(back_populates="actividad")
    certificados: Mapped[list["CertificadoActividad"]] = relationship(back_populates="actividad")

    def __repr__(self) -> str:
        return f"<ActividadEconomica {self.codigo} {self.descripcion[:40]}>"


class CatalogoActividadesDAO:
    """DAO del catálogo de actividades económicas (solo lectura)."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar_grupos(self) -> list[GrupoActividad]:
        """Lista los grupos de actividades económicas ordenados por código."""
        with self._session_factory() as session:
            return (
                session.query(GrupoActividad)
                .order_by(GrupoActividad.codigo)
                .all()
            )

    def listar_subgrupos(self, grupo: str | None = None) -> list[SubgrupoActividad]:
        """Lista los subgrupos, opcionalmente filtrados por grupo (código)."""
        with self._session_factory() as session:
            q = session.query(SubgrupoActividad)
            if grupo:
                g = session.query(GrupoActividad).filter_by(codigo=grupo).first()
                if g:
                    q = q.filter_by(grupo_id=g.id)
            return q.order_by(SubgrupoActividad.codigo).all()

    def listar_actividades(self, grupo: str | None = None,
                           subgrupo: str | None = None) -> list[ActividadEconomica]:
        """Lista las actividades económicas, opcionalmente filtradas por grupo/subgrupo (código)."""
        with self._session_factory() as session:
            q = session.query(ActividadEconomica)
            if grupo:
                g = session.query(GrupoActividad).filter_by(codigo=grupo).first()
                if g:
                    q = q.filter_by(grupo_id=g.id)
            if subgrupo:
                sq = session.query(SubgrupoActividad).filter_by(codigo=subgrupo)
                if grupo:
                    g = session.query(GrupoActividad).filter_by(codigo=grupo).first()
                    if g:
                        sq = sq.filter_by(grupo_id=g.id)
                sg = sq.first()
                if sg:
                    q = q.filter_by(subgrupo_id=sg.id)
            return q.order_by(ActividadEconomica.codigo).all()

    def resolver_ids_por_codigos(self, codigos: list[str]) -> list[int]:
        """Devuelve los ids de las actividades cuyo ``codigo`` está en ``codigos``.

        Se usa para resolver las categorías del alta (por su código AFIP) a
        ids del catálogo, para guardarlas en ``operador_actividades``.
        """
        if not codigos:
            return []
        with self._session_factory() as session:
            rows = (
                session.query(ActividadEconomica.id)
                .filter(ActividadEconomica.codigo.in_(codigos))
                .order_by(ActividadEconomica.id)
                .all()
            )
            return [r[0] for r in rows]
