# ROCCA — monorepo (workflow mínimo)

Estructura mínima de trabajo: backend Python que sirve la API y el frontend
React/TypeScript transpilado como estáticos.

```
src/
  backend/
    app/main.py            # FastAPI: API JSON + SPA (index.html + /static)
    requirements.txt
  frontend/
    index.html             # entrada del build (Vite)
    package.json           # scripts: dev / build / preview
    pnpm-lock.yaml
    vite.config.ts         # base /static/, proxy /api → :8000
    tsconfig.json
    src/
      main.tsx             # bootstrap React
      App.tsx              # componente raíz (consume /api/operadores)
```

## Flujo

```
┌────────────────────────┐        ┌──────────────────────────────┐
│  src/frontend (TS)     │ build  │  src/frontend/dist/          │
│  React + TypeScript    │ ─────▶ │  index.html + static/*.js    │
└────────────────────────┘  Vite  └──────────────┬───────────────┘
                                                  │ sirve como estático
┌────────────────────────┐                        ▼
│  src/backend (Python)  │  ──▶  FastAPI: /api/*  (JSON)
│  FastAPI + uvicorn     │         /static/*      (assets)
└────────────────────────┘         /*              (SPA fallback → index.html)
```

## Uso (pnpm)

```bash
# Frontend (desarrollo, Vite en :5173 con proxy de /api al backend)
cd src/frontend && pnpm install && pnpm run dev

# Build de producción (genera dist/ que consume el backend)
cd src/frontend && pnpm run build

# Backend (sirve API + estáticos en :8000)
cd src/backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

- **Dev**: `pnpm run dev` (Vite :5173, proxy `/api` → uvicorn :8000).
- **Producción**: `pnpm run build` genera `dist/`; uvicorn sirve todo desde :8000.

## Notas

- La estructura de `src/` es un monorepo plano (sin workspaces npm ni Poetry todavía); se puede agregar `package.json` root con npm workspaces y `pyproject.toml` cuando el proyecto crezca.
- El backend usa FastAPI como placeholder del servicio; cuando se defina la capa de persistencia se agrega SQLAlchemy + PostgreSQL (según `especificaciones/actividad-mantenimiento.md`).
