"""DAO y modelo ORM de adjuntos de persona.

Los adjuntos de persona son documentos de identidad e impositivos
compartidos entre todos los operadores de la persona (DNI, CUIT, IIBB).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class AdjuntoPersona(Base):
    """Modelo ORM de adjunto (documento) de una persona."""

    __tablename__ = "adjuntos_persona"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requisito: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre_original: Mapped[str] = mapped_column(String(255), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    persona: Mapped["Persona"] = relationship(back_populates="adjuntos")

    def __repr__(self) -> str:
        return f"<AdjuntoPersona id={self.id} persona={self.persona_id} req={self.requisito}>"


class AdjuntoPersonaDAO:
    """DAO de adjuntos de persona."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(
        self,
        persona_id: int,
        requisito: str,
        storage_key: str,
        content_type: str,
        size: int,
        nombre_original: str,
    ) -> AdjuntoPersona:
        """Crea y persiste un adjunto de persona."""
        with self._session_factory() as session:
            adjunto = AdjuntoPersona(
                persona_id=persona_id,
                requisito=requisito,
                storage_key=storage_key,
                content_type=content_type,
                size=size,
                nombre_original=nombre_original,
            )
            session.add(adjunto)
            session.commit()
            session.refresh(adjunto)
            return adjunto

    def listar_por_persona(self, persona_id: int) -> list[AdjuntoPersona]:
        """Lista todos los adjuntos de una persona."""
        with self._session_factory() as session:
            return (
                session.query(AdjuntoPersona)
                .filter_by(persona_id=persona_id)
                .all()
            )

    def obtener_por_id(self, adjunto_id: int) -> AdjuntoPersona | None:
        """Obtiene un adjunto por su id."""
        with self._session_factory() as session:
            return session.get(AdjuntoPersona, adjunto_id)

    def obtener_por_persona_y_requisito(
        self, persona_id: int, requisito: str
    ) -> AdjuntoPersona | None:
        """Obtiene el adjunto de una persona para un requisito específico."""
        with self._session_factory() as session:
            return (
                session.query(AdjuntoPersona)
                .filter_by(persona_id=persona_id, requisito=requisito)
                .first()
            )

    def eliminar(self, adjunto_id: int) -> bool:
        """Elimina un adjunto. Devuelve True si se eliminó."""
        with self._session_factory() as session:
            adjunto = session.get(AdjuntoPersona, adjunto_id)
            if adjunto is None:
                return False
            session.delete(adjunto)
            session.commit()
            return True
