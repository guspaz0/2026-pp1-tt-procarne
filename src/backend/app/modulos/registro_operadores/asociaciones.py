"""Modelos ORM de las tablas asociativas (N:M) del Módulo I.

- ``operador_actividades``: liga un operador con las actividades económicas
  que realiza (N:M). Ya existía en la BD (migración 6670163758dc); aquí se
  agrega su modelo ORM y el wiring de relaciones.
- ``certificado_actividades``: liga un certificado (F102) con las actividades
  que habilita (N:M). Reemplaza la columna de texto libre
  ``certificados.actividades_economicas`` (que se mantiene de forma
  denormalizada para el PDF, pero la fuente de verdad es esta intermedia).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class OperadorActividad(Base):
    """Asociación N:M entre ``operadores`` y ``actividades_economicas``."""

    __tablename__ = "operador_actividades"
    __table_args__ = (
        UniqueConstraint("operador_id", "actividad_id", name="uq_operador_actividades"),
        {"extend_existing": True},
    )

    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), primary_key=True
    )
    actividad_id: Mapped[int] = mapped_column(
        ForeignKey("actividades_economicas.id", ondelete="CASCADE"), primary_key=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador: Mapped["Operador"] = relationship(back_populates="actividades")
    actividad: Mapped["ActividadEconomica"] = relationship(back_populates="operadores")

    def __repr__(self) -> str:
        return f"<OperadorActividad operador={self.operador_id} actividad={self.actividad_id}>"


class CertificadoActividad(Base):
    """Asociación N:M entre ``certificados`` y ``actividades_economicas``."""

    __tablename__ = "certificado_actividades"
    __table_args__ = (
        UniqueConstraint("certificado_id", "actividad_id", name="uq_certificado_actividades"),
        {"extend_existing": True},
    )

    certificado_id: Mapped[int] = mapped_column(
        ForeignKey("certificados.id", ondelete="CASCADE"), primary_key=True
    )
    actividad_id: Mapped[int] = mapped_column(
        ForeignKey("actividades_economicas.id", ondelete="CASCADE"), primary_key=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    certificado: Mapped["Certificado"] = relationship(back_populates="actividades")
    actividad: Mapped["ActividadEconomica"] = relationship(back_populates="certificados")

    def __repr__(self) -> str:
        return f"<CertificadoActividad certificado={self.certificado_id} actividad={self.actividad_id}>"
