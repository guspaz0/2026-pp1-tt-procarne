# ROCCA — Terraform (Vercel vía GitHub)

Deploy del monorepo:

- **Backend** (FastAPI, `src/backend`) → **Vercel**, conectado al repositorio
  GitHub con `git_repository`: **cada push genera un deployment automático**
  (`main` → producción, demás branches → preview deployments).
- **Frontend** (Vite/React, `src/frontend`) → **Netlify** (deploy del site
  vía `netlify-cli`, fuera de Terraform).

> El deploy anterior en **Render** quedó como residuo en `terraform.tfstate`
> (`render_web_service.api`) — descartarlo antes de `apply` (ver abajo).

## Estructura

```
terraform/
├── main.tf        # vercel_project.api + vercel_git_repository.api + env vars + outputs
├── providers.tf   # required_providers + provider vercel
├── variables.tf   # Variables
└── terraform.tfvars.example  # Plantilla de variables (no commitear .tfvars)
```

## Requisitos

- Terraform >= 1.5
- `netlify-cli` instalado (`npm i -g netlify-cli`)
- API token de Vercel: <https://vercel.com/account/tokens>
  - El token debe pertenecer a la cuenta **guspaz0** que ya tiene Vercel
    conectado a GitHub (el repo ya está vinculado, así que no hay que
    re-autorizar).
- Personal access token de Netlify: <https://app.netlify.com/user/applications#personal-access-tokens>
- Site de Netlify ya creado en el dashboard (el provider no soporta creación de sites)

## Variables

| Variable              | Sensitive | Descripción                                              | Default                       |
|-----------------------|-----------|----------------------------------------------------------|-------------------------------|
| `vercel_api_token`    | sí        | API token de Vercel                                      | —                             |
| `vercel_project_name` | no        | Nombre del proyecto en Vercel (define la URL)            | `procarne`                    |
| `github_repo`         | no        | Repo GitHub `owner/name` al que se conecta Vercel        | `guspaz0/2026-pp1-tt-procarne` |
| `rocca_database_url`  | sí        | URL de PostgreSQL (Insforge / Neon) — **no SQLite**      | —                             |
| `netlify_token`       | sí        | Personal access token de Netlify                         | —                             |
| `netlify_site_id`     | no        | ID del site en Netlify (lo ves en la URL del dashboard)   | `procarne-sde`                |

## Cómo funciona el redeploy automático

1. Vercel se conecta a `guspaz0/2026-pp1-tt-procarne` en GitHub
   (`vercel_project.git_repository` + `vercel_git_repository`).
2. Cada push a cualquier branch dispara un deployment vía webhook:
   - `main` → **producción** (`https://procarne.vercel.app`).
   - Cualquier otra branch → **preview deployment** con URL efímera.
3. Vercel clona el repo, instala dependencias de `src/backend/requirements.txt`
   y builda el framework `fastapi`. No se necesita `vercel_deployment`
   (subida de archivos local) ni `vercel.json` extra.

## Uso

```bash
cd terraform

# 1) Descartar el estado antiguo de Render (solo la primera vez):
terraform state rm render_web_service.api

# 2) Init + apply:
terraform init
terraform apply
```

Variables: por defecto se toman de `terraform.tfvars` (local, no commitear).
Si no existe, copiar `terraform.tfvars.example` a `terraform.tfvars` y
completar los valores.

Después del apply, todo push a GitHub ya redirige automáticamente a Vercel.
Para verificar: Vercel Dashboard → proyecto `procarne` → tab *Git*, debe
mostrar el repo conectado y el historial de deployments por push.

## Redeploys manuales (opcional)

- **Backend**: push a la branch (o `git push` de un commit vacío si solo
  se quiere re-trigger): `git commit --allow-empty -m "redeploy" && git push`.
- **Frontend (Netlify)**:
  ```bash
  cd ../src/frontend && pnpm run build
  cd ../terraform && terraform apply -target=terraform_data.netlify_deploy
  ```

## Outputs

- `api_url` — URL del backend en Vercel (`https://<vercel_project_name>.vercel.app`)
- `frontend_url` — `https://<netlify_site_name>.netlify.app`

## Notas

- El backend lee `ROCCA_DATABASE_URL` (PostgreSQL en prod; **siempre**
  PostgreSQL, no SQLite — en Vercel el filesystem es efímero).
- `ROCCA_CORS_ORIGINS`: inyectarlo como env var de Vercel con la URL de
  Netlify si el frontend hace fetch al backend desde otro origen.
- El frontend lee `VITE_API_BASE_URL` en build time; fijarlo manualmente en
  las variables de entorno de Netlify apuntando a
  `https://<vercel_project_name>.vercel.app`.
- Health check del backend: `GET /api/health`.
- Límites de Vercel con FastAPI (función serverless): sin tareas de fondo
  largas ni WebSockets; cold starts por `crear_app()`; límite de tamaño de
  bundle.
- State: no commitear `terraform.tfstate` ni `*.tfvars`. Para uso en equipo,
  usar un backend remoto (Terraform Cloud, S3).
