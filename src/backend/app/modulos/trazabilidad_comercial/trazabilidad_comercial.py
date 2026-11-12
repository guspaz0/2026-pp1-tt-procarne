# """Composición del Módulo II — Trazabilidad Comercial.

# Clase que inyecta las dependencias (DAO, servicio) y registra el
# router en la aplicación FastAPI.
# """

# from __future__ import annotations

# from fastapi import FastAPI

# from modulos.trazabilidad_comercial.controlador import crear_router
# from modulos.trazabilidad_comercial.dao import RegistroTrazabilidadDAO
# from modulos.trazabilidad_comercial.servicio import TrazabilidadComercialService


# class TrazabilidadComercialModulo:
#     """Módulo II — Trazabilidad Comercial.

#     Responsabilidad única: componer el módulo (DAO + servicio + router)
#     y registrar sus endpoints en la aplicación.
#     """

#     def __init__(self, db_dao) -> None:
#         self._db_dao = db_dao
#         self._dao = RegistroTrazabilidadDAO(db_dao.obtener_sesion)
#         self._servicio = TrazabilidadComercialService(self._dao)

#     def registrar(self, app: FastAPI) -> None:
#         """Registra el router del módulo en la aplicación."""
#         router = crear_router(self._servicio)
#         app.include_router(router)
