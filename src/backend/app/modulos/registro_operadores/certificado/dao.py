"""DAO y modelo ORM de ``Certificado``.

Certificado de habilitación (F102) de un operador.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base
from modulos.registro_operadores.enums import EstadoCertificado


class Certificado(Base):
    """Modelo ORM de certificado de habilitación de un operador."""

    __tablename__ = "certificados"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    numero_certificado: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    tipo_certificado: Mapped[str] = mapped_column(String(50), nullable=False, default="HABILITACION")
    fecha_emision: Mapped[datetime] = mapped_column(nullable=False)
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    actividades_economicas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default=EstadoCertificado.ACTIVO.value)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador: Mapped["Operador"] = relationship(back_populates="certificados")

    def __repr__(self) -> str:
        return f"<Certificado {self.numero_certificado} operador={self.operador_id} estado={self.estado}>"


class CertificadoDAO:
    """DAO de certificados de habilitación."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, operador_id: int, numero_certificado: str,
              fecha_emision: datetime,
              tipo_certificado: str = "HABILITACION",
              fecha_vencimiento: datetime | None = None,
              actividades_economicas: str | None = None,
              observaciones: str | None = None) -> Certificado:
        """Crea y persiste un certificado."""
        with self._session_factory() as session:
            cert = Certificado(
                operador_id=operador_id,
                numero_certificado=numero_certificado,
                tipo_certificado=tipo_certificado,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                actividades_economicas=actividades_economicas,
                observaciones=observaciones,
            )
            session.add(cert)
            session.commit()
            session.refresh(cert)
            return cert

    def obtener(self, certificado_id: int) -> Certificado | None:
        """Obtiene un certificado por su id, o ``None``."""
        with self._session_factory() as session:
            return session.get(Certificado, certificado_id)

    def listar_por_operador(self, operador_id: int) -> list[Certificado]:
        """Lista los certificados de un operador (ordenados por emisión)."""
        with self._session_factory() as session:
            return (
                session.query(Certificado)
                .filter_by(operador_id=operador_id)
                .order_by(Certificado.fecha_emision.desc())
                .all()
            )

    def listar_activos_por_operador(self, operador_id: int) -> list[Certificado]:
        """Lista los certificados en estado ACTIVO de un operador."""
        with self._session_factory() as session:
            return (
                session.query(Certificado)
                .filter(
                    Certificado.operador_id == operador_id,
                    Certificado.estado == EstadoCertificado.ACTIVO.value,
                )
                .all()
            )

    def listar_no_relevados_por_operador(self, operador_id: int) -> list[Certificado]:
        """Lista los certificados que NO están en estado RELEVADO."""
        with self._session_factory() as session:
            return (
                session.query(Certificado)
                .filter(
                    Certificado.operador_id == operador_id,
                    Certificado.estado != EstadoCertificado.RELEVADO.value,
                )
                .all()
            )

    def marcar_relevado(self, certificado_id: int) -> None:
        """Pone un certificado en estado RELEVADO."""
        with self._session_factory() as session:
            cert = session.get(Certificado, certificado_id)
            if cert is not None:
                cert.estado = EstadoCertificado.RELEVADO.value
                session.commit()
