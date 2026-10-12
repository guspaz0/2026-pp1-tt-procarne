"""Servicio de negocio del Módulo III — Fiscalización (ROCCA)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from .dao import (
    Acta,
    Decomiso,
    FiscalizacionDAO,
    Infraccion,
    Inspeccion,
    Reincidencia,
    Sancion,
)
from .enums import (
    EstadoActa,
    EstadoSancion,
    GravedadInfraccion,
    ResultadoInspeccion,
    TipoActa,
    TipoInfraccion,
    TipoSancion,
)
from .schema import (
    ActaIn,
    DecomisoIn,
    InspeccionIn,
    InspeccionOut,
    ReincidenciaIn,
    ReincidenciaOut,
)


class FiscalizacionError(Exception):
    """Error de negocio del Módulo de Fiscalización."""


class FiscalizacionService:
    """Caso de uso: gestión de inspecciones, actas, decomisos,
    infracciones, sanciones y reincidencias."""

    def __init__(self, dao: FiscalizacionDAO) -> None:
        self._dao = dao

    # ------------------------------------------------------------------
    # Inspecciones
    # ------------------------------------------------------------------

    def registrar_inspeccion(self, datos: InspeccionIn) -> InspeccionOut:
        """Registra una nueva inspección con sus actas, decomisos e infracciones."""
        inspeccion = Inspeccion(
            inspector=datos.inspector,
            operador_cuit=datos.operador_cuit,
            tipo=datos.tipo.value,
            resultado=datos.resultado.value,
            latitud=datos.latitud,
            longitud=datos.longitud,
            observaciones=datos.observaciones,
        )

        guardada = self._dao.guardar_inspeccion(inspeccion)

        # Actas
        for acta_in in datos.actas:
            acta = Acta(
                inspeccion_id=guardada.id,
                tipo=acta_in.tipo.value,
                numero=acta_in.numero,
                descripcion=acta_in.descripcion,
                estado=acta_in.estado.value,
                fecha_firma=datetime.utcnow() if acta_in.estado is EstadoActa.FIRMADA else None,
            )
            self._dao.guardar_acta(acta)

        # Decomisos
        for decomiso_in in datos.decomisos:
            decomiso = Decomiso(
                inspeccion_id=guardada.id,
                producto=decomiso_in.producto,
                cantidad=decomiso_in.cantidad,
                unidad=decomiso_in.unidad,
                motivo=decomiso_in.motivo,
                destino=decomiso_in.destino,
                estado=decomiso_in.estado.value,
            )
            self._dao.guardar_decomiso(decomiso)

        # Infracciones (con sanciones anidadas)
        for infraccion_in in datos.infracciones:
            infraccion = Infraccion(
                inspeccion_id=guardada.id,
                operador_cuit=datos.operador_cuit,
                tipo=infraccion_in.tipo.value,
                gravedad=infraccion_in.gravedad.value,
                descripcion=infraccion_in.descripcion,
            )
            guardada_inf = self._dao.guardar_infraccion(infraccion)

            for sancion_in in infraccion_in.sanciones:
                sancion = Sancion(
                    infraccion_id=guardada_inf.id,
                    operador_cuit=datos.operador_cuit,
                    tipo=sancion_in.tipo.value,
                    monto=sancion_in.monto,
                    descripcion=sancion_in.descripcion,
                    estado=sancion_in.estado.value,
                )
                self._dao.guardar_sancion(sancion)

            # Registrar reincidencia si la gravedad es GRAVE o MUY_GRAVE
            if datos.operador_cuit and infraccion_in.gravedad in (
                GravedadInfraccion.GRAVE,
                GravedadInfraccion.MUY_GRAVE,
            ):
                self._dao.incrementar_reincidencia(
                    datos.operador_cuit,
                    observaciones=f"Infracción {infraccion_in.tipo.value} "
                    f"({infraccion_in.gravedad.value}) el {date.today().isoformat()}",
                )

        return InspeccionOut.from_orm(self._dao.obtener_inspeccion(guardada.id))

    def obtener_inspeccion(self, inspeccion_id: int) -> InspeccionOut:
        inspeccion = self._dao.obtener_inspeccion(inspeccion_id)
        if inspeccion is None:
            raise FiscalizacionError(f"Inspección no encontrada: id={inspeccion_id}")
        return InspeccionOut.from_orm(inspeccion)

    def listar_inspecciones(
        self,
        operador_cuit: Optional[str] = None,
        resultado: Optional[ResultadoInspeccion] = None,
        desde: Optional[date] = None,
        hasta: Optional[date] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[InspeccionOut]:
        inspecciones = self._dao.listar_inspecciones(
            operador_cuit=operador_cuit,
            resultado=resultado.value if resultado else None,
            desde=desde,
            hasta=hasta,
            limite=limite,
            offset=offset,
        )
        return [InspeccionOut.from_orm(i) for i in inspecciones]

    def marcar_enviada(self, inspeccion_id: int) -> InspeccionOut:
        """Marca la inspección como enviada (sincronizada)."""
        inspeccion = self._dao.obtener_inspeccion(inspeccion_id)
        if inspeccion is None:
            raise FiscalizacionError(f"Inspección no encontrada: id={inspeccion_id}")
        inspeccion.enviada = True
        actualizada = self._dao.actualizar_inspeccion(inspeccion)
        return InspeccionOut.from_orm(actualizada)

    def eliminar_inspeccion(self, inspeccion_id: int) -> None:
        eliminada = self._dao.eliminar_inspeccion(inspeccion_id)
        if not eliminada:
            raise FiscalizacionError(f"Inspección no encontrada: id={inspeccion_id}")

    # ------------------------------------------------------------------
    # Actas
    # ------------------------------------------------------------------

    def firmar_acta(self, acta_id: int) -> None:
        """Firma un acta."""
        from .dao import Acta as ActaORM

        with self._dao._session_factory() as session:
            acta = session.get(ActaORM, acta_id)
            if acta is None:
                raise FiscalizacionError(f"Acta no encontrada: id={acta_id}")
            if acta.estado != EstadoActa.BORRADOR.value:
                raise FiscalizacionError(
                    f"El acta {acta_id} no está en estado BORRADOR (estado: {acta.estado})"
                )
            acta.estado = EstadoActa.FIRMADA.value
            acta.fecha_firma = datetime.utcnow()
            session.commit()

    # ------------------------------------------------------------------
    # Infracciones
    # ------------------------------------------------------------------

    def listar_infracciones(
        self,
        operador_cuit: Optional[str] = None,
        gravedad: Optional[GravedadInfraccion] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list:
        infracciones = self._dao.listar_infracciones(
            operador_cuit=operador_cuit,
            gravedad=gravedad.value if gravedad else None,
            limite=limite,
            offset=offset,
        )
        from .schema import InfraccionOut

        return [InfraccionOut.from_orm(i) for i in infracciones]

    # ------------------------------------------------------------------
    # Sanciones
    # ------------------------------------------------------------------

    def actualizar_estado_sancion(self, sancion_id: int, estado: EstadoSancion) -> None:
        """Actualiza el estado de una sanción."""
        with self._dao._session_factory() as session:
            from .dao import Sancion as SancionORM

            sancion = session.get(SancionORM, sancion_id)
            if sancion is None:
                raise FiscalizacionError(f"Sanción no encontrada: id={sancion_id}")
            sancion.estado = estado.value
            if estado is EstadoSancion.CUMPLIDA:
                sancion.fecha_cumplimiento = date.today()
            session.commit()

    # ------------------------------------------------------------------
    # Reincidencias
    # ------------------------------------------------------------------

    def registrar_reincidencia(self, datos: ReincidenciaIn) -> ReincidenciaOut:
        """Registra (o incrementa) una reincidencia para un operador."""
        rec = self._dao.incrementar_reincidencia(
            datos.operador_cuit, datos.observaciones
        )
        return ReincidenciaOut.from_orm(rec)

    def obtener_reincidencia(self, operador_cuit: str) -> ReincidenciaOut:
        rec = self._dao.obtener_reincidencia(operador_cuit)
        if rec is None:
            raise FiscalizacionError(
                f"No hay reincidencias registradas para CUIT {operador_cuit}"
            )
        return ReincidenciaOut.from_orm(rec)

    def listar_reincidencias(
        self, limite: int = 100, offset: int = 0
    ) -> list[ReincidenciaOut]:
        recs = self._dao.listar_reincidencias(limite=limite, offset=offset)
        return [ReincidenciaOut.from_orm(r) for r in recs]
