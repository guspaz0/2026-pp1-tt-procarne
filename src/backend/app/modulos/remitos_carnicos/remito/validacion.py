# """Validación de remitos electrónicos cárnicos.

# Las reglas de validación son extensibles mediante subclases de
# :class:`ReglaValidacion`.
# """

# from __future__ import annotations

# from abc import ABC, abstractmethod
# from dataclasses import dataclass, field

# from modulos.remitos_carnicos.remito.schema import RemitoCarnicoIn


# @dataclass
# class ResultadoValidacion:
#     """Resultado de la validación de un remito."""

#     es_valido: bool
#     errores: list[str] = field(default_factory=list)

#     def agregar_error(self, mensaje: str) -> None:
#         """Agrega un error de validación."""
#         self.errores.append(mensaje)
#         self.es_valido = False


# class ReglaValidacion(ABC):
#     """Clase base abstracta para reglas de validación de remitos."""

#     @abstractmethod
#     def validar(self, remito: RemitoCarnicoIn) -> None:
#         """Valida el remito y agrega errores al resultado."""
#         raise NotImplementedError

#     @property
#     @abstractmethod
#     def nombre(self) -> str:
#         """Nombre de la regla."""
#         raise NotImplementedError


# class ReglaPuntoEmision(ReglaValidacion):
#     """Valida que el punto de emisión tenga 4 dígitos."""

#     @property
#     def nombre(self) -> str:
#         return "Punto de emisión"

#     def validar(self, remito: RemitoCarnicoIn) -> None:
#         resultado = self._resultado
#         if len(remito.punto_emision) != 4 or not remito.punto_emision.isdigit():
#             resultado.agregar_error("El punto de emisión debe tener 4 dígitos")

#     def __init__(self) -> None:
#         self._resultado: ResultadoValidacion | None = None

#     def ejecutar(self, remito: RemitoCarnicoIn, resultado: ResultadoValidacion) -> None:
#         self._resultado = resultado
#         self.validar(remito)


# class ReglaNumeroComprobante(ReglaValidacion):
#     """Valida que el número de comprobante tenga 10 dígitos."""

#     @property
#     def nombre(self) -> str:
#         return "Número de comprobante"

#     def validar(self, remito: RemitoCarnicoIn) -> None:
#         resultado = self._resultado
#         if len(remito.numero_comprobante) != 10 or not remito.numero_comprobante.isdigit():
#             resultado.agregar_error("El número de comprobante debe tener 10 dígitos")

#     def __init__(self) -> None:
#         self._resultado: ResultadoValidacion | None = None

#     def ejecutar(self, remito: RemitoCarnicoIn, resultado: ResultadoValidacion) -> None:
#         self._resultado = resultado
#         self.validar(remito)


# class ReglaFechaVencimiento(ReglaValidacion):
#     """Valida que la fecha de vencimiento sea posterior a la fecha de emisión."""

#     @property
#     def nombre(self) -> str:
#         return "Fecha de vencimiento"

#     def validar(self, remito: RemitoCarnicoIn) -> None:
#         resultado = self._resultado
#         if remito.fecha_vencimiento <= remito.fecha_emision:
#             resultado.agregar_error("La fecha de vencimiento debe ser posterior a la fecha de emisión")

#     def __init__(self) -> None:
#         self._resultado: ResultadoValidacion | None = None

#     def ejecutar(self, remito: RemitoCarnicoIn, resultado: ResultadoValidacion) -> None:
#         self._resultado = resultado
#         self.validar(remito)


# class ReglaRenglones(ReglaValidacion):
#     """Valida que el remito tenga al menos un renglón."""

#     @property
#     def nombre(self) -> str:
#         return "Renglones"

#     def validar(self, remito: RemitoCarnicoIn) -> None:
#         resultado = self._resultado
#         if not remito.renglones:
#             resultado.agregar_error("El remito debe tener al menos un renglón")

#     def __init__(self) -> None:
#         self._resultado: ResultadoValidacion | None = None

#     def ejecutar(self, remito: RemitoCarnicoIn, resultado: ResultadoValidacion) -> None:
#         self._resultado = resultado
#         self.validar(remito)


# class ValidadorRemito:
#     """Validador de remitos electrónicos cárnicos.

#     Aplica una lista de reglas de validación y devuelve el resultado.
#     """

#     def __init__(self, reglas: list[ReglaValidacion] | None = None) -> None:
#         self._reglas = reglas or [
#             ReglaPuntoEmision(),
#             ReglaNumeroComprobante(),
#             ReglaFechaVencimiento(),
#             ReglaRenglones(),
#         ]

#     def validar(self, remito: RemitoCarnicoIn) -> ResultadoValidacion:
#         """Valida el remito aplicando todas las reglas."""
#         resultado = ResultadoValidacion(es_valido=True)
#         for regla in self._reglas:
#             regla.ejecutar(remito, resultado)
#         return resultado
