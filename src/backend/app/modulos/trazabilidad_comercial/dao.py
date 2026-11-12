# """DAO y modelo ORM del Módulo II — Trazabilidad Comercial."""

# from __future__ import annotations

# from datetime import datetime, timezone
# from decimal import Decimal
# from typing import Optional

# from sqlalchemy import DateTime, Numeric, String
# from sqlalchemy.orm import Mapped, mapped_column

# from configs.db import Base


# class RegistroTrazabilidad(Base):
#     """Modelo ORM de registro de trazabilidad comercial."""

#     __tablename__ = "registros_trazabilidad"
#     __table_args__ = {"extend_existing": True}

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     tipo_ingreso: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
#     especie: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
#     cantidad: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
#     peso_kg: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
#     origen_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
#     destino_cuit: Mapped[str] = mapped_column(String(13), nullable=False, index=True)
#     tipo_destino: Mapped[str] = mapped_column(String(30), nullable=False)
#     estado: Mapped[str] = mapped_column(
#         String(20), default="PENDIENTE", nullable=False, index=True
#     )
#     fecha_ingreso: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     numero_remito: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
#     numero_dte: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
#     observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
#     creado_en: Mapped[datetime] = mapped_column(
#         default=lambda: datetime.now(timezone.utc), nullable=False
#     )

#     def __repr__(self) -> str:
#         return (
#             f"<RegistroTrazabilidad id={self.id} origen={self.origen_cuit} "
#             f"destino={self.destino_cuit} estado={self.estado}>"
#         )


# class RegistroTrazabilidadDAO:
#     """DAO de registros de trazabilidad comercial."""

#     def __init__(self, session_factory) -> None:
#         self._session_factory = session_factory

#     def crear(self, registro: RegistroTrazabilidad) -> RegistroTrazabilidad:
#         """Crea y persiste un registro de trazabilidad."""
#         with self._session_factory() as session:
#             session.add(registro)
#             session.commit()
#             session.refresh(registro)
#             return registro

#     def obtener_por_id(self, registro_id: int) -> RegistroTrazabilidad | None:
#         """Devuelve el registro con el id dado, o ``None``."""
#         with self._session_factory() as session:
#             return session.get(RegistroTrazabilidad, registro_id)

#     def listar(self, estado: str | None = None, especie: str | None = None,
#                origen_cuit: str | None = None, destino_cuit: str | None = None) -> list[RegistroTrazabilidad]:
#         """Lista registros, opcionalmente filtrados."""
#         with self._session_factory() as session:
#             query = session.query(RegistroTrazabilidad)
#             if estado is not None:
#                 query = query.filter_by(estado=estado)
#             if especie is not None:
#                 query = query.filter_by(especie=especie)
#             if origen_cuit is not None:
#                 query = query.filter_by(origen_cuit=origen_cuit)
#             if destino_cuit is not None:
#                 query = query.filter_by(destino_cuit=destino_cuit)
#             return list(query.all())

#     def actualizar_estado(self, registro_id: int, estado: str) -> RegistroTrazabilidad | None:
#         """Actualiza el estado de un registro."""
#         with self._session_factory() as session:
#             registro = session.get(RegistroTrazabilidad, registro_id)
#             if registro is None:
#                 return None
#             registro.estado = estado
#             session.commit()
#             session.refresh(registro)
#             return registro
