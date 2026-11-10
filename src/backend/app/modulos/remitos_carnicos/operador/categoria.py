"""Categorías de operador (actividad, categoría AFIP, situación).

Modelos:
- ``Actividad`` — actividad económica (bovino, porcino, etc.).
- ``CategoriaAfip`` — categoría AFIP asociada a una actividad.
- ``Situcion`` — situación del operador (ACTIVO, INACTIVO, EXCLUIDO).
- ``CategoriaOperador`` — categoría de un operador (asocia operador + categoría AFIP).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Actividad(Base):
    """Modelo ORM de actividad económica."""

    __tablename__ = "actividades"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Actividad id={self.id} nombre={self.nombre}>"


class CategoriaAfip(Base):
    """Modelo ORM de categoría AFIP."""

    __tablename__ = "categorias_afip"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actividad_id: Mapped[int] = mapped_column(
        ForeignKey("actividades.id"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<CategoriaAfip id={self.id} codigo={self.codigo}>"


class Situcion(Base):
    """Modelo ORM de situación del operador."""

    __tablename__ = "situaciones"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    descripcion: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Situcion id={self.id} descripcion={self.descripcion}>"


class CategoriaOperador(Base):
    """Modelo ORM de categoría de un operador."""

    __tablename__ = "operador_categorias"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias_afip.id"), nullable=False
    )
    situacion_id: Mapped[int] = mapped_column(
        ForeignKey("situaciones.id"), nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<CategoriaOperador id={self.id} operador_id={self.operador_id}>"


class ActividadDAO:
    """DAO de actividades económicas."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar(self) -> list[Actividad]:
        """Devuelve todas las actividades."""
        with self._session_factory() as session:
            return list(session.query(Actividad).all())

    def obtener_por_id(self, actividad_id: int) -> Actividad | None:
        """Devuelve la actividad con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Actividad, actividad_id)


class CategoriaAfipDAO:
    """DAO de categorías AFIP."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar(self, actividad_id: int | None = None) -> list[CategoriaAfip]:
        """Devuelve todas las categorías AFIP, opcionalmente filtradas por actividad."""
        with self._session_factory() as session:
            query = session.query(CategoriaAfip)
            if actividad_id is not None:
                query = query.filter_by(actividad_id=actividad_id)
            return list(query.all())

    def obtener_por_codigo(self, codigo: str) -> CategoriaAfip | None:
        """Devuelve la categoría AFIP con el código dado, o ``None``."""
        with self._session_factory() as session:
            return (
                session.query(CategoriaAfip)
                .filter_by(codigo=codigo)
                .first()
            )


class SitucionDAO:
    """DAO de situaciones."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar(self) -> list[Situacion]:
        """Devuelve todas las situaciones."""
        with self._session_factory() as session:
            return list(session.query(Situacion).all())

    def obtener_por_id(self, situacion_id: int) -> Situcion | None:
        """Devuelve la situación con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Situacion, situacion_id)


# Alias para compatibilidad (el nombre "Situcion" es un typo de "Situación")
Situacion = Situcion


class CategoriaOperadorDAO:
    """DAO de categorías de operador."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, operador_id: int, categoria_id: int, situacion_id: int) -> CategoriaOperador:
        """Crea y persiste una categoría de operador."""
        with self._session_factory() as session:
            categoria = CategoriaOperador(
                operador_id=operador_id,
                categoria_id=categoria_id,
                situacion_id=situacion_id,
            )
            session.add(categoria)
            session.commit()
            session.refresh(categoria)
            return categoria

    def listar_por_operador(self, operador_id: int) -> list[CategoriaOperador]:
        """Devuelve las categorías de un operador."""
        with self._session_factory() as session:
            return (
                session.query(CategoriaOperador)
                .filter_by(operador_id=operador_id)
                .all()
            )

    def listar_por_categoria(self, codigo: str) -> list[CategoriaOperador]:
        """Devuelve las categorías de operador con el código AFIP dado."""
        with self._session_factory() as session:
            return (
                session.query(CategoriaOperador)
                .join(CategoriaAfip, CategoriaOperador.categoria_id == CategoriaAfip.id)
                .filter(CategoriaAfip.codigo == codigo)
                .all()
            )
