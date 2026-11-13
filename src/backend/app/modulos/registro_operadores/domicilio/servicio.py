"""Servicio de Domicilios."""

from __future__ import annotations

from typing import Optional

from modulos.registro_operadores.domicilio.dao import Domicilio, DomicilioDAO


class DomicilioService:
    """Servicio de domicilios de operadores."""

    def __init__(self, dao: DomicilioDAO) -> None:
        self._dao = dao

    def obtener(self, domicilio_id: int) -> Optional[Domicilio]:
        """Obtiene un domicilio por su id."""
        return self._dao.obtener_por_id(domicilio_id)

    def listar(self) -> list[Domicilio]:
        """Lista todos los domicilios."""
        return self._dao.listar()

    def obtener(self, domicilio_id: int) -> Optional[Domicilio]:
        """Obtiene un domicilio por su id."""
        return self._dao.obtener_por_id(domicilio_id)

    def crear(self, operador_id: int, calle: str,
              numero: str | None = None,
              localidad: str = "",
              provincia: str = "",
              codigo_postal: str | None = None) -> Domicilio:
        """Crea un domicilio nuevo."""
        return self._dao.crear(operador_id, calle, numero, localidad,
                               provincia, codigo_postal)

    def actualizar(self, domicilio_id: int, **kwargs) -> Optional[Domicilio]:
        """Actualiza un domicilio."""
        return self._dao.actualizar(domicilio_id, **kwargs)

    def eliminar(self, domicilio_id: int) -> bool:
        """Elimina un domicilio."""
        return self._dao.eliminar(domicilio_id)
