"""Servicio de negocio del Módulo II — Trazabilidad Comercial (ROCCA)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from .dao import RegistroTrazabilidad, RegistroTrazabilidadDAO
from .enums import Especie, EstadoTrazabilidad, TipoDestino, TipoIngreso
from .schema import RegistroTrazabilidadIn, RegistroTrazabilidadOut


class TrazabilidadComercialError(Exception):
    """Error de negocio del Módulo de Trazabilidad Comercial."""


class TrazabilidadComercialService:
    """Caso de uso: registro de trazabilidad comercial de carnes."""

    def __init__(self, dao: RegistroTrazabilidadDAO) -> None:
        self._dao = dao

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------

    def registrar(self, datos: RegistroTrazabilidadIn) -> RegistroTrazabilidadOut:
        """Registra un nuevo movimiento de trazabilidad comercial."""
        # Validar duplicados por DTE o remito
        if datos.numero_dte:
            existente = self._dao.obtener_por_dte(datos.numero_dte)
            if existente is not None:
                raise TrazabilidadComercialError(
                    f"Ya existe un registro con DTE {datos.numero_dte} (id={existente.id})"
                )
        if datos.numero_remito:
            existente = self._dao.obtener_por_remito(datos.numero_remito)
            if existente is not None:
                raise TrazabilidadComercialError(
                    f"Ya existe un registro con remito {datos.numero_remito} (id={existente.id})"
                )

        registro = RegistroTrazabilidad(
            tipo_ingreso=datos.tipo_ingreso.value,
            origen_provincia=datos.origen_provincia,
            origen_localidad=datos.origen_localidad,
            establecimiento_faena=datos.establecimiento_faena,
            numero_dte=datos.numero_dte,
            numero_remito=datos.numero_remito,
            cantidad_kg=datos.cantidad_kg,
            especie=datos.especie.value,
            destino_tipo=datos.destino_tipo.value if datos.destino_tipo else None,
            destino_cuit=datos.destino_cuit,
            destino_razon_social=datos.destino_razon_social,
            estado=EstadoTrazabilidad.REGISTRADO.value,
            fecha_ingreso=datos.fecha_ingreso or date.today(),
            observaciones=datos.observaciones,
        )

        guardado = self._dao.guardar(registro)
        return RegistroTrazabilidadOut.from_orm(guardado)

    def obtener(self, registro_id: int) -> RegistroTrazabilidadOut:
        registro = self._dao.obtener_por_id(registro_id)
        if registro is None:
            raise TrazabilidadComercialError(
                f"Registro de trazabilidad no encontrado: id={registro_id}"
            )
        return RegistroTrazabilidadOut.from_orm(registro)

    def listar(
        self,
        tipo_ingreso: Optional[TipoIngreso] = None,
        especie: Optional[Especie] = None,
        estado: Optional[EstadoTrazabilidad] = None,
        origen_provincia: Optional[str] = None,
        destino_cuit: Optional[str] = None,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[RegistroTrazabilidadOut]:
        registros = self._dao.listar(
            tipo_ingreso=tipo_ingreso.value if tipo_ingreso else None,
            especie=especie.value if especie else None,
            estado=estado.value if estado else None,
            origen_provincia=origen_provincia,
            destino_cuit=destino_cuit,
            desde=desde,
            hasta=hasta,
            limite=limite,
            offset=offset,
        )
        return [RegistroTrazabilidadOut.from_orm(r) for r in registros]

    def validar(self, registro_id: int) -> RegistroTrazabilidadOut:
        """Marca el registro como VALIDADO (confirmación de recepción)."""
        registro = self._dao.obtener_por_id(registro_id)
        if registro is None:
            raise TrazabilidadComercialError(
                f"Registro de trazabilidad no encontrado: id={registro_id}"
            )
        if registro.estado != EstadoTrazabilidad.REGISTRADO.value:
            raise TrazabilidadComercialError(
                f"El registro {registro_id} no está en estado REGISTRADO "
                f"(estado actual: {registro.estado})"
            )
        registro.estado = EstadoTrazabilidad.VALIDADO.value
        actualizado = self._dao.actualizar(registro)
        return RegistroTrazabilidadOut.from_orm(actualizado)

    def rechazar(self, registro_id: int, motivo: Optional[str] = None) -> RegistroTrazabilidadOut:
        """Marca el registro como RECHAZADO."""
        registro = self._dao.obtener_por_id(registro_id)
        if registro is None:
            raise TrazabilidadComercialError(
                f"Registro de trazabilidad no encontrado: id={registro_id}"
            )
        if registro.estado != EstadoTrazabilidad.REGISTRADO.value:
            raise TrazabilidadComercialError(
                f"El registro {registro_id} no está en estado REGISTRADO "
                f"(estado actual: {registro.estado})"
            )
        registro.estado = EstadoTrazabilidad.RECHAZADO.value
        if motivo:
            registro.observaciones = (
                f"{registro.observaciones}\nRechazo: {motivo}".strip()
                if registro.observaciones
                else f"Rechazo: {motivo}"
            )
        actualizado = self._dao.actualizar(registro)
        return RegistroTrazabilidadOut.from_orm(actualizado)

    def eliminar(self, registro_id: int) -> None:
        """Elimina un registro de trazabilidad."""
        eliminado = self._dao.eliminar(registro_id)
        if not eliminado:
            raise TrazabilidadComercialError(
                f"Registro de trazabilidad no encontrado: id={registro_id}"
            )
