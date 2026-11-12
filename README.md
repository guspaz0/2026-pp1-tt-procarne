# ROCCA — Control Cadena Cárnica SDE

Sistema de registro y control de la cadena cárnica provincial (Módulo I: Registro de Operadores).

## Stack

| Capa               | Tecnología                                    |
| ------------------ | --------------------------------------------- |
| Frontend           | React 18 + TypeScript + Vite + Tailwind CSS 4 |
| Backend            | FastAPI (Python 3.12+) + SQLAlchemy 2         |
| Base de datos      | PostgreSQL 15+                                |
| Paquete (frontend) | pnpm                                          |

## Requisitos previos

- **Python 3.12+** instalado en el PATH.
- **Node.js 18+** y **pnpm** (`npm i -g pnpm`).
- **PostgreSQL** corriendo en `localhost:5432` con base `rocca` y usuario `gusta` (ver `.env`).
- En Windows, usar **Git Bash**, **WSL** o **PowerShell** (ver sección Windows).

## Arranque rápido (macOS / Linux)

```bash
./run.sh
```

Esto:

1. Verifica que PostgreSQL esté accesible en `localhost:5432`.
2. Compila el frontend (Vite + Tailwind) → emite en `src/backend/app/static/`.
3. Levanta el backend FastAPI en `http://localhost:8000`.
4. Levanta el Vite dev server en `http://localhost:5173` (proxy `/api` → `:8000`).

Opciones:

```bash
./run.sh --no-build   # salta la compilación del frontend
```

Para detener, `Ctrl+C`.

### URLs

| Servicio                           | URL                                |
| ---------------------------------- | ---------------------------------- |
| Backend (API + frontend compilado) | <http://localhost:8000>            |
| Frontend dev (Vite + HMR)          | <http://localhost:5173>            |
| API health check                   | <http://localhost:8000/api/health> |

## Arranque rápido (Windows)

### Opción A — PowerShell

```powershell
.\run.ps1
```

### Opción B — CMD

```cmd
run.bat
```

Ambos scripts hacen lo mismo que `./run.sh` en macOS/Linux. Requieren que PostgreSQL esté corriendo localmente (o en Docker).

> **Nota:** En Windows, el venv de Python usa `.venv\Scripts\activate` en lugar de `.venv/bin/activate`. Los scripts ya lo manejan.

## Desarrollo

```bash
# Terminal 1 — Backend (hot reload)
cd src/backend
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend (Vite HMR)
cd src/frontend
pnpm dev

# Build de producción (emite en backend/app/static)
cd src/frontend
pnpm build
```

## Scope actual (Sprint 1)

Solo el **Módulo I (Registro de Operadores)** está /Users/gusta/Downloads/cuase.pdf/Users/gusta/Downloads/cuase.pdfactivo. Los demás módulos (II–VII) están comentados en `app/app.py` y sus rutas muestran un placeholder "No implementado".
