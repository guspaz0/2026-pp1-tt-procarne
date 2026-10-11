"""Validación de reglas de negocio de Remitos Electrónicos Cárnicos.

Aplica **Open/Closed**: cada regla es una subclase de :class:`ReglaValidacion`.
Para agregar una nueva regla se crea una subclase sin modificar el validador.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .dao import RemitoCarnico


@dataclass
class ResultadoValidacion:
    """Resultado de la validación de una regla."""

    valido: bool
    mensaje: str = ""

    @classmethod
    def ok(cls) -> "ResultadoValidacion":
        return cls(valido=True)

    @classmethod
    def error(cls, mensaje: str) -> "ResultadoValidacion":
        return cls(valido=False, mensaje=mensaje)


class ReglaValidacion(ABC):
    """Clase abstracta de una regla de validación de remito."""

    @abstractmethod
    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        raise NotImplementedError


class ReglaRequiereDepositario(ReglaValidacion):
    """Casos que requieren un depositario (sector C)."""

    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        from ..enums import CasoRemito

        caso = CasoRemito(remito.caso)
        if caso.tiene_depositario and remito.depositario_id is None:
            return ResultadoValidacion.error(f"El caso {caso.value} requiere un depositario")
        return ResultadoValidacion.ok()


class ReglaNoAdmiteDepositario(ReglaValidacion):
    """Casos que no admiten depositario."""

    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        from ..enums import CasoRemito

        caso = CasoRemito(remito.caso)
        if not caso.tiene_depositario and remito.depositario_id is not None:
            return ResultadoValidacion.error(f"El caso {caso.value} no admite depositario")
        return ResultadoValidacion.ok()


class ReglaRequiereDestinatario(ReglaValidacion):
    """Casos que requieren un destinatario (sector D)."""

    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        from ..enums import CasoRemito

        caso = CasoRemito(remito.caso)
        if caso.tiene_destinatario and remito.destinatario_id is None:
            return ResultadoValidacion.error(f"El caso {caso.value} requiere un destinatario")
        return ResultadoValidacion.ok()


class ReglaNoAdmiteDestinatario(ReglaValidacion):
    """Casos que no admiten destinatario (reparto y entrega en planta)."""

    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        from ..enums import CasoRemito

        caso = CasoRemito(remito.caso)
        if not caso.tiene_destinatario and remito.destinatario_id is not None:
            return ResultadoValidacion.error(f"El caso {caso.value} no admite destinatario")
        return ResultadoValidacion.ok()


class ReglaNumeroTropa(ReglaValidacion):
    """Cada renglón cuya mercadería lo requiere debe tener N° de tropa."""

    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        for i, renglon in enumerate(remito.renglones, start=1):
            if renglon.mercaderia and renglon.mercaderia.requiere_numero_tropa and not renglon.numero_tropa:
                return ResultadoValidacion.error(
                    f"Renglón {i}: la mercadería {renglon.mercaderia.codigo_afip} "
                    f"({renglon.mercaderia.descripcion}) requiere N° de tropa"
                )
        return ResultadoValidacion.ok()


class ReglaRenglonesNoVacios(ReglaValidacion):
    """El remito debe tener al menos un renglón."""

    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        if not remito.renglones:
            return ResultadoValidacion.error("El remito debe tener al menos un renglón de mercadería")
        return ResultadoValidacion.ok()


class ReglaFechas(ReglaValidacion):
    """La fecha de vencimiento debe ser posterior a la de emisión."""

    def validar(self, remito: "RemitoCarnico") -> ResultadoValidacion:
        if remito.fecha_vencimiento <= remito.fecha_emision:
            return ResultadoValidacion.error("La fecha de vencimiento debe ser posterior a la de emisión")
        return ResultadoValidacion.ok()


class ValidadorRemito:
    """Ejecuta un conjunto de reglas de validación sobre un remito."""

    def __init__(self, reglas: Optional[list[ReglaValidacion]] = None) -> None:
        self._reglas: list[ReglaValidacion] = (
            reglas
            if reglas is not None
            else [
                ReglaRequiereDepositario(),
                ReglaNoAdmiteDepositario(),
                ReglaRequiereDestinatario(),
                ReglaNoAdmiteDestinatario(),
                ReglaNumeroTropa(),
                ReglaRenglonesNoVacios(),
                ReglaFechas(),
            ]
        )

    def agregar_regla(self, regla: ReglaValidacion) -> "ValidadorRemito":
        self._reglas.append(regla)
        return self

    def validar(self, remito: "RemitoCarnico") -> list[str]:
        errores: list[str] = []
        for regla in self._reglas:
            resultado = regla.validar(remito)
            if not resultado.valido:
                errores.append(resultado.mensaje)
        return errores

    def es_valido(self, remito: "RemitoCarnico") -> bool:
        return not self.validar(remito)
