"""Enumeraciones del Módulo I — Registro Provincial de Operadores."""

from __future__ import annotations

from enum import Enum


class CategoriaOperador(str, Enum):
    """Categoría de operador según la especificación del Módulo I.

    Cada categoría define un conjunto de requisitos específicos
    para la inscripción en el Registro Provincial de Operadores.
    """

    SALA_DE_DESPOSTE = "SALA_DE_DESPOSTE"
    CAMARAS_FRIGORIFICAS = "CAMARAS_FRIGORIFICAS"
    FABRICA_DE_CHACINADOS = "FABRICA_DE_CHACINADOS"
    CARNICERIAS = "CARNICERIAS"
    TRANSPONEDOR = "TRANSPONEDOR"
    SUPERMERCADO = "SUPERMERCADO"
    DISTRIBUIDOR = "DISTRIBUIDOR"


class TipoOperador(str, Enum):
    """Tipo de operador de la cadena cárnica (clasificación general)."""

    PRODUCTOR = "PRODUCTOR"
    FRIGORIFICO = "FRIGORIFICO"
    CARNICERIA = "CARNICERIA"
    COMERCIALIZADOR = "COMERCIALIZADOR"
    TRANSPORTE = "TRANSPORTE"
    DEPOSITO = "DEPOSITO"


class EstadoRegistral(str, Enum):
    """Estado registral del operador."""

    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    BAJADO = "BAJADO"


class TipoInscripcion(str, Enum):
    """Tipo de inscripción en el registro."""

    PRINCIPAL = "PRINCIPAL"
    SECUNDARIA = "SECUNDARIA"


class TipoDomicilio(str, Enum):
    """Tipo de domicilio del operador."""

    FISCAL = "FISCAL"
    OPERATIVO = "OPERATIVO"


class RequisitoGeneral(str, Enum):
    """Requisitos generales de inscripción (comunes a todas las categorías)."""

    INGRESOS_BRUTOS = "INGRESOS_BRUTOS"
    AFIP = "AFIP"
    REGIMEN_PROVISIONAL = "REGIMEN_PROVISIONAL"


class RequisitoEspecifico(str, Enum):
    """Requisitos específicos según categoría de operador."""

    # Sala de desposte
    REGISTRO_NACIONAL_FRIGORIFICOS = "REGISTRO_NACIONAL_FRIGORIFICOS"
    # Cámaras frigoríficas
    REGISTRO_NACIONAL_CAMARAS = "REGISTRO_NACIONAL_CAMARAS"
    # Fábrica de chacinados
    REGISTRO_NACIONAL_CHACINADOS = "REGISTRO_NACIONAL_CHACINADOS"
    # Carnicerías
    MATRICULA_MUNICIPAL_CARNICERIA = "MATRICULA_MUNICIPAL_CARNICERIA"
    # Transportista
    REGISTRO_NACIONAL_TRANSPORTE = "REGISTRO_NACIONAL_TRANSPORTE"
    # Supermercado
    MATRICULA_MUNICIPAL_SUPERMERCADO = "MATRICULA_MUNICIPAL_SUPERMERCADO"
    # Distribuidor
    REGISTRO_NACIONAL_DISTRIBUIDOR = "REGISTRO_NACIONAL_DISTRIBUIDOR"
