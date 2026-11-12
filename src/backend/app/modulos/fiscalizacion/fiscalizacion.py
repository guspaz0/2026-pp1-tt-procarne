# """Composición del Módulo III — Fiscalización.

# Clase que inyecta las dependencias (DAO, servicio) y registra el
# router en la aplicación FastAPI.
# """

# from __future__ import annotations

# from fastapi import FastAPI

# from modulos.fiscalizacion.controlador import crear_router
# from modulos.fiscalizacion.dao import FiscalizacionDAO
# from modulos.fiscalizacion.servicio import FiscalizacionService


# class FiscalizacionModulo:
#     """Módulo III — Fiscalización.

#     Responsabilidad única: componer el módulo (DAO + servicio + router)
#     y registrar sus endpoints en la aplicación.
#     """

#     def __init__(self, db_dao) -> None:
#         self._db_dao = db_dao
#         self._dao = FiscalizacionDAO(db_dao.obtener_sesion)
#         self._servicio = FiscalizacionService(self._dao)

#     def registrar(self, app: FastAPI) -> None:
#         """Registra el router del módulo en la aplicación."""
#         router = crear_router(self._servicio)
#         app.include_router(router)
