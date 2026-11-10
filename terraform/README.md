# ROCCA — Terraform (Vercel)

Deploy del monorepo a **Vercel** (framework `fastapi`):

- **Backend** (FastAPI, `src/backend`) → Vercel, framework `fastapi`.
- **Frontend** (Vite/React, `src/frontend`) → se builda localmente
  (`pnpm build`) y se emite en `src/backend/app/static/`. Vercel sirve
  el build estático como fallback SPA (el backend tiene un catch-all
  `GET /{ruta:path}` que devuelve `index.html`).

> No hay conexión a GitHub: el deploy se hace con `vercel_deployment`
> subiendo los archivos locales (regenerados por `sync.sh`).

## Estructura

```
terraform/
├── main.tf                    # vercel_project + vercel_deployment + env vars
├── providers.tf               # required_providers + provider vercel (con team)
├── variables.tf               # Variables de entrada
├── outputs.tf                 # Outputs (app_url, deployment_url, deployment_id)
├── sync.sh                    # Copia limpia de src/backend → deploy/backend
├── terraform.tfvars.example   # Plantilla de variables (no commitear .tfvars)
└── deploy/backend/            # Generado por sync.sh (no commitear)
```

## Requisitos

- Terraform >= 1.5
- API token de Vercel: <https://vercel.com/account/tokens>
  - El token debe pertenecer al **team** que posee el proyecto
    (`vercel_team_id` en `terraform.tfvars`). Sin el team, la API
    responde 403 Forbidden.
- `rsync` instalado (lo usa `sync.sh`).
- Para buildar el frontend antes del deploy: `pnpm` en `src/frontend`.

## Variables

| Variable              | Sensitive | Descripción                                              | Default                       |
|-----------------------|-----------|----------------------------------------------------------|-------------------------------|
| `vercel_api_token`    | sí        | API token de Vercel                                      | —                             |
| `vercel_project_name` | no        | Nombre del proyecto en Vercel (define la URL)            | `procarne`                    |
| `vercel_team_id`      | no        | ID del team de Vercel (`team_xxx`)                       | `team_jBuR0GcDPltyl5R6JqLOsSPO` |
| `rocca_database_url`  | sí        | URL de PostgreSQL (Insforge / Neon) — **no SQLite**      | —                             |
| `insforge_url`        | no        | URL del proyecto Insforge (IdP)                          | —                             |
| `insforge_api_key`    | sí        | API Key administrativa de Insforge (`ik_...`)            | —                             |

## Flujo de deploy

```bash
cd terraform

# 1) Build del frontend (emite en src/backend/app/static)
cd ../src/frontend && pnpm build && cd ../terraform

# 2) Regenerar la copia limpia para Vercel
./sync.sh

# 3) Init (solo la primera vez) + apply
terraform init
terraform apply
```

`sync.sh` copia `src/backend/` → `deploy/backend/` excluyendo `.venv`,
`__pycache__`, `.pytest_cache`, `*.db` y `.git`. El resource
`vercel_deployment.api` sube ese directorio a Vercel.

## Variables de entorno inyectadas en Vercel

| Key                   | Source                    | Sensitive |
|-----------------------|---------------------------|-----------|
| `ROCCA_DATABASE_URL`  | `var.rocca_database_url`  | sí        |
| `INSFORGE_URL`        | `var.insforge_url`        | no        |
| `INSFORGE_API_KEY`    | `var.insforge_api_key`    | sí        |

Se inyectan para los targets `production` y `preview`.

## Outputs

- `app_url` — URL del backend en Vercel (`https://<vercel_project_name>.vercel.app`)
- `deployment_url` — URL del deployment de producción actual (cambia en cada apply)
- `deployment_id` — ID del deployment de producción actual

## Notas

- El backend lee `ROCCA_DATABASE_URL` (PostgreSQL en prod; **siempre**
  PostgreSQL, no SQLite — en Vercel el filesystem es efímero).
- `ROCCA_CORS_ORIGINS`: inyectarlo como env var de Vercel con la URL del
  frontend si hace fetch al backend desde otro origen. En este setup el
  frontend se sirve desde el mismo origen que el backend (catch-all SPA),
  así que CORS no es un problema.
- `ROCCA_COOKIE_SECURE`: en producción (HTTPS) dejar en `1` (default).
  Para desarrollo local por HTTP, fijar en `0`.
- Health check del backend: `GET /api/health`.
- Límites de Vercel con FastAPI (función serverless): sin tareas de fondo
  largas ni WebSockets; cold starts por `crear_app()`; límite de tamaño de
  bundle.
- State: no commitear `terraform.tfstate` ni `*.tfvars`. Para uso en equipo,
  usar un backend remoto (Terraform Cloud, S3).
- El frontend no se despliega por separado: `pnpm build` emite en
  `src/backend/app/static/` y el backend lo sirve como SPA.
