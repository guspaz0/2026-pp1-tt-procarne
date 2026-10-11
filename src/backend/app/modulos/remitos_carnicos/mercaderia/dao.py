"""ORM y DAO de la mercadería (catálogo de códigos AFIP)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from configs.db import Base


class Mercaderia(Base):
    """Catálogo de códigos de mercadería (tabla de producción pública AFIP)."""

    __tablename__ = "mercaderias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_afip: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    requiere_numero_tropa: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Mercaderia codigo={self.codigo_afip!r}>"


class MercaderiaDAO:
    """Data Access Object de la mercadería."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_codigo(self, codigo_afip: str) -> Optional[Mercaderia]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = select(Mercaderia).where(Mercaderia.codigo_afip == codigo_afip)
            return session.execute(stmt).scalar_one_or_none()

    def obtener_por_id(self, mercaderia_id: int) -> Optional[Mercaderia]:
        with self._session_factory() as session:
            return session.get(Mercaderia, mercaderia_id)

    def listar(self, limite: int = 200, offset: int = 0) -> list[Mercaderia]:
        from sqlalchemy import select

        with self._session_factory() as session:
            stmt = select(Mercaderia).order_by(Mercaderia.codigo_afip).limit(limite).offset(offset)
            return list(session.execute(stmt).scalars().all())

    def guardar(self, mercaderia: Mercaderia) -> Mercaderia:
        with self._session_factory() as session:
            session.add(mercaderia)
            session.commit()
            session.refresh(mercaderia)
            return mercaderia
