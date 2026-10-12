"""ORM y DAO de la mercadería (catálogo genérico de productos)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, String, select
from sqlalchemy.orm import Mapped, mapped_column

from configs.db import Base


class Mercaderia(Base):
    """Catálogo genérico de mercaderías.

    Es la única entidad de mercadería del sistema: almacena el código
    (p. ej. el código AFIP), la descripción, la unidad de medida y los
    flags de trazabilidad y de requerimiento de N° de tropa.
    """

    __tablename__ = "mercaderias_genericas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    unidad_medida: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    requiere_trazabilidad: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requiere_numero_tropa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Mercaderia codigo={self.codigo!r}>"


class MercaderiaDAO:
    """Data Access Object de la mercadería."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_codigo(self, codigo: str) -> Optional[Mercaderia]:
        with self._session_factory() as session:
            stmt = select(Mercaderia).where(Mercaderia.codigo == codigo)
            return session.execute(stmt).scalar_one_or_none()

    def obtener_por_id(self, mercaderia_id: int) -> Optional[Mercaderia]:
        with self._session_factory() as session:
            return session.get(Mercaderia, mercaderia_id)

    def listar(self, limite: int = 200, offset: int = 0) -> list[Mercaderia]:
        with self._session_factory() as session:
            stmt = (
                select(Mercaderia)
                .order_by(Mercaderia.codigo)
                .limit(limite)
                .offset(offset)
            )
            return list(session.execute(stmt).scalars().all())

    def guardar(self, mercaderia: Mercaderia) -> Mercaderia:
        with self._session_factory() as session:
            session.add(mercaderia)
            session.commit()
            session.refresh(mercaderia)
            return mercaderia
