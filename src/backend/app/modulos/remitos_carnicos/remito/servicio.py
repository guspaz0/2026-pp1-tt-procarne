"""Servicio de negocio del Remito Electrónico Cárnico."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..enums import EstadoRemito
from ..mercaderia.dao import MercaderiaDAO
from ..operador.dao import OperadorDAO
from .dao import RemitoCarnico, RenglonRemito, RemitoCarnicoDAO
from .schema import RemitoCarnicoIn, RemitoCarnicoOut, RenglonRemitoOut, ParticipanteOut
from .validacion import ValidadorRemito


class RemitoCarnicoError(Exception):
    """Error de negocio del módulo de remitos cárnicos."""


class RemitoCarnicoService:
    """Caso de uso principal: gestión de Remitos Electrónicos Cárnicos.

    Aplica **Dependency Inversion**: depende de DAOs (abstracciones de
    persistencia), no de SQLAlchemy directamente.
    """

    def __init__(
        self,
        remito_dao: RemitoCarnicoDAO,
        operador_dao: OperadorDAO,
        mercaderia_dao: MercaderiaDAO,
        validador: Optional[ValidadorRemito] = None,
    ) -> None:
        self._remito_dao = remito_dao
        self._operador_dao = operador_dao
        self._mercaderia_dao = mercaderia_dao
        self._validador = validador or ValidadorRemito()

    def crear(self, datos: RemitoCarnicoIn) -> RemitoCarnicoOut:
        """Crea un remito a partir de los datos de entrada."""
        # 1. Operadores
        titular = self._operador_dao.obtener_por_cuit(datos.titular_cuit)
        if titular is None:
            raise RemitoCarnicoError(f"Titular no encontrado: CUIT {datos.titular_cuit}")

        transportista = self._operador_dao.obtener_por_cuit(datos.transportista_cuit)
        if transportista is None:
            raise RemitoCarnicoError(f"Transportista no encontrado: CUIT {datos.transportista_cuit}")

        depositario = None
        if datos.depositario_cuit is not None:
            depositario = self._operador_dao.obtener_por_cuit(datos.depositario_cuit)
            if depositario is None:
                raise RemitoCarnicoError(f"Depositario no encontrado: CUIT {datos.depositario_cuit}")

        destinatario = None
        if datos.destinatario_cuit is not None:
            destinatario = self._operador_dao.obtener_por_cuit(datos.destinatario_cuit)
            if destinatario is None:
                raise RemitoCarnicoError(f"Destinatario no encontrado: CUIT {datos.destinatario_cuit}")

        # 2. Mercaderías
        renglones: list[RenglonRemito] = []
        for renglon_in in datos.renglones:
            mercaderia = self._mercaderia_dao.obtener_por_codigo(renglon_in.codigo_afip)
            if mercaderia is None:
                raise RemitoCarnicoError(f"Mercadería no encontrada: código AFIP {renglon_in.codigo_afip}")
            renglon = RenglonRemito(
                mercaderia_id=mercaderia.id,
                unidades=float(renglon_in.unidades),
                kilos=float(renglon_in.kilos),
                numero_tropa=renglon_in.numero_tropa,
            )
            # Asignar la relación para que la validación pueda acceder a la mercadería
            renglon.mercaderia = mercaderia
            renglones.append(renglon)

        # 3. Objeto ORM
        remito = RemitoCarnico(
            punto_emision=datos.punto_emision,
            numero_comprobante=datos.numero_comprobante,
            caso=datos.caso.value,
            tipo_movimiento=datos.tipo_movimiento.value,
            estado=EstadoRemito.EMITIDO.value,
            fecha_emision=datos.fecha_emision,
            fecha_vencimiento=datos.fecha_vencimiento,
            titular_id=titular.id,
            depositario_id=depositario.id if depositario else None,
            destinatario_id=destinatario.id if destinatario else None,
            transportista_id=transportista.id,
            chofer_apellido_nombre=datos.chofer_apellido_nombre,
            chofer_documento=datos.chofer_documento,
            dominio_vehiculo=datos.dominio_vehiculo,
            hoja=datos.hoja,
            total_hojas=datos.total_hojas,
            renglones=renglones,
        )

        # 4. Validación
        errores = self._validador.validar(remito)
        if errores:
            raise RemitoCarnicoError("Remito inválido: " + "; ".join(errores))

        # 5. Persistencia
        guardado = self._remito_dao.guardar(remito)
        return self._a_dto(guardado)

    def obtener(self, punto_emision: str, numero_comprobante: str) -> RemitoCarnicoOut:
        remito = self._remito_dao.obtener_por_codigo(punto_emision, numero_comprobante)
        if remito is None:
            raise RemitoCarnicoError(f"Remito no encontrado: {punto_emision}-{numero_comprobante}")
        return self._a_dto(remito)

    def listar(
        self,
        estado: Optional[str] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        limite: int = 100,
        offset: int = 0,
    ) -> list[RemitoCarnicoOut]:
        remitos = self._remito_dao.listar(estado=estado, desde=desde, hasta=hasta, limite=limite, offset=offset)
        return [self._a_dto(r) for r in remitos]

    def anular(self, remito_id: int) -> RemitoCarnicoOut:
        remito = self._remito_dao.obtener_por_id(remito_id)
        if remito is None:
            raise RemitoCarnicoError(f"Remito no encontrado: id {remito_id}")
        if not self._remito_dao.anular(remito_id):
            raise RemitoCarnicoError(f"El remito {remito_id} ya está anulado o no existe")
        return self._a_dto(self._remito_dao.obtener_por_id(remito_id))

    @staticmethod
    def _a_dto(remito: RemitoCarnico) -> RemitoCarnicoOut:
        return RemitoCarnicoOut(
            id=remito.id,
            codigo_remito=remito.codigo_remito,
            caso=remito.caso,
            tipo_movimiento=remito.tipo_movimiento,
            estado=remito.estado,
            fecha_emision=remito.fecha_emision,
            fecha_vencimiento=remito.fecha_vencimiento,
            hoja=remito.hoja,
            total_hojas=remito.total_hojas,
            titular=ParticipanteOut(
                rol="TITULAR",
                cuit=remito.titular.cuit,
                razon_social=remito.titular.razon_social,
                domicilio=remito.titular.domicilio,
            ),
            depositario=ParticipanteOut(
                rol="DEPOSITARIO",
                cuit=remito.depositario.cuit,
                razon_social=remito.depositario.razon_social,
                domicilio=remito.depositario.domicilio,
            ) if remito.depositario else None,
            destinatario=ParticipanteOut(
                rol="DESTINATARIO",
                cuit=remito.destinatario.cuit,
                razon_social=remito.destinatario.razon_social,
                domicilio=remito.destinatario.domicilio,
            ) if remito.destinatario else None,
            transportista=ParticipanteOut(
                rol="TRANSPORTISTA",
                cuit=remito.transportista.cuit,
                razon_social=remito.transportista.razon_social,
                domicilio=remito.transportista.domicilio,
            ),
            renglones=[
                RenglonRemitoOut(
                    codigo_afip=r.mercaderia.codigo_afip,
                    descripcion=r.mercaderia.descripcion,
                    unidades=Decimal(str(r.unidades)),
                    kilos=Decimal(str(r.kilos)),
                    numero_tropa=r.numero_tropa,
                )
                for r in remito.renglones
            ],
            total_kilos=sum((Decimal(str(r.kilos)) for r in remito.renglones), Decimal("0")),
            total_unidades=sum((Decimal(str(r.unidades)) for r in remito.renglones), Decimal("0")),
        )
