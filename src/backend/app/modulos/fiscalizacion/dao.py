"""ORM y DAO del Módulo III — Fiscalización (ROCCA).

Entidades:

- :class:`Inspeccion` — inspección geolocalizada de un establecimiento
- :class:`Acta` — acta levantada durante la inspección
- :class:`Decomiso` — decomiso de mercadería
- :class:`Infraccion` — infracción detectada
- :class:`Sancion` — sanción aplicada
- :class:`Reincidencia` — registro de reincidencias por operador
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from configs.db import Base


# ---------------------------------------------------------------------------
# Inspección
# ---------------------------------------------------------------------------


class Inspeccion(Base):
    """Inspección de establecimiento geolocalizada."""

    __tablename__ = "fiscalizacion_inspecciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inspector: Mapped[str] = mapped_column(String(120), nullable=False)
    operador_cuit: Mapped[Optional[str]] = mapped_column(
        String(13), nullable=True, index=True
    )
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    latitud: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitud: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="RUTINA")
    resultado: Mapped[str] = mapped_column(String(30), nullable=False, default="CONFORME")
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    enviada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    actas: Mapped[list["Acta"]] = relationship(
        back_populates="inspeccion", cascade="all, delete-orphan"
    )
    infracciones: Mapped[list["Infraccion"]] = relationship(
        back_populates="inspeccion", cascade="all, delete-orphan"
    )
    decomisos: Mapped[list["Decomiso"]] = relationship(
        back_populates="inspeccion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Inspeccion id={self.id} inspector={self.inspector!r} "
            f"resultado={self.resultado!r}>"
        )


# ---------------------------------------------------------------------------
# Acta
# ---------------------------------------------------------------------------


class Acta(Base):
    """Acta levantada durante una inspección."""

    __tablename__ = "fiscalizacion_actas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inspeccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_inspecciones.id"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    numero: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="BORRADOR")
    fecha_firma: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    inspeccion: Mapped["Inspeccion"] = relationship(back_populates="actas")

    def __repr__(self) -> str:
        return f"<Acta id={self.id} tipo={self.tipo!r} estado={self.estado!r}>"


# ---------------------------------------------------------------------------
# Decomiso
# ---------------------------------------------------------------------------


class Decomiso(Base):
    """Decomiso de mercadería detectado en inspección."""

    __tablename__ = "fiscalizacion_decomisos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inspeccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_inspecciones.id"), nullable=False, index=True
    )
    producto: Mapped[str] = mapped_column(String(255), nullable=False)
    cantidad: Mapped[float] = mapped_column(Float, nullable=False)
    unidad: Mapped[str] = mapped_column(String(20), nullable=False, default="KG")
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    destino: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="EN_CURSADO")

    inspeccion: Mapped["Inspeccion"] = relationship(back_populates="decomisos")

    def __repr__(self) -> str:
        return f"<Decomiso id={self.id} producto={self.producto!r} estado={self.estado!r}>"


# ---------------------------------------------------------------------------
# Infracción
# ---------------------------------------------------------------------------


class Infraccion(Base):
    """Infracción detectada durante una inspección."""

    __tablename__ = "fiscalizacion_infracciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inspeccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_inspecciones.id"), nullable=False, index=True
    )
    operador_cuit: Mapped[Optional[str]] = mapped_column(
        String(13), nullable=True, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    gravedad: Mapped[str] = mapped_column(String(20), nullable=False, default="LEVE")
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    inspeccion: Mapped["Inspeccion"] = relationship(back_populates="infracciones")
    sanciones: Mapped[list["Sancion"]] = relationship(
        back_populates="infraccion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Infraccion id={self.id} tipo={self.tipo!r} gravedad={self.gravedad!r}>"


# ---------------------------------------------------------------------------
# Sanción
# ---------------------------------------------------------------------------


class Sancion(Base):
    """Sanción aplicada por una infracción."""

    __tablename__ = "fiscalizacion_sanciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    infraccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_infracciones.id"), nullable=False, index=True
    )
    operador_cuit: Mapped[Optional[str]] = mapped_column(
        String(13), nullable=True, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    monto: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    fecha_aplicacion: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    fecha_cumplimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    infraccion: Mapped["Infraccion"] = relationship(back_populates="sanciones")

    def __repr__(self) -> str:
        return f"<Sancion id={self.id} tipo={self.tipo!r} estado={self.estado!r}>"


# ---------------------------------------------------------------------------
# Reincidencia
# ---------------------------------------------------------------------------


class Reincidencia(Base):
    """Registro de reincidencias por operador."""

    __tablename__ = "fiscalizacion_reincidencias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ultima_fecha: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Reincidencia cuit={self.operador_cuit!r} cantidad={self.cantidad}>"


# ---------------------------------------------------------------------------
# Opciones de carga eager
# ---------------------------------------------------------------------------


def _inspeccion_options():
    return [
        "selectinload(Inspeccion.actas)",
        "selectinload(Inspeccion.infracciones)",
        "selectinload(Inspeccion.decomisos)",
    ]


def _infraccion_options():
    return ["selectinload(Infraccion.sanciones)"]


# ---------------------------------------------------------------------------
# DAO
# ---------------------------------------------------------------------------


class FiscalizacionDAO:
    """Data Access Object del Módulo de Fiscalización."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    # ---- Inspecciones ----------------------------------------------------

    def obtener_inspeccion(self, inspeccion_id: int) -> Optional[Inspeccion]:
        from sqlalchemy.orm import selectinload

        with self._session_factory() as session:
            stmt = (
                select(Inspeccion)
                .options(
                    selectinload(Inspeccion.actas),
                    selectinload(Inspeccion.infracciones).selectinload(Infraccion.sanciones),
                    selectinload(Inspeccion.decomisos),
                )
                .where(Inspeccion.id == inspeccion_id)
            )
            return session.execute(stmt).unique().scalar_one_or_none()

    def listar_inspecciones(
        self,
        operador_cuit: Optional[str] = None,
        resultado: Optional[str] = None,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[Inspeccion]:
        with self._session_factory() as session:
            stmt = (
                select(Inspeccion)
                .options(
                    selectinload(Inspeccion.actas),
                    selectinload(Inspeccion.infracciones).selectinload(Infraccion.sanciones),
                    selectinload(Inspeccion.decomisos),
                )
            )
            if operador_cuit is not None:
                stmt = stmt.where(Inspeccion.operador_cuit == operador_cuit)
            if resultado is not None:
                stmt = stmt.where(Inspeccion.resultado == resultado)
            if desde is not None:
                stmt = stmt.where(Inspeccion.fecha >= datetime.combine(desde, datetime.min.time()))
            if hasta is not None:
                stmt = stmt.where(Inspeccion.fecha <= datetime.combine(hasta, datetime.max.time()))
            stmt = stmt.order_by(Inspeccion.id.desc()).limit(limite).offset(offset)
            return list(session.execute(stmt).unique().scalars().all())

    def guardar_inspeccion(self, inspeccion: Inspeccion) -> Inspeccion:
        with self._session_factory() as session:
            session.add(inspeccion)
            session.commit()
            session.refresh(inspeccion)
            return inspeccion

    def actualizar_inspeccion(self, inspeccion: Inspeccion) -> Inspeccion:
        with self._session_factory() as session:
            session.merge(inspeccion)
            session.commit()
            inspeccion_id = inspeccion.id
        return self.obtener_inspeccion(inspeccion_id)

    def eliminar_inspeccion(self, inspeccion_id: int) -> bool:
        with self._session_factory() as session:
            inspeccion = session.get(Inspeccion, inspeccion_id)
            if inspeccion is None:
                return False
            session.delete(inspeccion)
            session.commit()
            return True

    # ---- Actas -----------------------------------------------------------

    def guardar_acta(self, acta: Acta) -> Acta:
        with self._session_factory() as session:
            session.add(acta)
            session.commit()
            session.refresh(acta)
            return acta

    def actualizar_acta(self, acta: Acta) -> Acta:
        with self._session_factory() as session:
            session.merge(acta)
            session.commit()
            acta_id = acta.id
        with self._session_factory() as session:
            return session.get(Acta, acta_id)

    # ---- Decomisos -------------------------------------------------------

    def guardar_decomiso(self, decomiso: Decomiso) -> Decomiso:
        with self._session_factory() as session:
            session.add(decomiso)
            session.commit()
            session.refresh(decomiso)
            return decomiso

    def actualizar_decomiso(self, decomiso: Decomiso) -> Decomiso:
        with self._session_factory() as session:
            session.merge(decomiso)
            session.commit()
            decomiso_id = decomiso.id
        with self._session_factory() as session:
            return session.get(Decomiso, decomiso_id)

    # ---- Infracciones ----------------------------------------------------

    def guardar_infraccion(self, infraccion: Infraccion) -> Infraccion:
        with self._session_factory() as session:
            session.add(infraccion)
            session.commit()
            session.refresh(infraccion)
            return infraccion

    def listar_infracciones(
        self,
        operador_cuit: Optional[str] = None,
        gravedad: Optional[str] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[Infraccion]:
        with self._session_factory() as session:
            stmt = (
                select(Infraccion)
                .options(selectinload(Infraccion.sanciones))
            )
            if operador_cuit is not None:
                stmt = stmt.where(Infraccion.operador_cuit == operador_cuit)
            if gravedad is not None:
                stmt = stmt.where(Infraccion.gravedad == gravedad)
            stmt = stmt.order_by(Infraccion.id.desc()).limit(limite).offset(offset)
            return list(session.execute(stmt).unique().scalars().all())

    # ---- Sanciones -------------------------------------------------------

    def guardar_sancion(self, sancion: Sancion) -> Sancion:
        with self._session_factory() as session:
            session.add(sancion)
            session.commit()
            session.refresh(sancion)
            return sancion

    def actualizar_sancion(self, sancion: Sancion) -> Sancion:
        with self._session_factory() as session:
            session.merge(sancion)
            session.commit()
            sancion_id = sancion.id
        with self._session_factory() as session:
            return session.get(Sancion, sancion_id)

    # ---- Reincidencias ---------------------------------------------------

    def obtener_reincidencia(self, operador_cuit: str) -> Optional[Reincidencia]:
        with self._session_factory() as session:
            stmt = select(Reincidencia).where(Reincidencia.operador_cuit == operador_cuit)
            return session.execute(stmt).scalar_one_or_none()

    def incrementar_reincidencia(self, operador_cuit: str, observaciones: Optional[str] = None) -> Reincidencia:
        """Incrementa el contador de reincidencias del operador."""
        with self._session_factory() as session:
            rec = session.execute(
                select(Reincidencia).where(Reincidencia.operador_cuit == operador_cuit)
            ).scalar_one_or_none()
            if rec is None:
                rec = Reincidencia(
                    operador_cuit=operador_cuit,
                    cantidad=1,
                    ultima_fecha=date.today(),
                    observaciones=observaciones,
                )
                session.add(rec)
            else:
                rec.cantidad += 1
                rec.ultima_fecha = date.today()
                if observaciones:
                    rec.observaciones = (
                        f"{rec.observaciones}\n{observaciones}".strip()
                        if rec.observaciones
                        else observaciones
                    )
            session.commit()
            session.refresh(rec)
            return rec

    def listar_reincidencias(
        self, limite: int = 100, offset: int = 0
    ) -> list[Reincidencia]:
        with self._session_factory() as session:
            stmt = (
                select(Reincidencia)
                .order_by(Reincidencia.cantidad.desc())
                .limit(limite)
                .offset(offset)
            )
            return list(session.execute(stmt).scalars().all())
