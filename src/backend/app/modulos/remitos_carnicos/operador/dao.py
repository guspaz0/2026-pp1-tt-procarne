"""DAO y modelo ORM del operador de la cadena cárnica."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Operador(Base):
    """Modelo ORM de operador de la cadena cárnica."""

    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id"), nullable=False, unique=True, index=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Operador id={self.id} persona_id={self.persona_id}>"


class OperadorDAO:
    """DAO de operadores de la cadena cárnica."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, persona_id: int) -> Operador:
        """Crea y persiste un operador nuevo."""
        with self._session_factory() as session:
            operador = Operador(persona_id=persona_id)
            session.add(operador)
            session.commit()
            session.refresh(operador)
            return operador

    def obtener_por_id(self, operador_id: int) -> Operador | None:
        """Devuelve el operador con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Operador, operador_id)

    def obtener_por_persona(self, persona_id: int) -> Operador | None:
        """Devuelve el operador asociado a una persona, o ``None``."""
        with self._session_factory() as session:
            return (
                session.query(Operador)
                .filter_by(persona_id=persona_id)
                .first()
            )

    def listar(self) -> list[Operador]:
        """Devuelve todos los operadores."""
        with self._session_factory() as session:
            return list(session.query(Operador).all())
