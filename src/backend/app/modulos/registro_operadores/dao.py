"""DAO y modelos ORM del Módulo I — Registro Provincial de Operadores.

Modelos:
- ``ROCCAOperador`` — operador de la cadena cárnica.
- ``Habilitacion`` — habilitación de un operador para una actividad.
- ``Inscripcion`` — inscripción de un operador en el registro.
- ``DomicilioOperativo`` — domicilio operativo de un operador.
- ``RequisitoInscripcion`` — requisito (general o específico) cumplido por un operador.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base
from core.persona.dao import Persona
from modulos.registro_operadores.enums import (
    EstadoRegistral,
    TipoDomicilio,
    TipoInscripcion,
    TipoOperador,
)


class ROCCAOperador(Base):
    """Modelo ORM de operador de la cadena cárnica.

    Tabla ``operadores`` — cada fila es una sucursal/establecimiento.
    Se vincula a una ``persona`` (entidad legal padre) vía ``persona_id``.
    El ``domicilio`` es el domicilio comercial propio de esta sucursal,
    que puede diferir del domicilio de la persona titular.
    """

    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id"), nullable=False, index=True
    )
    cuit: Mapped[str] = mapped_column(String(13), nullable=False, unique=True, index=True)
    razon_social: Mapped[str] = mapped_column(String(255), nullable=False)
    domicilio_comercial: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    categoria: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, index=True)
    estado_registral: Mapped[str] = mapped_column(
        String(20), default=EstadoRegistral.ACTIVO.value, nullable=False, index=True
    )
    alta_fecha: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    baja_fecha: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    persona: Mapped["Persona"] = relationship(back_populates="operadores")
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

    def __repr__(self) -> str:
        return f"<ROCCAOperador id={self.id} cuit={self.cuit} tipo={self.tipo} categoria={self.categoria}>"


class Habilitacion(Base):
    """Modelo ORM de habilitación de un operador para una actividad."""

    __tablename__ = "habilitaciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    actividad: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20), default=EstadoRegistral.ACTIVO.value, nullable=False
    )
    fecha_habilitacion: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    operador: Mapped["ROCCAOperador"] = relationship(back_populates="habilitaciones")

    def __repr__(self) -> str:
        return f"<Habilitacion id={self.id} operador_id={self.operador_id} actividad={self.actividad}>"


class Inscripcion(Base):
    """Modelo ORM de inscripción de un operador en el registro."""

    __tablename__ = "inscripciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(
        String(20), default=TipoInscripcion.PRINCIPAL.value, nullable=False
    )
    fecha_inscripcion: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    numero_inscripcion: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    operador: Mapped["ROCCAOperador"] = relationship(back_populates="inscripciones")

    def __repr__(self) -> str:
        return f"<Inscripcion id={self.id} operador_id={self.operador_id}>"


class GrupoActividad(Base):
    """Modelo ORM de grupo de actividad económica (letra: A, B, C, ...)."""

    __tablename__ = "grupos_actividad"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(1), nullable=False, unique=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)

    def __repr__(self) -> str:
        return f"<GrupoActividad {self.codigo} {self.descripcion[:40]}>"


class SubgrupoActividad(Base):
    """Modelo ORM de subgrupo de actividad económica."""

    __tablename__ = "subgrupos_actividad"
    __table_args__ = (UniqueConstraint("grupo_id", "codigo", name="uq_subgrupo_grupo_codigo"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos_actividad.id"), nullable=False, index=True
    )

    grupo: Mapped["GrupoActividad"] = relationship()

    def __repr__(self) -> str:
        return f"<SubgrupoActividad {self.codigo} {self.descripcion[:40]}>"


class ActividadEconomica(Base):
    """Modelo ORM de actividad económica (DGR Santiago)."""

    __tablename__ = "actividades_economicas"
    __table_args__ = (UniqueConstraint("subgrupo_id", "codigo", name="uq_actividad_subgrupo_codigo"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    alicuota: Mapped[Optional[float]] = mapped_column(nullable=True)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupos_actividad.id"), nullable=False, index=True
    )
    subgrupo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("subgrupos_actividad.id"), nullable=True, index=True
    )

    grupo: Mapped["GrupoActividad"] = relationship()
    subgrupo: Mapped[Optional["SubgrupoActividad"]] = relationship()

    def __repr__(self) -> str:
        return f"<ActividadEconomica {self.codigo} {self.descripcion[:40]}>"


class Certificado(Base):
    """Modelo ORM de certificado de habilitación de un operador."""

    __tablename__ = "certificados"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    numero_certificado: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    tipo_certificado: Mapped[str] = mapped_column(String(50), nullable=False, default="HABILITACION")
    fecha_emision: Mapped[datetime] = mapped_column(nullable=False)
    fecha_vencimiento: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    actividades_economicas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVO")
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador: Mapped["ROCCAOperador"] = relationship(back_populates="certificados")

    def __repr__(self) -> str:
        return f"<Certificado {self.numero_certificado} operador={self.operador_id} estado={self.estado}>"


class DomicilioOperativo(Base):
    """Modelo ORM de domicilio operativo de un operador."""

    __tablename__ = "domicilios_operativos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[str] = mapped_column(
        String(20), default=TipoDomicilio.OPERATIVO.value, nullable=False
    )
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    localidad: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    provincia: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    codigo_postal: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    es_principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    operador: Mapped["ROCCAOperador"] = relationship(back_populates="domicilios_operativos")

    def __repr__(self) -> str:
        return f"<DomicilioOperativo id={self.id} operador_id={self.operador_id}>"


class RequisitoInscripcion(Base):
    """Modelo ORM de requisito de inscripción cumplido por un operador.

    Cada requisito puede ser general (común a todas las categorías) o
    específico (vinculado a una categoría de operador).
    """

    __tablename__ = "requisitos_inscripcion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_id: Mapped[int] = mapped_column(
        ForeignKey("operadores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    codigo: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    es_general: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cumplido: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_cumplimiento: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador: Mapped["ROCCAOperador"] = relationship(back_populates="requisitos")

    def __repr__(self) -> str:
        return f"<RequisitoInscripcion id={self.id} operador_id={self.operador_id} codigo={self.codigo} cumplido={self.cumplido}>"


class ROCCAOperadorDAO:
    """DAO de operadores de la cadena cárnica."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def crear(self, cuit: str, razon_social: str, tipo: TipoOperador | str,
              persona_id: int | None = None,
              domicilio_comercial: str | None = None,
              telefono: str | None = None, email: str | None = None,
              categoria: str | None = None) -> ROCCAOperador:
        """Crea y persiste un operador nuevo (sucursal/establecimiento)."""
        with self._session_factory() as session:
            operador = ROCCAOperador(
                cuit=cuit,
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

    def obtener_por_id(self, operador_id: int) -> ROCCAOperador | None:
        """Devuelve el operador con el id dado, o ``None``."""
        with self._session_factory() as session:
            return session.get(ROCCAOperador, operador_id)

    def obtener_por_cuit(self, cuit: str) -> ROCCAOperador | None:
        """Devuelve el operador con el CUIT dado, o ``None``."""
        with self._session_factory() as session:
            return (
                session.query(ROCCAOperador)
                .filter_by(cuit=cuit)
                .first()
            )

    def listar(self, tipo: TipoOperador | str | None = None,
               estado_registral: EstadoRegistral | str | None = None,
               categoria: str | None = None) -> list[ROCCAOperador]:
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        with self._session_factory() as session:
            query = session.query(ROCCAOperador)
            if tipo is not None:
                query = query.filter_by(tipo=tipo if isinstance(tipo, str) else tipo.value)
            if estado_registral is not None:
                query = query.filter_by(
                    estado_registral=estado_registral if isinstance(estado_registral, str) else estado_registral.value
                )
            if categoria is not None:
                query = query.filter_by(categoria=categoria)
            return list(query.all())

    def actualizar_estado(self, operador_id: int, estado: EstadoRegistral) -> ROCCAOperador | None:
        """Actualiza el estado registral de un operador."""
        with self._session_factory() as session:
            operador = session.get(ROCCAOperador, operador_id)
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

    def listar_requisitos(self, operador_id: int) -> list[RequisitoInscripcion]:
        """Lista los requisitos de inscripción de un operador."""
        with self._session_factory() as session:
            return (
                session.query(RequisitoInscripcion)
                .filter_by(operador_id=operador_id)
                .all()
            )
