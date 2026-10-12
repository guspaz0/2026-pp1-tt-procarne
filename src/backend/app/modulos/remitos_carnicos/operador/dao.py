"""ORM y DAO del operador de la cadena cárnica.

El Operador se refiere a una PersonaJuridica en la tabla ``personas``.
Solo almacena los campos específicos del operador (domicilio_fiscal,
categoria, situacion) y las relaciones con categorías/actividades.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Table, Column, ForeignKey, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from configs.db import Base

# Tabla intermedia operador <-> actividad (many-to-many)
operador_actividades = Table(
    "operador_actividades",
    Base.metadata,
    Column("operador_id", Integer, ForeignKey("operadores.id"), primary_key=True),
    Column("actividad_id", Integer, ForeignKey("actividades.id"), primary_key=True),
)


class Operador(Base):
    """Operador de la cadena cárnica (padrón AFIP).

    Se refiere a una PersonaJuridica en ``personas``. Los campos comunes
    (cuit, razon_social, domicilio, telefono, email) se obtienen de la persona.
    """

    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("personas.id"), unique=True, index=True, nullable=False
    )
    domicilio_fiscal: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relaciones
    persona: Mapped["Persona"] = relationship("Persona", lazy="joined")
    categorias: Mapped[list["CategoriaOperador"]] = relationship(
        "CategoriaOperador", back_populates="operador", cascade="all, delete-orphan"
    )
    actividades: Mapped[list["Actividad"]] = relationship(
        "Actividad",
        secondary=operador_actividades,
        back_populates="operadores",
    )

    @property
    def cuit(self) -> str:
        """El CUIT es el identificador de la persona jurídica."""
        return self.persona.identificador

    @property
    def razon_social(self) -> str:
        """La razón social es el nombre de la persona jurídica."""
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
        return f"<Operador persona_id={self.persona_id} cuit={self.cuit!r}>"


def _eager_options():
    """Opciones de carga eager (se resuelven en tiempo de consulta)."""
    from modulos.remitos_carnicos.operador.categoria import Actividad
    return [
        selectinload(Operador.persona),
        selectinload(Operador.categorias),
        selectinload(Operador.actividades).selectinload(Actividad.categorias_afip),
    ]


class OperadorDAO:
    """Data Access Object del operador."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_cuit(self, cuit: str) -> Optional[Operador]:
        with self._session_factory() as session:
            stmt = (
                select(Operador)
                .join(Operador.persona)
                .where(Operador.persona.has(identificador=cuit, tipo="PJ"))
                .options(*_eager_options())
            )
            return session.execute(stmt).unique().scalar_one_or_none()

    def obtener_por_id(self, operador_id: int) -> Optional[Operador]:
        with self._session_factory() as session:
            return session.get(Operador, operador_id, options=_eager_options())

    def listar(self, limite: int = 100, offset: int = 0) -> list[Operador]:
        with self._session_factory() as session:
            stmt = select(Operador).options(*_eager_options()).limit(limite).offset(offset)
            return list(session.execute(stmt).unique().scalars().all())

    def listar_por_actividad(self, actividad_id: int, limite: int = 100, offset: int = 0) -> list[Operador]:
        with self._session_factory() as session:
            stmt = (
                select(Operador)
                .join(Operador.actividades)
                .where(Operador.actividades.any(id=actividad_id))
                .options(*_eager_options())
                .limit(limite)
                .offset(offset)
            )
            return list(session.execute(stmt).unique().scalars().all())

    def guardar(self, operador: Operador, persona: Optional["Persona"] = None) -> Operador:
        with self._session_factory() as session:
            if persona is not None:
                session.add(persona)
                session.commit()
                session.refresh(persona)
                operador.persona_id = persona.id
            session.add(operador)
            session.commit()
            operador_id = operador.id
        # Recargar con relaciones eager
        return self.obtener_por_id(operador_id)

    def actualizar(self, operador: Operador) -> Operador:
        with self._session_factory() as session:
            session.merge(operador)
            session.commit()
            operador_id = operador.id
        # Recargar con relaciones eager
        return self.obtener_por_id(operador_id)
