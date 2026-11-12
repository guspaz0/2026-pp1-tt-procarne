"""DAO de Operador (sucursal/establecimiento) — Módulo I: Registro de Operadores.

Cada operador pertenece a una persona (física o jurídica) mediante
``persona_id``. La persona es la entidad legal; el operador es la
sucursal/establecimiento.

El CUIT **no** se guarda en ``operadores``: identifica a la persona
titular (``personas.identificador``). Por eso no existe ``operadores.cuit``.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base
from modulos.registro_operadores.enums import EstadoRegistral, TipoOperador


class Operador(Base):
    """Modelo ORM de Operador (sucursal/establecimiento)."""

    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id", ondelete="CASCADE"), nullable=False
    )
    razon_social: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domicilio_comercial: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    categoria: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estado_registral: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDIENTE")
    alta_fecha: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    baja_fecha: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    persona: Mapped["Persona"] = relationship(back_populates="operadores")
    requisitos: Mapped[list["RequisitoInscripcion"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    adjuntos: Mapped[list["AdjuntoOperador"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    actividades: Mapped[list["OperadorActividad"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    certificados: Mapped[list["Certificado"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    domicilios_operativos: Mapped[list["DomicilioOperativo"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    habilitaciones: Mapped[list["Habilitacion"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )
    inscripciones: Mapped[list["Inscripcion"]] = relationship(
        back_populates="operador", cascade="all, delete-orphan"
    )


class OperadorDAO:
    """DAO de Operador sobre PostgreSQL (SQLAlchemy 2.0)."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    # ------------------------------------------------------------------
    # Lecturas
    # ------------------------------------------------------------------

    def obtener_por_id(self, operador_id: int) -> Optional[Operador]:
        """Busca un operador por su id."""
        with self._session_factory() as session:
            return session.get(Operador, operador_id)

    def obtener_por_cuit(self, cuit: str) -> Optional[Operador]:
        """Busca un operador por el CUIT de su persona titular.

        El CUIT vive en ``personas.identificador``: se busca la persona
        y se devuelve el primer operador vinculado a ella.
        """
        from core.persona.dao import Persona

        with self._session_factory() as session:
            persona = (
                session.query(Persona)
                .filter(Persona.tipo_documento == "CUIT", Persona.identificador == cuit)
                .first()
            )
            if persona is None:
                return None
            return (
                session.query(Operador)
                .filter(Operador.persona_id == persona.id)
                .first()
            )

    def listar(self, tipo: Optional[str] = None,
               estado_registral: Optional[str] = None,
               categoria: Optional[str] = None) -> list[Operador]:
        """Lista operadores, opcionalmente filtrados por tipo, estado y categoría."""
        with self._session_factory() as session:
            stmt = select(Operador)
            if tipo is not None:
                stmt = stmt.where(Operador.tipo == tipo)
            if estado_registral is not None:
                stmt = stmt.where(Operador.estado_registral == estado_registral)
            if categoria is not None:
                stmt = stmt.where(Operador.categoria == categoria)
            return list(session.scalars(stmt).all())

    # ------------------------------------------------------------------
    # Escrituras
    # ------------------------------------------------------------------

    def crear(self, razon_social: str, tipo: TipoOperador | str,
              persona_id: int,
              domicilio_comercial: Optional[str] = None,
              telefono: Optional[str] = None,
              email: Optional[str] = None,
              categoria: Optional[str] = None) -> Operador:
        """Crea y persiste un operador."""
        with self._session_factory() as session:
            op = Operador(
                persona_id=persona_id,
                razon_social=razon_social,
                domicilio_comercial=domicilio_comercial,
                telefono=telefono,
                email=email,
                tipo=tipo,
                categoria=categoria,
                estado_registral=EstadoRegistral.PENDIENTE.value,
                alta_fecha=datetime.now(timezone.utc),
            )
            session.add(op)
            session.commit()
            session.refresh(op)
            return op

    def actualizar(self, operador_id: int, **kwargs) -> Optional[Operador]:
        """Actualiza campos del operador."""
        with self._session_factory() as session:
            op = session.get(Operador, operador_id)
            if op is None:
                return None
            for k, v in kwargs.items():
                if hasattr(op, k):
                    setattr(op, k, v)
            session.commit()
            session.refresh(op)
            return op

    def actualizar_estado(self, operador_id: int, estado: str) -> Optional[Operador]:
        """Cambia el estado registral del operador."""
        return self.actualizar(operador_id, estado_registral=estado)

    def eliminar(self, operador_id: int) -> bool:
        """Elimina un operador."""
        with self._session_factory() as session:
            op = session.get(Operador, operador_id)
            if op is None:
                return False
            session.delete(op)
            session.commit()
            return True

    # ------------------------------------------------------------------
    # Actividades económicas (N:M vía operador_actividades)
    # ------------------------------------------------------------------

    def asignar_actividades(self, operador_id: int, actividad_ids: list[int]) -> None:
        """Reemplaza el conjunto de actividades del operador.

        Guarda en ``operador_actividades`` las actividades del catálogo
        (``actividades_economicas``) que realiza el operador.
        """
        from modulos.registro_operadores.asociaciones import OperadorActividad

        with self._session_factory() as session:
            # Limpia las existentes y vuelve a insertar (idempotente)
            session.query(OperadorActividad).filter_by(operador_id=operador_id).delete()
            for aid in (actividad_ids or []):
                session.add(OperadorActividad(operador_id=operador_id, actividad_id=aid))
            session.commit()

    def listar_actividad_ids(self, operador_id: int) -> list[int]:
        """Devuelve los ids de actividades del catálogo del operador."""
        from modulos.registro_operadores.asociaciones import OperadorActividad

        with self._session_factory() as session:
            rows = (
                session.query(OperadorActividad.actividad_id)
                .filter_by(operador_id=operador_id)
                .order_by(OperadorActividad.actividad_id)
                .all()
            )
            return [r[0] for r in rows]
