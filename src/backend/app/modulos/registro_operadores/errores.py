"""Errores de negocio compartidos del Módulo I — Registro Provincial de Operadores.

Módulo intencionalmente sin dependencias internas para poder ser importado
desde cualquier entidad sin generar ciclos de importación.
"""


class OperadorError(Exception):
    """Error de negocio del módulo de registro de operadores."""
