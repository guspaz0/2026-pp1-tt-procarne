"""Modelo ORM de DocumentoRequisito.

Vincula un ``operador_requisito`` con un ``archivo`` (documento subido),
registrando quién lo cargó y cuándo.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class DocumentoRequisito(Base):
    """Modelo ORM de documento_requisito."""

    __tablename__ = "documento_requisito"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operador_requisito_id: Mapped[int] = mapped_column(
        ForeignKey("operador_requisitos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    archivo_id: Mapped[int] = mapped_column(
        ForeignKey("archivos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    persona_carga_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("personas.id", ondelete="SET NULL"), nullable=True
    )
    fecha_carga: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )

    operador_requisito: Mapped["OperadorRequisito"] = relationship(
        back_populates="documentos"
    )
    archivo: Mapped["Archivo"] = relationship(back_populates="documentos")
    persona_carga: Mapped[Optional["Persona"]] = relationship()

    def __repr__(self) -> str:
        return f"<DocumentoRequisito id={self.id} op_req={self.operador_requisito_id} archivo={self.archivo_id}>"


class DocumentoRequisitoDAO:
    """DAO de documento_requisito."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, id: int) -> Optional[DocumentoRequisito]:
        """Obtiene un documento_requisito por su id."""
        with self._session_factory() as session:
            return session.get(DocumentoRequisito, id)

    def listar_por_operador_requisito(self, operador_requisito_id: int) -> list[DocumentoRequisito]:
        """Lista los documentos de un operador_requisito."""
        with self._session_factory() as session:
            return (
                session.query(DocumentoRequisito)
                .filter_by(operador_requisito_id=operador_requisito_id)
                .all()
            )

    def crear(self, operador_requisito_id: int, archivo_id: int,
              persona_carga_id: int | None = None) -> DocumentoRequisito:
        """Crea y persiste un documento_requisito nuevo."""
        with self._session_factory() as session:
            doc = DocumentoRequisito(
                operador_requisito_id=operador_requisito_id,
                archivo_id=archivo_id,
                persona_carga_id=persona_carga_id,
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc

    def eliminar(self, id: int) -> bool:
        """Elimina un documento_requisito."""
        with self._session_factory() as session:
            doc = session.get(DocumentoRequisito, id)
            if doc is None:
                return False
            session.delete(doc)
            session.commit()
            return True
