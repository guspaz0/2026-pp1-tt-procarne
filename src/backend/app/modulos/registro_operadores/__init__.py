"""Módulo I — Registro Provincial de Operadores (ROCCA).

Organización por entidad DAO (una carpeta por entidad):

- ``operador`` — agregado raíz: operador de la cadena cárnica.
- ``habilitacion`` — habilitación de un operador para una actividad.
- ``inscripcion`` — inscripción de un operador en el registro.
- ``actividad_economica`` — catálogo de actividades (DGR Santiago).
- ``certificado`` — certificado de habilitación F102.
- ``domicilio_operativo`` — domicilio operativo de un operador.
- ``requisito_inscripcion`` — requisitos generales/específicos por categoría.
- ``adjunto_operador`` — adjuntos (documentos) de operador.

Cada carpeta contiene (al menos):
- ``dao.py`` — modelo ORM (SQLAlchemy) + DAO.
- ``dto.py`` — schemas Pydantic (``*In`` request, ``*Out`` response).
- ``servicio.py`` — lógica de negocio (opcional si la entidad no lo necesita).
- ``controlador.py`` — router API FastAPI de la entidad.

El router del módulo (``controlador.py`` en la raíz) compone los routers de
cada entidad, y :class:`RegistroOperadoresModulo` compone los DAOs y
servicios.
"""

from modulos.registro_operadores.adjunto_operador.dao import AdjuntoOperador, AdjuntoOperadorDAO
from modulos.registro_operadores.actividad_economica.dao import (
    ActividadEconomica,
    GrupoActividad,
    SubgrupoActividad,
)
from modulos.registro_operadores.certificado.dao import Certificado, CertificadoDAO
from modulos.registro_operadores.controlador import crear_router
from modulos.registro_operadores.domicilio_operativo.dao import DomicilioOperativo
from modulos.registro_operadores.enums import (
    CategoriaOperador,
    EstadoCertificado,
    EstadoRegistral,
    TipoDomicilio,
    TipoInscripcion,
    TipoOperador,
)
from modulos.registro_operadores.habilitacion.dao import Habilitacion
from modulos.registro_operadores.inscripcion.dao import Inscripcion
from modulos.registro_operadores.operador.dao import Operador, OperadorDAO
from modulos.registro_operadores.operador.dto import OperadorIn, OperadorOut
from modulos.registro_operadores.operador.servicio import (
    OperadorError,
    OperadorService,
)
from modulos.registro_operadores.registro_operadores import RegistroOperadoresModulo
from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcion

__all__ = [
    "ActividadEconomica",
    "AdjuntoOperador",
    "AdjuntoOperadorDAO",
    "Certificado",
    "CertificadoDAO",
    "CategoriaOperador",
    "DomicilioOperativo",
    "EstadoCertificado",
    "EstadoRegistral",
    "GrupoActividad",
    "Habilitacion",
    "Inscripcion",
    "RequisitoInscripcion",
    "Operador",
    "OperadorDAO",
    "OperadorError",
    "OperadorIn",
    "OperadorOut",
    "OperadorService",
    "RegistroOperadoresModulo",
    "SubgrupoActividad",
    "TipoDomicilio",
    "TipoInscripcion",
    "TipoOperador",
    "crear_router",
]
