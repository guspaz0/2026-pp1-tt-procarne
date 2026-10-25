"""ORM y DAO de la persona (física o jurídica)."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, CheckConstraint, select
from sqlalchemy.orm import Mapped, mapped_column

from configs.db import Base


class Persona(Base):
    """Persona física o jurídica del registro.

    - ``tipo``: PF (física) o PJ (jurídica)
    - ``tipo_documento``: DNI o CUIT
    - ``identificador``: 8 dígitos (DNI) o 11 dígitos (CUIT)
    - ``nombre`` + ``apellido``: obligatorios para PF
    - ``razon_social``: obligatorio para PJ (se infiere de apellido+nombre para PF)
    """

    __tablename__ = "personas"
    __table_args__ = (
        CheckConstraint(
            "(tipo_documento = 'DNI' AND LENGTH(identificador) = 8) OR "
            "(tipo_documento = 'CUIT' AND LENGTH(identificador) = 11)",
            name="chk_identificador_longitud",
        ),
        CheckConstraint(
            "tipo IN ('PF', 'PJ')", name="chk_tipo_persona"
        ),
        CheckConstraint(
            "tipo_documento IN ('DNI', 'CUIT')", name="chk_tipo_documento"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(2), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(4), nullable=False)
    identificador: Mapped[str] = mapped_column(String(13), unique=True, index=True, nullable=False)
    nombre: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    apellido: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    razon_social: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domicilio: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    @property
    def nombre_completo(self) -> str:
        """Nombre completo (PF) o razón social (PJ)."""
        if self.tipo == "PJ":
            return self.razon_social or ""
        partes = [p for p in [self.nombre, self.apellido] if p]
        return " ".join(partes)

    def __repr__(self) -> str:
        return f"<Persona tipo={self.tipo} doc={self.tipo_documento} id={self.identificador}>"


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
