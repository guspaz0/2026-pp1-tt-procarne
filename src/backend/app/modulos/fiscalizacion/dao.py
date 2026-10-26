"""DAO y modelos ORM del Módulo III — Fiscalización.

Modelos:
- ``Inspeccion`` — inspección realizada a un operador.
- ``Acta`` — acta de inspección, decomiso, infracción o sanción.
- ``Decomiso`` — decomiso de mercadería.
- ``Infraccion`` — infracción detectada.
- ``Sancion`` — sanción aplicada.
- ``Reincidencia`` — reincidencia de un operador.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Inspeccion(Base):
    """Modelo ORM de inspección."""

    __tablename__ = "fiscalizacion_inspecciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    operador_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    inspector: Mapped[str] = mapped_column(String(120), nullable=False)
    resultado: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

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
        return f"<Inspeccion id={self.id} operador_cuit={self.operador_cuit}>"


class Acta(Base):
    """Modelo ORM de acta."""

    __tablename__ = "fiscalizacion_actas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inspeccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_inspecciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default="BORRADOR", nullable=False
    )
    contenido: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    firmado_por: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    fecha_firma: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    inspeccion: Mapped["Inspeccion"] = relationship(back_populates="actas")

    def __repr__(self) -> str:
        return f"<Acta id={self.id} inspeccion_id={self.inspeccion_id} tipo={self.tipo}>"


class Decomiso(Base):
    """Modelo ORM de decomiso."""

    __tablename__ = "fiscalizacion_decomisos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inspeccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_inspecciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mercaderia: Mapped[str] = mapped_column(String(255), nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    peso_kg: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default="PENDIENTE", nullable=False
    )
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    inspeccion: Mapped["Inspeccion"] = relationship(back_populates="decomisos")

    def __repr__(self) -> str:
        return f"<Decomiso id={self.id} inspeccion_id={self.inspeccion_id}>"


class Infraccion(Base):
    """Modelo ORM de infracción."""

    __tablename__ = "fiscalizacion_infracciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inspeccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_inspecciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operador_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    gravedad: Mapped[str] = mapped_column(String(20), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    inspeccion: Mapped["Inspeccion"] = relationship(back_populates="infracciones")
    sanciones: Mapped[list["Sancion"]] = relationship(
        back_populates="infraccion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Infraccion id={self.id} operador_cuit={self.operador_cuit}>"


class Sancion(Base):
    """Modelo ORM de sanción."""

    __tablename__ = "fiscalizacion_sanciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    infraccion_id: Mapped[int] = mapped_column(
        ForeignKey("fiscalizacion_infracciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operador_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    monto: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    estado: Mapped[str] = mapped_column(
        String(20), default="PENDIENTE", nullable=False
    )
    fecha_notificacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_pago: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    infraccion: Mapped["Infraccion"] = relationship(back_populates="sanciones")

    def __repr__(self) -> str:
        return f"<Sancion id={self.id} infraccion_id={self.infraccion_id}>"


class Reincidencia(Base):
    """Modelo ORM de reincidencia."""

    __tablename__ = "fiscalizacion_reincidencias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    cantidad_infracciones: Mapped[int] = mapped_column(default=0, nullable=False)
    ultima_fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Reincidencia id={self.id} operador_cuit={self.operador_cuit}>"


class FiscalizacionDAO:
    """DAO de fiscalización."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    # ------------------------------------------------------------------
    # Inspecciones
    # ------------------------------------------------------------------

    def crear_inspeccion(self, inspeccion: Inspeccion) -> Inspeccion:
        """Crea y persiste una inspección."""
        with self._session_factory() as session:
            session.add(inspeccion)
            session.commit()
            session.refresh(inspeccion)
            return inspeccion

    def obtener_inspeccion(self, inspeccion_id: int) -> Inspeccion | None:
        """Devuelve la inspección con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Inspeccion, inspeccion_id)

    def listar_inspecciones(self, operador_cuit: str | None = None) -> list[Inspeccion]:
        """Lista inspecciones, opcionalmente filtradas por operador."""
        with self._session_factory() as session:
            query = session.query(Inspeccion)
            if operador_cuit is not None:
                query = query.filter_by(operador_cuit=operador_cuit)
            return list(query.all())

    # ------------------------------------------------------------------
    # Actas
    # ------------------------------------------------------------------

    def crear_acta(self, acta: Acta) -> Acta:
        """Crea y persiste un acta."""
        with self._session_factory() as session:
            session.add(acta)
            session.commit()
            session.refresh(acta)
            return acta

    def obtener_acta(self, acta_id: int) -> Acta | None:
        """Devuelve el acta con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Acta, acta_id)

    def listar_actas(self, inspeccion_id: int | None = None) -> list[Acta]:
        """Lista actas, opcionalmente filtradas por inspección."""
        with self._session_factory() as session:
            query = session.query(Acta)
            if inspeccion_id is not None:
                query = query.filter_by(inspeccion_id=inspeccion_id)
            return list(query.all())

    def actualizar_acta(self, acta: Acta) -> Acta:
        """Actualiza un acta existente."""
        with self._session_factory() as session:
            session.add(acta)
            session.commit()
            session.refresh(acta)
            return acta

    # ------------------------------------------------------------------
    # Decomisos
    # ------------------------------------------------------------------

    def crear_decomiso(self, decomiso: Decomiso) -> Decomiso:
        """Crea y persiste un decomiso."""
        with self._session_factory() as session:
            session.add(decomiso)
            session.commit()
            session.refresh(decomiso)
            return decomiso

    def obtener_decomiso(self, decomiso_id: int) -> Decomiso | None:
        """Devuelve el decomiso con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Decomiso, decomiso_id)

    def listar_decomisos(self, inspeccion_id: int | None = None) -> list[Decomiso]:
        """Lista decomisos, opcionalmente filtrados por inspección."""
        with self._session_factory() as session:
            query = session.query(Decomiso)
            if inspeccion_id is not None:
                query = query.filter_by(inspeccion_id=inspeccion_id)
            return list(query.all())

    # ------------------------------------------------------------------
    # Infracciones
    # ------------------------------------------------------------------

    def crear_infraccion(self, infraccion: Infraccion) -> Infraccion:
        """Crea y persiste una infracción."""
        with self._session_factory() as session:
            session.add(infraccion)
            session.commit()
            session.refresh(infraccion)
            return infraccion

    def obtener_infraccion(self, infraccion_id: int) -> Infraccion | None:
        """Devuelve la infracción con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Infraccion, infraccion_id)

    def listar_infracciones(self, operador_cuit: str | None = None) -> list[Infraccion]:
        """Lista infracciones, opcionalmente filtradas por operador."""
        with self._session_factory() as session:
            query = session.query(Infraccion)
            if operador_cuit is not None:
                query = query.filter_by(operador_cuit=operador_cuit)
            return list(query.all())

    # ------------------------------------------------------------------
    # Sanciones
    # ------------------------------------------------------------------

    def crear_sancion(self, sancion: Sancion) -> Sancion:
        """Crea y persiste una sanción."""
        with self._session_factory() as session:
            session.add(sancion)
            session.commit()
            session.refresh(sancion)
            return sancion

    def obtener_sancion(self, sancion_id: int) -> Sancion | None:
        """Devuelve la sanción con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Sancion, sancion_id)

    def listar_sanciones(self, operador_cuit: str | None = None) -> list[Sancion]:
        """Lista sanciones, opcionalmente filtradas por operador."""
        with self._session_factory() as session:
            query = session.query(Sancion)
            if operador_cuit is not None:
                query = query.filter_by(operador_cuit=operador_cuit)
            return list(query.all())

    def actualizar_sancion(self, sancion: Sancion) -> Sancion:
        """Actualiza una sanción existente."""
        with self._session_factory() as session:
            session.add(sancion)
            session.commit()
            session.refresh(sancion)
            return sancion

    # ------------------------------------------------------------------
    # Reincidencias
    # ------------------------------------------------------------------

    def obtener_reincidencia(self, operador_cuit: str) -> Reincidencia | None:
        """Devuelve la reincidencia de un operador, o ``None``."""
        with self._session_factory() as session:
            return (
                session.query(Reincidencia)
                .filter_by(operador_cuit=operador_cuit)
                .first()
            )

    def actualizar_reincidencia(self, operador_cuit: str) -> Reincidencia:
        """Actualiza la reincidencia de un operador."""
        with self._session_factory() as session:
            reincidencia = (
                session.query(Reincidencia)
                .filter_by(operador_cuit=operador_cuit)
                .first()
            )
            if reincidencia is None:
                reincidencia = Reincidencia(
                    operador_cuit=operador_cuit,
                    cantidad_infracciones=1,
                    ultima_fecha=datetime.now(timezone.utc),
                )
                session.add(reincidencia)
            else:
                reincidencia.cantidad_infracciones += 1
                reincidencia.ultima_fecha = datetime.now(timezone.utc)
            session.commit()
            session.refresh(reincidencia)
            return reincidencia
