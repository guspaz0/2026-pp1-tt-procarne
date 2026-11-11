"""Lógica de negocio de ``RequisitoInscripcion``.

Incluye el catálogo de requisitos:
- :data:`REQUISITOS_ADJUNTO_PERSONA` — adjuntos de persona (compartidos).
- :data:`REQUISITOS_GENERALES` — requisitos generales de operador.
- :data:`REQUISITOS_ESPECIFICOS_POR_CATEGORIA` — matriz de requisitos
  específicos por categoría (según especificación del Módulo I).
"""

from __future__ import annotations

from modulos.registro_operadores.enums import (
    CategoriaOperador,
    RequisitoAdjuntoPersona,
    RequisitoEspecifico,
    RequisitoGeneralOperador,
)
from modulos.registro_operadores.errores import OperadorError
from modulos.registro_operadores.requisito_inscripcion.dao import RequisitoInscripcionDAO
from modulos.registro_operadores.requisito_inscripcion.dto import RequisitoInscripcionOut


# ---------------------------------------------------------------------------
# Catálogo de requisitos (según especificación del Módulo I)
# ---------------------------------------------------------------------------

# Adjuntos de persona (compartidos entre todos sus operadores)
REQUISITOS_ADJUNTO_PERSONA: list[str] = [
    RequisitoAdjuntoPersona.DNI_FRENTE.value,
    RequisitoAdjuntoPersona.DNI_DORSO.value,
    RequisitoAdjuntoPersona.CUIT.value,
    RequisitoAdjuntoPersona.IIBB.value,
]

# Requisitos generales de operador (comunes a todas las categorías)
REQUISITOS_GENERALES: list[str] = [
    RequisitoGeneralOperador.AFIP_ULTIMO_PAGO.value,
    RequisitoGeneralOperador.REGIMEN_PROVISIONAL.value,
]

# Matriz de requisitos específicos por categoría (según especificación)
REQUISITOS_ESPECIFICOS_POR_CATEGORIA: dict[str, list[str]] = {
    CategoriaOperador.SALA_DE_DESPOSTE.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.MEMORIA_CONSTRUCTIVA.value,
        RequisitoEspecifico.MEMORIA_OPERATIVA.value,
        RequisitoEspecifico.CERTIFICADO_EFLUENTES.value,
    ],
    CategoriaOperador.CAMARAS_FRIGORIFICAS.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.PLANO_CAMARA.value,
        RequisitoEspecifico.MATRICULA_RUCA.value,
        RequisitoEspecifico.USUARIO_FAENADOR.value,
        RequisitoEspecifico.DOMINIO_CAMARA.value,
        RequisitoEspecifico.HABILITACION_SANITARIA_CAMARA.value,
    ],
    CategoriaOperador.FABRICA_DE_CHACINADOS.value: [
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.LIBRETA_SANITARIA.value,
        RequisitoEspecifico.MEMORIA_OPERATIVA.value,
        RequisitoEspecifico.PLANOS_OBRA.value,
        RequisitoEspecifico.MEMORIA_EDILICIA.value,
        RequisitoEspecifico.TASA_FOJAS.value,
        RequisitoEspecifico.PERMISO_VUELCO_EFLUENTES.value,
        RequisitoEspecifico.ACTA_CONSTITUCION.value,
        RequisitoEspecifico.DOMINIO_ESTABLECIMIENTO.value,
        RequisitoEspecifico.DDJJ_VOLUMEN.value,
        RequisitoEspecifico.LIBRO_ACTAS.value,
        RequisitoEspecifico.INSCRIPCION_BROMATOLOGIA.value,
    ],
    CategoriaOperador.CARNICERIAS.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.LIBRETA_SANITARIA.value,
    ],
    CategoriaOperador.CARNICERIA_CON_CAMARA.value: [
        RequisitoEspecifico.FORMULARIO_101.value,
        RequisitoEspecifico.HABILITACION_MUNICIPAL.value,
        RequisitoEspecifico.LIBRETA_SANITARIA.value,
        RequisitoEspecifico.PLANO_CAMARA.value,
        RequisitoEspecifico.MATRICULA_RUCA.value,
        RequisitoEspecifico.USUARIO_FAENADOR.value,
        RequisitoEspecifico.DOMINIO_CAMARA.value,
        RequisitoEspecifico.HABILITACION_SANITARIA_CAMARA.value,
    ],
    # Transportista, Supermercado y Distribuidor: pendientes de definir
    CategoriaOperador.TRANSPONEDOR.value: [],
    CategoriaOperador.SUPERMERCADO.value: [],
    CategoriaOperador.DISTRIBUIDOR.value: [],
}


class RequisitoInscripcionService:
    """Servicio de negocio de requisitos de inscripción."""

    def __init__(self, dao: RequisitoInscripcionDAO) -> None:
        self._dao = dao

    def listar(self, operador_id: int) -> list[RequisitoInscripcionOut]:
        """Lista los requisitos de inscripción de un operador."""
        requisitos = self._dao.listar_por_operador(operador_id)
        return [RequisitoInscripcionOut.model_validate(r) for r in requisitos]

    def listar_pendientes(self, operador_id: int) -> list[RequisitoInscripcionOut]:
        """Lista los requisitos aún no cumplidos de un operador."""
        requisitos = self._dao.listar_por_operador(operador_id)
        pendientes = [r for r in requisitos if not r.cumplido]
        return [RequisitoInscripcionOut.model_validate(r) for r in pendientes]

    def actualizar(self, operador_id: int, requisito_id: int,
                   cumplido: bool, observaciones: str | None = None) -> RequisitoInscripcionOut:
        """Actualiza el estado de cumplimiento de un requisito."""
        requisito = self._dao.actualizar_cumplimiento(requisito_id, cumplido, observaciones)
        if requisito is None or requisito.operador_id != operador_id:
            raise OperadorError(f"No existe el requisito {requisito_id} para el operador {operador_id}")
        return RequisitoInscripcionOut.model_validate(requisito)

    # ------------------------------------------------------------------
    # Catálogo de requisitos
    # ------------------------------------------------------------------

    def obtener_requisitos_especificos_por_categoria(self, categoria: str) -> list[str]:
        """Devuelve los códigos de requisitos específicos para una categoría."""
        return REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, [])

    def requisitos_para_categoria(self, categoria: str) -> list[str]:
        """Devuelve todos los requisitos de adjunto (generales + específicos) para una categoría."""
        return REQUISITOS_GENERALES + REQUISITOS_ESPECIFICOS_POR_CATEGORIA.get(categoria, [])

    def validar_requisito_para_categoria(self, categoria: str, requisito: str) -> bool:
        """Valida que un requisito corresponda a la categoría del operador."""
        validos = self.requisitos_para_categoria(categoria)
        return requisito in validos
