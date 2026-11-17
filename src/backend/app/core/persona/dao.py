"""DAO y modelo ORM de la persona.

El modelo ORM (``Persona``) hereda de ``Base`` y se registra en
``Base.metadata`` para que Alembic y ``create_all`` lo detecten.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String
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
    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )
    domicilio_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("domicilios.id", ondelete="SET NULL"), nullable=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operadores: Mapped[list["Operador"]] = relationship(
        back_populates="persona"
    )
    adjuntos: Mapped[list["AdjuntoPersona"]] = relationship(
        back_populates="persona", cascade="all, delete-orphan"
    )
    domicilio_rel: Mapped[Optional["Domicilio"]] = relationship(
        back_populates="persona", lazy="joined"
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
              nombre: str, email: str | None = None,
              domicilio_id: int | None = None) -> Persona:
        """Crea y persiste una persona nueva."""
        with self._session_factory() as session:
            persona = Persona(
                tipo=tipo,
                tipo_documento=tipo_documento,
                identificador=identificador,
                nombre=nombre,
                email=email,
                domicilio_id=domicilio_id,
            )
            session.add(persona)
            session.commit()
            session.refresh(persona)
            return persona

    def actualizar(self, persona_id: int, **kwargs) -> Persona | None:
        """Actualiza campos de una persona (p. ej. ``email``, ``nombre``)."""
        with self._session_factory() as session:
            persona = session.get(Persona, persona_id)
            if persona is None:
                return None
            for k, v in kwargs.items():
                if hasattr(persona, k):
                    setattr(persona, k, v)
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

    def obtener_por_email(self, email: str) -> Persona | None:
        """Devuelve la persona con el email dado, o ``None``.

        El email es único por persona (constraint en BD). Se usa para
        detectar colisiones antes de asignar un email a otra persona.
        """
        with self._session_factory() as session:
            return session.query(Persona).filter_by(email=email).first()

    def listar(self) -> list[Persona]:
        """Devuelve todas las personas."""
        with self._session_factory() as session:
            return list(session.query(Persona).all())


