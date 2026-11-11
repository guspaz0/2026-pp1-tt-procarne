"""DAO y modelo ORM de ``Operador`` — operador de la cadena cárnica.

Tabla ``operadores`` — cada fila es una sucursal/establecimiento.
Se vincula a una ``persona`` (entidad legal padre) vía ``persona_id``.
El ``domicilio_comercial`` es el domicilio comercial propio de esta
sucursal, que puede diferir del domicilio de la persona titular.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base
from core.persona.dao import Persona
from modulos.registro_operadores.enums import EstadoRegistral, TipoOperador


class Operador(Base):
    """Modelo ORM de operador de la cadena cárnica."""

    __tablename__ = "operadores"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id"), nullable=False, index=True
    )
    razon_social: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domicilio_comercial: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tipo: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, index=True)
    categoria: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, index=True)
    estado_registral: Mapped[str] = mapped_column(
        String(20), default=EstadoRegistral.PENDIENTE.value, nullable=False, index=True
    )
    alta_fecha: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    baja_fecha: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    persona: Mapped["Persona"] = relationship(back_populates="operadores", lazy="joined")
    habilitaciones: Mapped[list["Habilitacion"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    domicilios_operativos: Mapped[list["DomicilioOperativo"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    requisitos: Mapped[list["RequisitoInscripcion"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    certificados: Mapped[list["Certificado"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    adjuntos: Mapped[list["AdjuntoOperador"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Operador id={self.id} persona_id={self.persona_id} tipo={self.tipo} categoria={self.categoria}>"


class OperadorDAO:
    """DAO de operadores de la cadena cárnica."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, razon_social: str, tipo: TipoOperador | str,
              persona_id: int | None = None,
              domicilio_comercial: str | None = None,
              telefono: str | None = None, email: str | None = None,
              categoria: str | None = None) -> Operador:
        """Crea y persiste un operador nuevo (sucursal/establecimiento).

        El CUIT no se guarda aquí: vive en ``personas.identificador`` vía
        ``persona_id`` (1 persona : N operadores).
        """
        with self._session_factory() as session:
            operador = Operador(
                razon_social=razon_social,
                tipo=tipo if isinstance(tipo, str) else tipo.value,
                persona_id=persona_id,
                domicilio_comercial=domicilio_comercial,
                telefono=telefono,
                email=email,
                categoria=categoria,
                alta_fecha=datetime.now(timezone.utc),
            )
            session.add(operador)
            session.commit()
            session.refresh(operador)
            return operador

    def obtener_por_id(self, operador_id: int) -> Operador | None:
        """Devuelve el operador con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(Operador, operador_id)

    def listar(self, tipo: TipoOperador | str | None = None,
               estado_registral: EstadoRegistral | str | None = None,
               categoria: str | None = None) -> list[Operador]:
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        with self._session_factory() as session:
            query = session.query(Operador)
            if tipo is not None:
                query = query.filter_by(tipo=tipo if isinstance(tipo, str) else tipo.value)
            if estado_registral is not None:
                query = query.filter_by(
                    estado_registral=estado_registral if isinstance(estado_registral, str) else estado_registral.value
                )
            if categoria is not None:
                query = query.filter_by(categoria=categoria)
            return list(query.all())

    def actualizar_estado(self, operador_id: int, estado: EstadoRegistral) -> Operador | None:
        """Actualiza el estado registral de un operador."""
        with self._session_factory() as session:
            operador = session.get(Operador, operador_id)
            if operador is None:
                return None
            operador.estado_registral = estado.value
            if estado == EstadoRegistral.BAJADO:
                operador.baja_fecha = datetime.now(timezone.utc)
            elif estado == EstadoRegistral.ACTIVO:
                operador.baja_fecha = None
            session.commit()
            session.refresh(operador)
            return operador
