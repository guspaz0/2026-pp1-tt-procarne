# ROCCA — Control Cadena Cárnica SDE

Sistema de registro y control de la cadena cárnica provincial (Módulo I: Registro de Operadores).

## Stack

| Capa | Tecnología |
| --- | --- |
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS 4 |
| Backend | FastAPI (Python 3.12+) + SQLAlchemy 2 |
| Base de datos | PostgreSQL 15+ |
| Paquete (frontend) | pnpm |

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

| Servicio | URL |
| --- | --- |
| Backend (API + frontend compilado) | http://localhost:8000 |
| Frontend dev (Vite + HMR) | http://localhost:5173 |
| API health check | http://localhost:8000/api/health |

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

## Estructura del proyecto

```
├── run.sh                 # macOS / Linux — un comando para todo
├── run.ps1                # Windows PowerShell — un comando para todo
├── run.bat                # Windows CMD — wrapper de run.ps1
├── .env                   # Variables de entorno (ROCCA_DATABASE_URL)
├── especificaciones/      # Documentos de requerimiento y especificación
└── src/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py            # Entry point (uvicorn app.main:app)
    │   │   ├── app.py             # Composición de módulos (Módulo I activo)
    │   │   ├── configs/           # DAO base, DB engine
    │   │   ├── core/              # Entidades compartidas (Persona, etc.)
    │   │   └── modulos/
    │   │       └── registro_operadores/  # Módulo I — CRUD, schemas, servicio
    │   ├── migrations/            # Alembic (alembic upgrade head)
    │   └── .venv/                 # Virtual environment Python
    └── frontend/
        ├── src/
        │   ├── App.tsx            # Router (BrowserRouter)
        │   ├── AppRoutes.tsx      # Definición de rutas
        │   ├── components/
        │   │   ├── layout/        # Header, NavBar, Footer, AppLayout
        │   │   └── shared/        # Icons, FormField
        │   ├── routes/
        │   │   ├── modulo-i/      # Módulo I — Padrón, Jerarquía, Inscripción
        │   │   └── ModuloPage.tsx # Placeholder para módulos no implementados
        │   ├── store/             # Redux Toolkit slices + API
        │   └── types.ts           # Tipos compartidos
        └── vite.config.ts         # Proxy /api → :8000
```

## Rutas del frontend

| Ruta | Vista |
| --- | --- |
| `/` | Redirige a `/operadores` |
| `/operadores` | Redirige a `/operadores/padron` |
| `/operadores/padron` | Padrón de Sucursales (tabla) |
| `/operadores/jerarquia` | Jerarquía: Personas y Sucursales |
| `/operadores/inscripcion` | Formulario F 102 — Inscripción |
| `/remitos` | Remitos REC y Tránsito *(No implementado)* |
| `/fiscalizacion` | Fiscalización en Ruta *(No implementado)* |
| `/monitor` | Monitor Estratégico *(No implementado)* |
| `/portal` | Portal Público *(No implementado)* |
| `/faena` | Faena en Origen *(No implementado)* |

## Base de datos

- **Engine:** PostgreSQL (local o Docker).
- **Variable:** `ROCCA_DATABASE_URL` (ver `.env`).
- **Migraciones (Alembic):**

  ```bash
  cd src/backend
  source .venv/bin/activate          # Windows: .venv\Scripts\activate
  alembic upgrade head               # aplicar migraciones
  alembic revision --autogenerate -m "descripcion"  # generar nueva
  ```

- **Tablas (Módulo I):**

  | Tabla | Descripción |
  | --- | --- |
  | `personas` | Entidades legales (CUIT, razón social) |
  | `operadores` | Sucursales / establecimientos (FK → personas) |
  | `domicilios_operativos` | Domicilios adicionales por operador |
  | `habilitaciones` | Habilitaciones por operador |
  | `inscripciones` | Inscripciones F 102 |
  | `requisitos_inscripcion` | Checklist de requisitos |
  | `certificados` | Cartones F 102 emitidos |
  | `grupos_actividad` | Grupos económicos (A–Q) |
  | `subgrupos_actividad` | Subgrupos (FK → grupos) |
  | `actividades_economicas` | Actividades con alícuota (FK → subgrupos) |

## API (Módulo I)

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| GET | `/api/registro-operadores` | Lista operadores |
| POST | `/api/registro-operadores` | Crea operador |
| GET | `/api/registro-operadores/{id}` | Detalle |
| PUT | `/api/registro-operadores/{id}` | Actualiza |
| DELETE | `/api/registro-operadores/{id}` | Da de baja |
| GET | `/api/registro-operadores/{id}/certificados` | Certificados del operador |
| POST | `/api/registro-operadores/{id}/certificados` | Emite certificado |
| GET | `/api/registro-operadores/catalogo/actividades/grupos` | Grupos económicos |
| GET | `/api/registro-operadores/catalogo/actividades/subgrupos` | Subgrupos (filtro `?grupo=D`) |
| GET | `/api/registro-operadores/catalogo/actividades` | Actividades (filtro `?grupo=D&subgrupo=1511`) |

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

Solo el **Módulo I (Registro de Operadores)** está activo. Los demás módulos (II–VII) están comentados en `app/app.py` y sus rutas muestran un placeholder "No implementado".
