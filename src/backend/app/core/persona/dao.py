"""ORM y DAO de la persona (física o jurídica)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from configs.db import Base


class Persona(Base):
    """Persona física o jurídica del registro.

    ``tipo`` distingue física/jurídica; ``identificador`` guarda el DNI
    (física) o el CUIT (jurídica). ``cuit`` es opcional y solo aplica a
    personas físicas inscriptas en AFIP (monotributistas, etc.).
    """

    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    identificador: Mapped[str] = mapped_column(String(13), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    cuit: Mapped[Optional[str]] = mapped_column(String(13), unique=True, index=True, nullable=True)
    domicilio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<Persona tipo={self.tipo} identificador={self.identificador!r}>"


class PersonaDAO:
    """Data Access Object de la persona."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_identificador(self, identificador: str) -> Optional[Persona]:
        with self._session_factory() as session:
            stmt = select(Persona).where(Persona.identificador == identificador)
            return session.execute(stmt).scalar_one_or_none()

    def obtener_por_id(self, persona_id: int) -> Optional[Persona]:
        with self._session_factory() as session:
            return session.get(Persona, persona_id)

    def listar(self, limite: int = 200, offset: int = 0) -> list[Persona]:
        with self._session_factory() as session:
            stmt = (
                select(Persona)
                .order_by(Persona.nombre)
                .limit(limite)
                .offset(offset)
            )
            return list(session.execute(stmt).scalars().all())

    def guardar(self, persona: Persona) -> Persona:
        with self._session_factory() as session:
            session.add(persona)
            session.commit()
            session.refresh(persona)
            return persona
