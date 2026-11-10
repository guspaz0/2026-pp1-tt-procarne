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
    CARNICERIA_CON_CAMARA = "CARNICERIA_CON_CAMARA"
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
    """Estado registral del operador.

    Ciclo de vida:
    PENDIENTE → (supervisor activa) → ACTIVO → (suspende) → SUSPENDIDO → (reactiva) → ACTIVO / (baja) → BAJADO
    """

    PENDIENTE = "PENDIENTE"
    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    BAJADO = "BAJADO"


class EstadoCertificado(str, Enum):
    """Estado del certificado de operador.

    Ciclo de vida:
    - ACTIVO: estado inicial al emitirse el certificado.
    - VENCIDO: fecha_vencimiento en el pasado (cálculo automático al consultar).
    - SUSPENDIDO: suspensión manual por supervisor.
    - RELEVADO: reemplazado por un certificado nuevo emitido antes del vencimiento.
    """

    ACTIVO = "ACTIVO"
    VENCIDO = "VENCIDO"
    SUSPENDIDO = "SUSPENDIDO"
    RELEVADO = "RELEVADO"


class TipoInscripcion(str, Enum):
    """Tipo de inscripción en el registro."""

    PRINCIPAL = "PRINCIPAL"
    SECUNDARIA = "SECUNDARIA"


class TipoDomicilio(str, Enum):
    """Tipo de domicilio del operador."""

    FISCAL = "FISCAL"
    OPERATIVO = "OPERATIVO"


class RequisitoAdjuntoPersona(str, Enum):
    """Requisitos de adjuntos de persona (compartidos entre todos sus operadores).

    Son documentos de identidad e impositivos que se cargan una sola vez.
    """

    DNI_FRENTE = "dni_frente"
    DNI_DORSO = "dni_dorso"
    CUIT = "cuit"
    IIBB = "iibb"


class RequisitoGeneralOperador(str, Enum):
    """Requisitos generales de adjuntos de operador (comunes a todas las categorías)."""

    AFIP_ULTIMO_PAGO = "afip_ultimo_pago"
    REGIMEN_PROVISIONAL = "regimen_provisional"


class RequisitoEspecifico(str, Enum):
    """Requisitos específicos según categoría de operador.

    Cada código corresponde a un documento que se adjunta por operador.
    """

    # Comunes a varias categorías
    FORMULARIO_101 = "formulario_101"
    HABILITACION_MUNICIPAL = "habilitacion_municipal"
    LIBRETA_SANITARIA = "libreta_sanitaria"

    # Sala de desposte
    MEMORIA_CONSTRUCTIVA = "memoria_constructiva"
    MEMORIA_OPERATIVA = "memoria_operativa"
    CERTIFICADO_EFLUENTES = "certificado_efluentes"

    # Cámaras frigoríficas / Carnicería con cámara
    PLANO_CAMARA = "plano_camara"
    MATRICULA_RUCA = "matricula_ruca"
    USUARIO_FAENADOR = "usuario_faenador"
    DOMINIO_CAMARA = "dominio_camara"
    HABILITACION_SANITARIA_CAMARA = "habilitacion_sanitaria_camara"

    # Fábrica de chacinados
    PLANOS_OBRA = "planos_obra"
    MEMORIA_EDILICIA = "memoria_edilicia"
    TASA_FOJAS = "tasa_fojas"
    PERMISO_VUELCO_EFLUENTES = "permiso_vuelco_efluentes"
    ACTA_CONSTITUCION = "acta_constitucion"
    DOMINIO_ESTABLECIMIENTO = "dominio_establecimiento"
    DDJJ_VOLUMEN = "ddjj_volumen"
    LIBRO_ACTAS = "libro_actas"
    INSCRIPCION_BROMATOLOGIA = "inscripcion_bromatologia"
