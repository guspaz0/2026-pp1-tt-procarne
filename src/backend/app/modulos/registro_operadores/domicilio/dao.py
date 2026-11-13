"""Modelo ORM de Domicilio.

Cada operador tiene un único domicilio.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Domicilio(Base):
    """Modelo ORM de domicilio de un operador."""

    __tablename__ = "domicilios"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    calle: Mapped[str] = mapped_column(String(100), nullable=False)
    numero: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    localidad: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(50), nullable=False)
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    operadores: Mapped[list["Operador"]] = relationship(back_populates="domicilio")

    def __repr__(self) -> str:
        return f"<Domicilio id={self.id} operador_id={self.operador_id} calle={self.calle}>"


class DomicilioDAO:
    """DAO de domicilios."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, domicilio_id: int) -> Optional[Domicilio]:
        """Obtiene un domicilio por su id."""
        with self._session_factory() as session:
            return session.get(Domicilio, domicilio_id)

    def obtener_por_id(self, domicilio_id: int) -> Optional[Domicilio]:
        """Obtiene un domicilio por su id."""
        with self._session_factory() as session:
            return session.get(Domicilio, domicilio_id)

    def listar(self) -> list[Domicilio]:
        """Lista todos los domicilios."""
        with self._session_factory() as session:
            return list(session.query(Domicilio).all())

    def crear(self, calle: str,
              numero: str | None = None,
              localidad: str = "",
              provincia: str = "",
              codigo_postal: str | None = None) -> Domicilio:
        """Crea y persiste un domicilio nuevo."""
        with self._session_factory() as session:
            dom = Domicilio(
                calle=calle,
                numero=numero,
                localidad=localidad,
                provincia=provincia,
                codigo_postal=codigo_postal,
            )
            session.add(dom)
            session.commit()
            session.refresh(dom)
            return dom

    def actualizar(self, domicilio_id: int, **kwargs) -> Optional[Domicilio]:
        """Actualiza campos de un domicilio."""
        with self._session_factory() as session:
            dom = session.get(Domicilio, domicilio_id)
            if dom is None:
                return None
            for k, v in kwargs.items():
                if hasattr(dom, k):
                    setattr(dom, k, v)
            session.commit()
            session.refresh(dom)
            return dom

    def eliminar(self, domicilio_id: int) -> bool:
        """Elimina un domicilio."""
        with self._session_factory() as session:
            dom = session.get(Domicilio, domicilio_id)
            if dom is None:
                return False
            session.delete(dom)
            session.commit()
            return True
