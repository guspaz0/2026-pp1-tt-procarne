"""DAO y modelo ORM de ``DomicilioOperativo``.

Domicilio operativo de un operador.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base
from modulos.registro_operadores.enums import TipoDomicilio


class DomicilioOperativo(Base):
    """Modelo ORM de domicilio operativo de un operador."""

    __tablename__ = "domicilios_operativos"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(
        String(20), default=TipoDomicilio.OPERATIVO.value, nullable=False
    )
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    localidad: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    provincia: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    es_principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    operador: Mapped["Operador"] = relationship(back_populates="domicilios_operativos")

    def __repr__(self) -> str:
        return f"<DomicilioOperativo id={self.id} operador_id={self.operador_id}>"


class DomicilioOperativoDAO:
    """DAO de domicilios operativos."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, operador_id: int, direccion: str,
              localidad: str | None = None, provincia: str | None = None,
              codigo_postal: str | None = None, es_principal: bool = False) -> DomicilioOperativo:
        """Crea y persiste un domicilio operativo."""
        with self._session_factory() as session:
            domicilio = DomicilioOperativo(
                operador_id=operador_id,
                direccion=direccion,
                localidad=localidad,
                provincia=provincia,
                codigo_postal=codigo_postal,
                es_principal=es_principal,
            )
            session.add(domicilio)
            session.commit()
            session.refresh(domicilio)
            return domicilio

    def listar_por_operador(self, operador_id: int) -> list[DomicilioOperativo]:
        """Lista los domicilios operativos de un operador."""
        with self._session_factory() as session:
            return (
                session.query(DomicilioOperativo)
                .filter_by(operador_id=operador_id)
                .all()
            )
