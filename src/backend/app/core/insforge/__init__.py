"""Cliente de InsForge (identity provider).

Cliente HTTP ``httpx`` que habla con la API de InsForge. Sin dependencias
externas de SDK: InsForge expone una API REST documentada (auth, database)
que se consume con ``httpx.AsyncClient``.

Dos credenciales con privilegios distintos:
- **API key** (``ik_...``): acceso administrativo; BYPASS de RLS. Se usa solo
  para operaciones de gestión (crear usuario, enviar verificación).
- **Token de usuario** (JWT emitido por InsForge al hacer login): se reenvía en
  cada operación de base de datos para que InsForge aplique RLS como ese
  usuario.
"""
