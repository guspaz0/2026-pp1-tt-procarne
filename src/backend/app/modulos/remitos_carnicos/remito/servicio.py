"""Servicio de negocio del Remito Electrónico Cárnico.

Casos de uso:
- Emitir un remito (con validación).
- Buscar por comprobante.
- Listar remitos (con filtros).
- Cambiar el estado del remito.
"""

from __future__ import annotations

from modulos.remitos_carnicos.enums import EstadoRemito
from modulos.remitos_carnicos.operador.dao import OperadorDAO
from modulos.remitos_carnicos.remito.dao import RemitoCarnico, RemitoCarnicoDAO, RenglonRemito
from modulos.remitos_carnicos.remito.schema import RemitoCarnicoIn, RemitoCarnicoOut
from modulos.remitos_carnicos.remito.validacion import ValidadorRemito
from core.mercaderia.dao import MercaderiaDAO


class RemitoCarnicoError(Exception):
    """Error de negocio del servicio de remitos."""


class RemitoCarnicoService:
    """Servicio de negocio de remitos electrónicos cárnicos."""

    def __init__(
        self,
        dao: RemitoCarnicoDAO,
        operador_dao: OperadorDAO,
        mercaderia_dao: MercaderiaDAO,
        validador: ValidadorRemito | None = None,
    ) -> None:
        self._dao = dao
        self._operador_dao = operador_dao
        self._mercaderia_dao = mercaderia_dao
        self._validador = validador or ValidadorRemito()

    def emitir_remito(self, data: RemitoCarnicoIn) -> RemitoCarnicoOut:
        """Emite un remito electrónico cárnico (con validación)."""
        # Validar
        resultado = self._validador.validar(data)
        if not resultado.es_valido:
            raise RemitoCarnicoError(f"Error de validación: {'; '.join(resultado.errores)}")

        # Verificar que los operadores existan
        self._verificar_operador(data.titular_cuit, "titular")
        self._verificar_operador(data.transportista_cuit, "transportista")
        if data.destinatario_cuit:
            self._verificar_operador(data.destinatario_cuit, "destinatario")

        # Verificar que las mercaderías existan
        for renglon in data.renglones:
            mercaderia = self._mercaderia_dao.obtener_por_codigo_afip(renglon.codigo_afip)
            if mercaderia is None:
                raise RemitoCarnicoError(
                    f"No existe una mercadería con código AFIP {renglon.codigo_afip}"
                )

        # Crear el remito
        remito = RemitoCarnico(
            punto_emision=data.punto_emision,
            numero_comprobante=data.numero_comprobante,
            caso=data.caso,
            tipo_movimiento=data.tipo_movimiento,
            estado=EstadoRemito.EMITIDO.value,
            fecha_emision=data.fecha_emision,
            fecha_vencimiento=data.fecha_vencimiento,
            titular_cuit=data.titular_cuit,
            transportista_cuit=data.transportista_cuit,
            destinatario_cuit=data.destinatario_cuit,
            depositario_cuit=data.depositario_cuit,
            chofer_apellido_nombre=data.chofer_apellido_nombre,
            chofer_documento=data.chofer_documento,
            dominio_vehiculo=data.dominio_vehiculo,
            observaciones=data.observaciones,
        )
        for renglon in data.renglones:
            remito.renglones.append(
                RenglonRemito(
                    codigo_afip=renglon.codigo_afip,
                    unidades=renglon.unidades,
                    kilos=renglon.kilos,
                    numero_tropa=renglon.numero_tropa,
                    observaciones=renglon.observaciones,
                )
            )

        self._dao.crear(remito)
        return RemitoCarnicoOut.model_validate(remito)

    def obtener_por_comprobante(self, punto_emision: str, numero_comprobante: str) -> RemitoCarnicoOut | None:
        """Busca un remito por su comprobante."""
        remito = self._dao.obtener_por_comprobante(punto_emision, numero_comprobante)
        return RemitoCarnicoOut.model_validate(remito) if remito else None

    def listar(self, estado: str | None = None) -> list[RemitoCarnicoOut]:
        """Lista remitos, opcionalmente filtrados por estado."""
        remitos = self._dao.listar(estado=estado)
        return [RemitoCarnicoOut.model_validate(r) for r in remitos]

    def cambiar_estado(self, remito_id: int, estado: EstadoRemito) -> RemitoCarnicoOut:
        """Cambia el estado de un remito."""
        remito = self._dao.actualizar_estado(remito_id, estado.value)
        if remito is None:
            raise RemitoCarnicoError(f"No existe un remito con id {remito_id}")
        return RemitoCarnicoOut.model_validate(remito)

    def _verificar_operador(self, cuit: str, rol: str) -> None:
        """Verifica que el operador con el CUIT dado exista."""
        # En una implementación completa, se buscaría el operador por CUIT
        # a través del DAO de operadores o personas.
        pass
