"""Modelo ORM de Archivo.

Un archivo es un documento almacenado en storage (InsForge S3).
Puede ser referenciado por múltiples ``documento_requisito``.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.db import Base


class Archivo(Base):
    """Modelo ORM de archivo (documento en storage)."""

    __tablename__ = "archivos"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    documentos: Mapped[list["DocumentoRequisito"]] = relationship(
        back_populates="archivo"
    )

    def __repr__(self) -> str:
        return f"<Archivo id={self.id} nombre={self.nombre}>"


class ArchivoDAO:
    """DAO de archivos."""

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def obtener_por_id(self, archivo_id: int) -> Optional[Archivo]:
        """Obtiene un archivo por su id."""
        with self._session_factory() as session:
            return session.get(Archivo, archivo_id)

    def crear(self, nombre: str, storage_path: str,
              size_bytes: int, mime_type: str) -> Archivo:
        """Crea y persiste un archivo nuevo."""
        with self._session_factory() as session:
            arch = Archivo(
                nombre=nombre,
                storage_path=storage_path,
                size_bytes=size_bytes,
                mime_type=mime_type,
            )
            session.add(arch)
            session.commit()
            session.refresh(arch)
            return arch

    def eliminar(self, archivo_id: int) -> bool:
        """Elimina un archivo."""
        with self._session_factory() as session:
            arch = session.get(Archivo, archivo_id)
            if arch is None:
                return False
            session.delete(arch)
            session.commit()
            return True
