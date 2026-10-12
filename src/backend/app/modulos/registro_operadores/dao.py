"""ORM y DAO del Módulo I — Registro Provincial de Operadores (ROCCA).

Entidades:

- :class:`ROCCAOperador` — registro provincial del operador (datos
  identificatorios, tipo de actividad, estado registral).
- :class:`Habilitacion` — habilitación sanitaria/comercial del operador.
- :class:`Inscripcion` — inscripción nacional o provincial (ARCA, SIGSA,
  RFOCB, etc.).
- :class:`DomicilioOperativo` — domicilio operativo (principal o
  secundario) del establecimiento.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from configs.db import Base


class ROCCAOperador(Base):
    """Operador inscripto en el Registro Provincial (Módulo I).

    Se refiere a una :class:`Persona` jurídica (identificada por CUIT)
    y a un tipo de operador de la cadena cárnica. Guarda además el
    estado registral y la fecha de inscripción.
    """

    __tablename__ = "rocca_operadores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id"), unique=True, index=True, nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    estado_registral: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ACTIVO", index=True
    )
    fecha_inscripcion: Mapped[date] = mapped_column(Date, nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relaciones
    persona: Mapped["Persona"] = relationship("Persona", lazy="joined")
    habilitaciones: Mapped[list["Habilitacion"]] = relationship(
        "Habilitacion", back_populates="operador", cascade="all, delete-orphan"
    )
    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        "Inscripcion", back_populates="operador", cascade="all, delete-orphan"
    )
    domicilios: Mapped[list["DomicilioOperativo"]] = relationship(
        "DomicilioOperativo", back_populates="operador", cascade="all, delete-orphan"
    )

    @property
    def cuit(self) -> str:
        return self.persona.identificador

    @property
    def razon_social(self) -> str:
        return self.persona.nombre

    @property
    def domicilio(self) -> Optional[str]:
        return self.persona.domicilio

    @property
    def telefono(self) -> Optional[str]:
        return self.persona.telefono

    @property
    def email(self) -> Optional[str]:
        return self.persona.email

    def __repr__(self) -> str:
        return (
            f"<ROCCAOperador id={self.id} cuit={self.cuit!r} "
            f"tipo={self.tipo!r} estado={self.estado_registral!r}>"
        )


class Habilitacion(Base):
    """Habilitación de un operador (sanitaria, comercial, etc.)."""

    __tablename__ = "rocca_habilitaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("rocca_operadores.id"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(80), nullable=False)
    numero: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    autoridad: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    fecha_emision: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="VIGENTE")

    # Relaciones
    operador: Mapped["ROCCAOperador"] = relationship(
        "ROCCAOperador", back_populates="habilitaciones"
    )

    def __repr__(self) -> str:
        return (
            f"<Habilitacion id={self.id} tipo={self.tipo!r} "
            f"numero={self.numero!r} estado={self.estado!r}>"
        )


class Inscripcion(Base):
    """Inscripción nacional o provincial del operador.

    Ejemplos: RFOCB (nacional), ARCA/AFIP (nacional), SIGSA/Senasa
    (nacional), registro provincial de la Dirección General de
    Agricultura y Ganadería.
    """

    __tablename__ = "rocca_inscripciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("rocca_operadores.id"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # NACIONAL | PROVINCIAL
    organismo: Mapped[str] = mapped_column(String(120), nullable=False)
    numero: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fecha_inscripcion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVA")

    # Relaciones
    operador: Mapped["ROCCAOperador"] = relationship(
        "ROCCAOperador", back_populates="inscripciones"
    )

    def __repr__(self) -> str:
        return (
            f"<Inscripcion id={self.id} tipo={self.tipo!r} "
            f"organismo={self.organismo!r} numero={self.numero!r}>"
        )


class DomicilioOperativo(Base):
    """Domicilio operativo del establecimiento del operador."""

    __tablename__ = "rocca_domicilios_operativos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("rocca_operadores.id"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="PRINCIPAL")
    calle: Mapped[str] = mapped_column(String(255), nullable=False)
    numero: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    localidad: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    departamento: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    provincia: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relaciones
    operador: Mapped["ROCCAOperador"] = relationship(
        "ROCCAOperador", back_populates="domicilios"
    )

    def __repr__(self) -> str:
        return (
            f"<DomicilioOperativo id={self.id} tipo={self.tipo!r} "
            f"calle={self.calle!r} localidad={self.localidad!r}>"
        )


def _eager_options():
    """Opciones de carga eager para :class:`ROCCAOperador`."""
    return [
        selectinload(ROCCAOperador.persona),
        selectinload(ROCCAOperador.habilitaciones),
        selectinload(ROCCAOperador.inscripciones),
        selectinload(ROCCAOperador.domicilios),
    ]


class ROCCAOperadorDAO:
    """Data Access Object del operador del Registro Provincial."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, operador_id: int) -> Optional[ROCCAOperador]:
        with self._session_factory() as session:
            return session.get(
                ROCCAOperador, operador_id, options=_eager_options()
            )

    def obtener_por_cuit(self, cuit: str) -> Optional[ROCCAOperador]:
        with self._session_factory() as session:
            stmt = (
                select(ROCCAOperador)
                .join(ROCCAOperador.persona)
                .where(ROCCAOperador.persona.has(identificador=cuit, tipo="PJ"))
                .options(*_eager_options())
            )
            return session.execute(stmt).unique().scalar_one_or_none()

    def listar(
        self,
        tipo: Optional[str] = None,
        estado_registral: Optional[str] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[ROCCAOperador]:
        with self._session_factory() as session:
            stmt = select(ROCCAOperador).options(*_eager_options())
            if tipo is not None:
                stmt = stmt.where(ROCCAOperador.tipo == tipo)
            if estado_registral is not None:
                stmt = stmt.where(ROCCAOperador.estado_registral == estado_registral)
            stmt = stmt.order_by(ROCCAOperador.id).limit(limite).offset(offset)
            return list(session.execute(stmt).unique().scalars().all())

    def guardar(
        self, operador: ROCCAOperador, persona: Optional["Persona"] = None
    ) -> ROCCAOperador:
        with self._session_factory() as session:
            if persona is not None:
                session.add(persona)
                session.commit()
                session.refresh(persona)
                operador.persona_id = persona.id
            session.add(operador)
            session.commit()
            operador_id = operador.id
        return self.obtener_por_id(operador_id)

    def actualizar(self, operador: ROCCAOperador) -> ROCCAOperador:
        with self._session_factory() as session:
            session.merge(operador)
            session.commit()
            operador_id = operador.id
        return self.obtener_por_id(operador_id)
