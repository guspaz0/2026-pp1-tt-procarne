"""DAO y modelo ORM de la persona.

El modelo ORM (``Persona``) hereda de ``Base`` y se registra en
``Base.metadata`` para que Alembic y ``create_all`` lo detecten.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Persona(Base):
    """Modelo ORM de persona (física o jurídica)."""

    __tablename__ = "personas"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # FISICA / JURIDICA
    tipo_documento: Mapped[str] = mapped_column(String(10), nullable=False)  # DNI / CUIT
    identificador: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    domicilio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operadores: Mapped[list["ROCCAOperador"]] = relationship(
        back_populates="persona"
    )
    adjuntos: Mapped[list["AdjuntoPersona"]] = relationship(
        back_populates="persona", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Persona id={self.id} {self.tipo} {self.identificador}>"


class PersonaDAO:
    """DAO de personas.

    Encapsula las operaciones de acceso a datos sobre la tabla
    ``personas``.
    """

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, tipo: str, tipo_documento: str, identificador: str,
              nombre: str, domicilio: str | None = None) -> Persona:
        """Crea y persiste una persona nueva."""
        with self._session_factory() as session:
            persona = Persona(
                tipo=tipo,
                tipo_documento=tipo_documento,
                identificador=identificador,
                nombre=nombre,
                domicilio=domicilio,
            )
            session.add(persona)
            session.commit()
            session.refresh(persona)
            return persona

    def obtener_por_id(self, persona_id: int) -> Persona | None:
        """Devuelve la persona con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Persona, persona_id)

    def obtener_por_documento(self, tipo: str, identificador: str) -> Persona | None:
        """Devuelve la persona con el documento dado, o ``None``."""
        with self._session_factory() as session:
            return (
                session.query(Persona)
                .filter_by(tipo_documento=tipo, identificador=identificador)
                .first()
            )

    def listar(self) -> list[Persona]:
        """Devuelve todas las personas."""
        with self._session_factory() as session:
            return list(session.query(Persona).all())

    def actualizar_domicilio(self, persona_id: int, domicilio: str) -> Persona | None:
        """Actualiza el domicilio de una persona."""
        with self._session_factory() as session:
            persona = session.get(Persona, persona_id)
            if persona is None:
                return None
            persona.domicilio = domicilio
            session.commit()
            session.refresh(persona)
            return persona
