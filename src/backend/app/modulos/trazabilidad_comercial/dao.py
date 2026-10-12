"""ORM y DAO del Módulo II — Trazabilidad Comercial (ROCCA).

Entidades:

- :class:`RegistroTrazabilidad` — registro de ingreso de carne a la
  provincia con origen, establecimiento de faena, DTE, remito, kilos,
  especie y destino comercial.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from configs.db import Base


class RegistroTrazabilidad(Base):
    """Registro de trazabilidad comercial de carne.

    Captura el ingreso de carnes a la provincia con los datos de
    origen, establecimiento de faena, documentos (DTE/remito),
    cantidad, especie y destino comercial.
    """

    __tablename__ = "registros_trazabilidad"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Tipo de ingreso
    tipo_ingreso: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    # Origen de la mercadería
    origen_provincia: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    origen_localidad: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    establecimiento_faena: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Documentos
    numero_dte: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    numero_remito: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)

    # Cantidad y especie
    cantidad_kg: Mapped[float] = mapped_column(Float, nullable=False)
    especie: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Destino comercial
    destino_tipo: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    destino_cuit: Mapped[Optional[str]] = mapped_column(String(13), nullable=True, index=True)
    destino_razon_social: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Estado y metadatos
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="REGISTRADO", index=True)
    fecha_registro: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    fecha_ingreso: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<RegistroTrazabilidad id={self.id} tipo={self.tipo_ingreso!r} "
            f"especie={self.especie!r} kg={self.cantidad_kg} estado={self.estado!r}>"
        )


def _eager_options():
    """Opciones de carga eager (vacío por ahora, sin relaciones ORM)."""
    return []


class RegistroTrazabilidadDAO:
    """Data Access Object del registro de trazabilidad comercial."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, registro_id: int) -> Optional[RegistroTrazabilidad]:
        with self._session_factory() as session:
            return session.get(
                RegistroTrazabilidad, registro_id, options=_eager_options()
            )

    def obtener_por_dte(self, numero_dte: str) -> Optional[RegistroTrazabilidad]:
        with self._session_factory() as session:
            stmt = (
                select(RegistroTrazabilidad)
                .where(RegistroTrazabilidad.numero_dte == numero_dte)
                .order_by(RegistroTrazabilidad.id.desc())
            )
            return session.execute(stmt).scalar_one_or_none()

    def obtener_por_remito(self, numero_remito: str) -> Optional[RegistroTrazabilidad]:
        with self._session_factory() as session:
            stmt = (
                select(RegistroTrazabilidad)
                .where(RegistroTrazabilidad.numero_remito == numero_remito)
                .order_by(RegistroTrazabilidad.id.desc())
            )
            return session.execute(stmt).scalar_one_or_none()

    def listar(
        self,
        tipo_ingreso: Optional[str] = None,
        especie: Optional[str] = None,
        estado: Optional[str] = None,
        origen_provincia: Optional[str] = None,
        destino_cuit: Optional[str] = None,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[RegistroTrazabilidad]:
        with self._session_factory() as session:
            stmt = select(RegistroTrazabilidad).options(*_eager_options())
            if tipo_ingreso is not None:
                stmt = stmt.where(RegistroTrazabilidad.tipo_ingreso == tipo_ingreso)
            if especie is not None:
                stmt = stmt.where(RegistroTrazabilidad.especie == especie)
            if estado is not None:
                stmt = stmt.where(RegistroTrazabilidad.estado == estado)
            if origen_provincia is not None:
                stmt = stmt.where(RegistroTrazabilidad.origen_provincia == origen_provincia)
            if destino_cuit is not None:
                stmt = stmt.where(RegistroTrazabilidad.destino_cuit == destino_cuit)
            if desde is not None:
                stmt = stmt.where(RegistroTrazabilidad.fecha_ingreso >= desde)
            if hasta is not None:
                stmt = stmt.where(RegistroTrazabilidad.fecha_ingreso <= hasta)
            stmt = stmt.order_by(RegistroTrazabilidad.id.desc()).limit(limite).offset(offset)
            return list(session.execute(stmt).unique().scalars().all())

    def guardar(self, registro: RegistroTrazabilidad) -> RegistroTrazabilidad:
        with self._session_factory() as session:
            session.add(registro)
            session.commit()
            session.refresh(registro)
            return registro

    def actualizar(self, registro: RegistroTrazabilidad) -> RegistroTrazabilidad:
        with self._session_factory() as session:
            session.merge(registro)
            session.commit()
            registro_id = registro.id
        return self.obtener_por_id(registro_id)

    def eliminar(self, registro_id: int) -> bool:
        with self._session_factory() as session:
            registro = session.get(RegistroTrazabilidad, registro_id)
            if registro is None:
                return False
            session.delete(registro)
            session.commit()
            return True
