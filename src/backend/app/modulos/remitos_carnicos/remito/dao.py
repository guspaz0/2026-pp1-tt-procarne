"""DAO y modelos ORM del Remito Electrónico Cárnico."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class RemitoCarnico(Base):
    """Modelo ORM de remito electrónico cárnico."""

    __tablename__ = "remitos_carnicos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    punto_emision: Mapped[str] = mapped_column(String(4), nullable=False)
    numero_comprobante: Mapped[str] = mapped_column(String(10), nullable=False)
    caso: Mapped[str] = mapped_column(String(2), nullable=False)
    tipo_movimiento: Mapped[str] = mapped_column(String(30), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="EMITIDO", nullable=False)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_entrega: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Participantes
    titular_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    transportista_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
    destinatario_cuit: Mapped[Optional[str]] = mapped_column(String(13), nullable=True, index=True)
    depositario_cuit: Mapped[Optional[str]] = mapped_column(String(13), nullable=True)

    # Datos del transporte
    chofer_apellido_nombre: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    chofer_documento: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    dominio_vehiculo: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Observaciones
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    renglones: Mapped[list["RenglonRemito"]] = relationship(
        back_populates="remito", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<RemitoCarnico id={self.id} punto={self.punto_emision} "
            f"numero={self.numero_comprobante} caso={self.caso}>"
        )


class RenglonRemito(Base):
    """Modelo ORM de renglón de remito."""

    __tablename__ = "renglones_remito"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    remito_id: Mapped[int] = mapped_column(
        ForeignKey("remitos_carnicos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    codigo_afip: Mapped[str] = mapped_column(String(20), nullable=False)
    unidades: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    kilos: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    numero_tropa: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    remito: Mapped["RemitoCarnico"] = relationship(back_populates="renglones")

    def __repr__(self) -> str:
        return f"<RenglonRemito id={self.id} remito_id={self.remito_id} codigo_afip={self.codigo_afip}>"


class RemitoCarnicoDAO:
    """DAO de remitos electrónicos cárnicos."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, remito: RemitoCarnico) -> RemitoCarnico:
        """Crea y persiste un remito nuevo (con sus renglones)."""
        with self._session_factory() as session:
            session.add(remito)
            session.commit()
            session.refresh(remito)
            return remito

    def obtener_por_id(self, remito_id: int) -> RemitoCarnico | None:
        """Devuelve el remito con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(RemitoCarnico, remito_id)

    def obtener_por_comprobante(self, punto_emision: str, numero_comprobante: str) -> RemitoCarnico | None:
        """Devuelve el remito con el comprobante dado, o ``None``."""
        with self._session_factory() as session:
            return (
                session.query(RemitoCarnico)
                .filter_by(punto_emision=punto_emision, numero_comprobante=numero_comprobante)
                .first()
            )

    def listar(self, estado: str | None = None) -> list[RemitoCarnico]:
        """Devuelve todos los remitos, opcionalmente filtrados por estado."""
        with self._session_factory() as session:
            query = session.query(RemitoCarnico)
            if estado is not None:
                query = query.filter_by(estado=estado)
            return list(query.all())

    def actualizar_estado(self, remito_id: int, estado: str) -> RemitoCarnico | None:
        """Actualiza el estado de un remito."""
        with self._session_factory() as session:
            remito = session.get(RemitoCarnico, remito_id)
            if remito is None:
                return None
            remito.estado = estado
            if estado == "ENTREGADO":
                remito.fecha_entrega = datetime.now(timezone.utc)
            session.commit()
            session.refresh(remito)
            return remito
