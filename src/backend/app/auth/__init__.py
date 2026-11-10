"""Autenticación de ROCCA: InsForge como Identity Provider (IdP).

FastAPI actúa como Backend-for-Frontend (BFF):
- El frontend NUNCA habla con InsForge directamente: solo con FastAPI.
- InsForge emite los tokens (JWT de acceso + refresh); FastAPI los valida,
  los guarda en cookies HttpOnly y los reenvía a InsForge para las
  operaciones de base de datos acotadas al usuario (RLS).

Ver ``app/core/insforge/`` para el cliente y ``app/auth/`` para el middleware,
el servicio, los schemas y el router.
"""
