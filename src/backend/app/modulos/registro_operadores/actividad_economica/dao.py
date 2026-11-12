"""DAO y modelos ORM del catálogo de actividades económicas (DGR Santiago).

- ``GrupoActividad`` — grupo de actividad económica (letra: A, B, C, ...).
- ``SubgrupoActividad`` — subgrupo de actividad económica.
- ``SubSubgrupoActividad`` — sub-subgrupo (3.er dígito) de actividad económica.
- ``ActividadEconomica`` — actividad económica concreta.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship, joinedload, foreign
from sqlalchemy.ext.hybrid import hybrid_property

from configs.db import Base


class GrupoActividad(Base):
    """Modelo ORM de grupo de actividad económica (letra: A, B, C, ...).

    El ``codigo`` (letra) es la clave primaria: identifica al grupo de forma
    natural y estable.
    """

    __tablename__ = "grupos_actividad"
    __table_args__ = {"extend_existing": True}

    codigo: Mapped[str] = mapped_column(String(1), primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)

    # Jerarquía: un grupo tiene muchos subgrupos (subgrupos_actividad.grupo_id).
    subgrupos: Mapped[list["SubgrupoActividad"]] = relationship(back_populates="grupo")

    def __repr__(self) -> str:
        return f"<GrupoActividad {self.codigo} {self.descripcion[:40]}>"


class SubgrupoActividad(Base):
    """Modelo ORM de subgrupo de actividad económica.

    La clave primaria es compuesta ``(grupo_id, codigo)``: el ``codigo`` del
    subgrupo (p. ej. ``11``) solo es único dentro de su grupo, y ``grupo_id``
    referencia el ``codigo`` del grupo (letra).
    """

    __tablename__ = "subgrupos_actividad"
    __table_args__ = {"extend_existing": True}

    # FK al grupo (su codigo/letra) — parte de la PK compuesta.
    grupo_id: Mapped[str] = mapped_column(
        ForeignKey("grupos_actividad.codigo"), primary_key=True
    )
    codigo: Mapped[str] = mapped_column(String(10), primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)

    grupo: Mapped["GrupoActividad"] = relationship(back_populates="subgrupos")
    # Jerarquía: un subgrupo tiene muchos sub-subgrupos. No hay FK directa a
    # ``subgrupos_actividad`` (el sub-subgrupo referencia ``grupo_id`` y
    # ``subgrupo_codigo`` como columnas), por lo que se define el join explícito.
    subsubgrupos: Mapped[list["SubSubgrupoActividad"]] = relationship(
        primaryjoin="and_("
        "SubgrupoActividad.grupo_id == foreign(SubSubgrupoActividad.grupo_id), "
        "SubgrupoActividad.codigo == foreign(SubSubgrupoActividad.subgrupo_codigo))",
        back_populates="subgrupo",
    )

    def __repr__(self) -> str:
        return f"<SubgrupoActividad {self.grupo_id}-{self.codigo} {self.descripcion[:40]}>"


class SubSubgrupoActividad(Base):
    """Modelo ORM de sub-subgrupo de actividad económica (3.er dígito).

    La clave primaria es compuesta ``(grupo_id, subgrupo_codigo, codigo)``:
    el ``codigo`` (3 dígitos, p. ej. ``111``) identifica al sub-subgrupo y solo
    es único dentro de su subgrupo. ``grupo_id`` referencia el ``codigo`` del
    grupo y ``subgrupo_codigo`` el ``codigo`` del subgrupo.
    """

    __tablename__ = "subsubgrupos_actividad"
    __table_args__ = {"extend_existing": True}

    # FK al grupo (su codigo/letra) — parte de la PK compuesta.
    grupo_id: Mapped[str] = mapped_column(
        ForeignKey("grupos_actividad.codigo"), primary_key=True
    )
    # Código del subgrupo al que pertenece (2 dígitos) — parte de la PK compuesta.
    subgrupo_codigo: Mapped[str] = mapped_column(String(10), primary_key=True)
    # Código del sub-subgrupo (3 dígitos, p. ej. ``111``) — parte de la PK compuesta.
    codigo: Mapped[str] = mapped_column(String(10), primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)

    grupo: Mapped["GrupoActividad"] = relationship(overlaps="subsubgrupos")
    subgrupo: Mapped["SubgrupoActividad"] = relationship(
        primaryjoin="and_("
        "foreign(SubSubgrupoActividad.grupo_id) == SubgrupoActividad.grupo_id, "
        "foreign(SubSubgrupoActividad.subgrupo_codigo) == SubgrupoActividad.codigo)",
        back_populates="subsubgrupos",
        overlaps="grupo",
    )

    def __repr__(self) -> str:
        return f"<SubSubgrupoActividad {self.grupo_id}-{self.subgrupo_codigo}-{self.codigo} {self.descripcion[:40]}>"


class ActividadEconomica(Base):
    """Modelo ORM de actividad económica (DGR Santiago).

    Jerarquía (el largo del código indica el nivel, ver tabla original CUASE):

        - grupo            → letra  (``A``)
        - subgrupo         → 2 dígitos (``11``)
        - grupo de actividad → 3 dígitos (``111``)
        - actividad        → 5/7 dígitos (``11110``, ``101000``)

    La columna ``codigo`` guarda el código de la actividad (hoja). El código
    completo se conforma en la capa de presentación (DTO) a partir de la
    jerarquía; no se denormaliza en la tabla.
    """

    __tablename__ = "actividades_economicas"
    __table_args__ = (
        UniqueConstraint("subgrupo_codigo", "codigo", name="uq_actividad_subgrupo_codigo"),
        # Índice compuesto para búsquedas por la jerarquía: código + grupo +
        # subgrupo. Permite resolver una actividad por su código dentro de un
        # grupo/subgrupo concreto sin escanear la tabla completa.
        Index(
            "ix_actividades_economicas_codigo_grupo_subgrupo",
            "codigo",
            "grupo_id",
            "subgrupo_codigo",
        ),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    # FK al grupo: ahora referencia el ``codigo`` (letra) del grupo, que es su PK.
    grupo_id: Mapped[str] = mapped_column(
        ForeignKey("grupos_actividad.codigo"), nullable=False, index=True
    )
    # Código del subgrupo (único dentro del grupo). No es una FK a una PK
    # compuesta; se resuelve junto con ``grupo_id`` vía la relación ``subgrupo``.
    subgrupo_codigo: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    # Código del sub-subgrupo (3 dígitos, p. ej. ``111``). Se resuelve junto con
    # ``grupo_id`` y ``subgrupo_codigo`` vía la relación ``subsubgrupo``.
    subsubgrupo_codigo: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)

    grupo: Mapped["GrupoActividad"] = relationship()
    subgrupo: Mapped[Optional["SubgrupoActividad"]] = relationship(
        primaryjoin="and_("
        "foreign(ActividadEconomica.grupo_id) == SubgrupoActividad.grupo_id, "
        "foreign(ActividadEconomica.subgrupo_codigo) == SubgrupoActividad.codigo)",
        overlaps="grupo",
    )
    subsubgrupo: Mapped[Optional["SubSubgrupoActividad"]] = relationship(
        primaryjoin="and_("
        "foreign(ActividadEconomica.grupo_id) == SubSubgrupoActividad.grupo_id, "
        "foreign(ActividadEconomica.subgrupo_codigo) == SubSubgrupoActividad.subgrupo_codigo, "
        "foreign(ActividadEconomica.subsubgrupo_codigo) == SubSubgrupoActividad.codigo)",
        overlaps="grupo,subgrupo",
    )
    operadores: Mapped[list["OperadorActividad"]] = relationship(back_populates="actividad")
    certificados: Mapped[list["CertificadoActividad"]] = relationship(back_populates="actividad")

    @hybrid_property
    def codigo_grupo(self) -> Optional[str]:
        """Código (letra) del grupo al que pertenece la actividad.

        Campo calculado vía la relación ``grupo`` (eager-load en el DAO).
        """
        return self.grupo.codigo if self.grupo else None

    @hybrid_property
    def codigo_subgrupo(self) -> Optional[str]:
        """Código del subgrupo (ej. ``11``).

        Campo calculado vía la relación ``subgrupo`` (eager-load en el DAO).
        """
        if not self.subgrupo:
            return None
        return self.subgrupo.codigo

    @hybrid_property
    def codigo_subsubgrupo(self) -> Optional[str]:
        """Código del sub-subgrupo (ej. ``111``).

        Campo calculado vía la relación ``subsubgrupo`` (eager-load en el DAO).
        """
        if not self.subsubgrupo:
            return None
        return self.subsubgrupo.codigo

    @hybrid_property
    def codigo_completo(self) -> str:
        """Código completo de la actividad, construido por concatenación de la
        jerarquía, tolerante a ``None``.

        Campo calculado (no almacenado). El código DGR de la actividad (hoja)
        ya incrusta los prefijos de subgrupo y sub-subgrupo (por largo), por lo
        que se construye como::

            grupo + subgrupo + (subsubgrupo - prefijo subgrupo)
                    + (actividad - prefijo subsubgrupo)

        Cada nivel se coalesce a cadena vacía cuando es ``None``/``null`` (no
        todas las actividades tienen subgrupo ni sub-subgrupo). El resultado es
        equivalente a ``grupo.codigo + actividad.codigo`` cuando la jerarquía
        está completa, pero es robusto ante niveles ausentes.
        """
        grupo = (self.grupo.codigo if self.grupo else "") or ""
        sub = (self.subgrupo.codigo if self.subgrupo else "") or ""
        subsub = (self.subsubgrupo.codigo if self.subsubgrupo else "") or ""
        codigo = self.codigo or ""

        # El código de la actividad (hoja) empieza por el prefijo del
        # sub-subgrupo (que a su vez empieza por el del subgrupo). Se extrae la
        # parte "hoja" (lo que queda tras el prefijo del sub-subgrupo) para no
        # duplicar niveles al concatenar.
        if subsub and codigo.startswith(subsub):
            hoja = codigo[len(subsub):]
        elif sub and codigo.startswith(sub):
            hoja = codigo[len(sub):]
        else:
            hoja = codigo
        # El sub-subgrupo ya incluye el prefijo del subgrupo; se añade solo su
        # parte propia (el 3.er dígito) para no duplicar el subgrupo.
        if subsub and subsub.startswith(sub):
            subsub_extra = subsub[len(sub):]
        else:
            subsub_extra = subsub
        return f"{grupo}{sub}{subsub_extra}{hoja}"

    def __repr__(self) -> str:
        return f"<ActividadEconomica {self.codigo} {self.descripcion[:40]}>"


class CatalogoActividadesDAO:
    """DAO del catálogo de actividades económicas (solo lectura)."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def listar_grupos(self) -> list[GrupoActividad]:
        """Lista los grupos de actividades económicas ordenados por código."""
        with self._session_factory() as session:
            return (
                session.query(GrupoActividad)
                .order_by(GrupoActividad.codigo)
                .all()
            )

    def listar_subgrupos(self, grupo: str | None = None) -> list[SubgrupoActividad]:
        """Lista los subgrupos, opcionalmente filtrados por grupo (código/letra)."""
        with self._session_factory() as session:
            q = session.query(SubgrupoActividad)
            if grupo:
                q = q.filter_by(grupo_id=grupo)
            return q.order_by(SubgrupoActividad.grupo_id, SubgrupoActividad.codigo).all()

    def listar_subsubgrupos(self, grupo: str | None = None,
                            subgrupo: str | None = None) -> list[SubSubgrupoActividad]:
        """Lista los sub-subgrupos, opcionalmente filtrados por grupo y/o subgrupo (código)."""
        with self._session_factory() as session:
            q = session.query(SubSubgrupoActividad)
            if grupo:
                q = q.filter_by(grupo_id=grupo)
            if subgrupo:
                q = q.filter_by(subgrupo_codigo=subgrupo)
            return (
                q.order_by(
                    SubSubgrupoActividad.grupo_id,
                    SubSubgrupoActividad.subgrupo_codigo,
                    SubSubgrupoActividad.codigo,
                )
                .all()
            )

    def listar_actividades(self, grupo: str | None = None,
                           subgrupo: str | None = None,
                           subsubgrupo: str | None = None) -> list[ActividadEconomica]:
        """Lista las actividades económicas, opcionalmente filtradas por
        grupo/subgrupo/sub-subgrupo (código).

        Se eager-loadean las relaciones ``grupo``, ``subgrupo`` y ``subsubgrupo``
        (``joinedload``) para que los campos calculados ``codigo_grupo`` /
        ``codigo_subgrupo`` / ``codigo_subsubgrupo`` puedan resolverse una vez
        que la sesión se cierra (instancias desacopladas) al construir el DTO
        Pydantic.
        """
        with self._session_factory() as session:
            q = (
                session.query(ActividadEconomica)
                .options(
                    joinedload(ActividadEconomica.grupo),
                    joinedload(ActividadEconomica.subgrupo),
                    joinedload(ActividadEconomica.subsubgrupo),
                )
            )
            if grupo:
                q = q.filter_by(grupo_id=grupo)
            if subgrupo:
                q = q.filter_by(subgrupo_codigo=subgrupo)
            if subsubgrupo:
                q = q.filter_by(subsubgrupo_codigo=subsubgrupo)
            return q.order_by(ActividadEconomica.codigo).all()

    def resolver_ids_por_codigos(self, codigos: list[str]) -> list[int]:
        """Devuelve los ids de las actividades cuyo ``codigo`` está en ``codigos``.

        Se usa para resolver las categorías del alta (por su código DGR) a
        ids del catálogo, para guardarlas en ``operador_actividades``.
        """
        if not codigos:
            return []
        with self._session_factory() as session:
            rows = (
                session.query(ActividadEconomica.id)
                .filter(ActividadEconomica.codigo.in_(codigos))
                .order_by(ActividadEconomica.id)
                .all()
            )
            return [r[0] for r in rows]
