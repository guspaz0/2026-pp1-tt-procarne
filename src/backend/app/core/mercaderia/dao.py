"""DAO y modelo ORM de la mercadería (catálogo genérico)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from configs.db import Base


class Mercaderia(Base):
    """Modelo ORM de mercadería (catálogo genérico)."""

    __tablename__ = "mercaderias_genericas"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    unidad_medida: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    requiere_trazabilidad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requiere_numero_tropa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Mercaderia id={self.id} codigo={self.codigo}>"


class MercaderiaDAO:
    """DAO de mercaderías (catálogo genérico)."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, codigo: str, descripcion: str, unidad_medida: str | None = None,
              requiere_trazabilidad: bool = False,
              requiere_numero_tropa: bool = False) -> Mercaderia:
        """Crea y persiste una mercadería nueva."""
        with self._session_factory() as session:
            mercaderia = Mercaderia(
                codigo=codigo,
                descripcion=descripcion,
                unidad_medida=unidad_medida,
                requiere_trazabilidad=requiere_trazabilidad,
                requiere_numero_tropa=requiere_numero_tropa,
            )
            session.add(mercaderia)
            session.commit()
            session.refresh(mercaderia)
            return mercaderia

    def obtener_por_id(self, mercaderia_id: int) -> Mercaderia | None:
        """Devuelve la mercadería con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Mercaderia, mercaderia_id)

    def obtener_por_codigo_afip(self, codigo: str) -> Mercaderia | None:
        """Devuelve la mercadería con el código AFIP dado, o ``None``."""
        with self._session_factory() as session:
            return (
                session.query(Mercaderia)
                .filter_by(codigo=codigo)
                .first()
            )

    def listar(self) -> list[Mercaderia]:
        """Devuelve todas las mercaderías."""
        with self._session_factory() as session:
            return list(session.query(Mercaderia).all())
