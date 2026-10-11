"""ORM y DAO del Remito Electrónico Cárnico."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class RemitoCarnico(Base):
    """Remito Electrónico Cárnico (carátula + caso + participantes)."""

    __tablename__ = "remitos_carnicos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    punto_emision: Mapped[str] = mapped_column(String(10), nullable=False)
    numero_comprobante: Mapped[str] = mapped_column(String(20), nullable=False)
    caso: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_movimiento: Mapped[str] = mapped_column(String(3), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), default="E", nullable=False)
    fecha_emision: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_vencimiento: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    hoja: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_hojas: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Participantes (FK a operadores)
    titular_id: Mapped[int] = mapped_column(ForeignKey("operadores.id"), nullable=False)
    depositario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("operadores.id"), nullable=True)
    destinatario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("operadores.id"), nullable=True)
    transportista_id: Mapped[int] = mapped_column(ForeignKey("operadores.id"), nullable=False)

    # Datos del transportista
    chofer_apellido_nombre: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    chofer_documento: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    dominio_vehiculo: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relaciones
    titular: Mapped["Operador"] = relationship("Operador", foreign_keys=[titular_id], lazy="joined")
    depositario: Mapped[Optional["Operador"]] = relationship("Operador", foreign_keys=[depositario_id], lazy="joined")
    destinatario: Mapped[Optional["Operador"]] = relationship("Operador", foreign_keys=[destinatario_id], lazy="joined")
    transportista: Mapped["Operador"] = relationship("Operador", foreign_keys=[transportista_id], lazy="joined")
    renglones: Mapped[list["RenglonRemito"]] = relationship(
        "RenglonRemito", back_populates="remito", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<RemitoCarnico {self.punto_emision}-{self.numero_comprobante} caso={self.caso} estado={self.estado!r}>"

    @property
    def codigo_remito(self) -> str:
        return f"{self.punto_emision}-{self.numero_comprobante}"


class RenglonRemito(Base):
    """Renglón del detalle de mercadería transportada (sector F)."""

    __tablename__ = "renglones_remito"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    remito_id: Mapped[int] = mapped_column(ForeignKey("remitos_carnicos.id", ondelete="CASCADE"), nullable=False, index=True)
    mercaderia_id: Mapped[int] = mapped_column(ForeignKey("mercaderias.id"), nullable=False, index=True)
    unidades: Mapped[float] = mapped_column(default=0.0, nullable=False)
    kilos: Mapped[float] = mapped_column(default=0.0, nullable=False)
    numero_tropa: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relaciones
    remito: Mapped["RemitoCarnico"] = relationship("RemitoCarnico", back_populates="renglones")
    mercaderia: Mapped["Mercaderia"] = relationship("Mercaderia", lazy="joined")

    def __repr__(self) -> str:
        return f"<RenglonRemito remito_id={self.remito_id} mercaderia={self.mercaderia.codigo_afip if self.mercaderia else '?'} kg={self.kilos}>"


class RemitoCarnicoDAO:
    """Data Access Object del remito electrónico cárnico."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def guardar(self, remito: RemitoCarnico) -> RemitoCarnico:
        with self._session_factory() as session:
            session.add(remito)
            session.commit()
            session.refresh(remito)
            return remito

    def obtener_por_codigo(self, punto_emision: str, numero_comprobante: str) -> Optional[RemitoCarnico]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = select(RemitoCarnico).where(
                RemitoCarnico.punto_emision == punto_emision,
                RemitoCarnico.numero_comprobante == numero_comprobante,
            )
            return session.execute(stmt).scalar_one_or_none()

    def obtener_por_id(self, remito_id: int) -> Optional[RemitoCarnico]:
        with self._session_factory() as session:
            return session.get(RemitoCarnico, remito_id)

    def listar(
        self,
        estado: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[RemitoCarnico]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = select(RemitoCarnico)
            if estado is not None:
                stmt = stmt.where(RemitoCarnico.estado == estado)
            if desde is not None:
                stmt = stmt.where(RemitoCarnico.fecha_emision >= desde)
            if hasta is not None:
                stmt = stmt.where(RemitoCarnico.fecha_emision <= hasta)
            stmt = stmt.order_by(RemitoCarnico.fecha_emision.desc()).limit(limite).offset(offset)
            return list(session.execute(stmt).scalars().all())

    def anular(self, remito_id: int) -> bool:
        with self._session_factory() as session:
            remito = session.get(RemitoCarnico, remito_id)
            if remito is None or remito.estado == "AN":
                return False
            remito.estado = "AN"
            session.commit()
            return True
