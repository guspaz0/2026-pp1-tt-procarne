"""Servicio de negocio del operador."""

from __future__ import annotations

from typing import Optional

from modulos.genericos.persona.dao import Persona
from .dao import Operador, OperadorDAO
from .schema import OperadorIn, OperadorOut


class OperadorError(Exception):
    """Error de negocio del módulo de operadores."""


class OperadorService:
    """Caso de uso: gestión de operadores de la cadena cárnica."""

    def __init__(self, dao: OperadorDAO) -> None:
        self._dao = dao

    def crear(self, datos: OperadorIn) -> OperadorOut:
        existente = self._dao.obtener_por_cuit(datos.cuit)
        if existente is not None:
            raise OperadorError(f"Operador ya existe: CUIT {datos.cuit}")

        # Crear persona jurídica
        persona = Persona(
            tipo="PJ",
            identificador=datos.cuit,
            nombre=datos.razon_social,
            cuit=datos.cuit,
            domicilio=datos.domicilio,
            telefono=datos.telefono,
            email=datos.email,
        )
        
        # Crear operador referenciando a la persona
        operador = Operador(
            persona_id=persona.id,
            domicilio_fiscal=datos.domicilio_fiscal,
        )
        
        guardado = self._dao.guardar(operador, persona)
        return OperadorOut.from_orm(guardado)

    def obtener(self, cuit: str) -> OperadorOut:
        operador = self._dao.obtener_por_cuit(cuit)
        if operador is None:
            raise OperadorError(f"Operador no encontrado: CUIT {cuit}")
        return OperadorOut.from_orm(operador)

    def listar(self, limite: int = 100, offset: int = 0) -> list[OperadorOut]:
        operadores = self._dao.listar(limite=limite, offset=offset)
        return [OperadorOut.from_orm(o) for o in operadores]
