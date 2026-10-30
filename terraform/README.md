# ROCCA — Terraform (Vercel + Netlify)

Deploy del monorepo:

- **Backend** (FastAPI, `src/backend`) → **Vercel** (función serverless Python).
- **Frontend** (Vite/React, `src/frontend`) → **Netlify** site (deploy vía `netlify-cli`).

> El backend anterior en **Render** quedó descomentado en `main.tf` y
> `variables.tf` por si hace falta volver.

## Estructura

```
terraform/
├── main.tf               # Recursos: vercel_project.api, env vars, vercel_deployment.api, terraform_data.netlify_deploy, outputs
├── providers.tf          # required_providers + provider vercel
├── variables.tf          # Variables (secciones backend y frontend)
└── README.md
```

## Requisitos

- Terraform >= 1.5 (cómo instalarlo: [Instalar Terraform](#instalar-terraform))
- `netlify-cli` instalado (`npm i -g netlify-cli`)
- API token de Vercel: <https://vercel.com/account/tokens>
- Personal access token de Netlify: <https://app.netlify.com/user/applications#personal-access-tokens>
- Site de Netlify creado manualmente en el dashboard (el provider no soporta creación de sites)

## Variables

| Variable              | Sensitive | Descripción                                              | Default                    |
|-----------------------|-----------|----------------------------------------------------------|----------------------------|
| `vercel_api_token`    | sí        | API token de Vercel                                      | —                          |
| `vercel_project_name` | no        | Nombre del proyecto en Vercel (define la URL)            | `rocca-api`                |
| `rocca_database_url`  | sí        | URL de PostgreSQL (Insforge / Neon) — **no SQLite**      | —                          |
| `netlify_token`       | sí        | Personal access token de Netlify                         | —                          |
| `netlify_site_id`     | no        | ID del site en Netlify (lo ves en la URL del dashboard)   | —                          |
| `netlify_site_name`   | no        | Nombre del site en Netlify                               | `procarne-sde`             |

## Instalar Terraform

Descargas oficiales y checksums: <https://developer.hashicorp.com/terraform/install>

### macOS

Con [Homebrew](https://brew.sh):

```bash
brew install hashicorp/tap/terraform
```

Alternativa: descargar el `.zip` para macOS (arm64 o amd64) desde la página de
install, descomprimirlo y mover el binario a un directorio en el `PATH`:

```bash
# ejemplo para Apple Silicon (arm64); usar la versión y el hash actuales del sitio
curl -O https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_darwin_arm64.zip
unzip terraform_1.9.8_darwin_arm64.zip
sudo mv terraform /usr/local/bin/
```

### Linux

Con el repositorio oficial de HashiCorp (Debian/Ubuntu):

```bash
# 1. Agregar la clave GPG y el repositorio (ajustar la versión de Terraform y la de tu distro)
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

Alternativa (cualquier distro): descargar el `.zip` de la página de install,
descomprimirlo y mover el binario a un directorio en el `PATH`:

```bash
# ejemplo para amd64; usar la versión y el hash actuales del sitio
curl -O https://releases.hashicorp.com/terraform/1.9.8/terraform_1.9.8_linux_amd64.zip
unzip terraform_1.9.8_darwin_arm64.zip
sudo mv terraform /usr/local/bin/
```

### Windows

Con [WinGet](https://github.com/microsoft/winget-cli) (incluido en Windows 10/11 recientes):

```powershell
winget install HashiCorp.Terraform
```

Alternativas:

- Con [Chocolatey](https://chocolatey.org): `choco install terraform`
- Con [Scoop](https://scoop.sh): `scoop install terraform`
- Manual: descargar el `.zip` para Windows (amd64) desde la página de
  install, descomprimirlo y agregar la carpeta al `PATH` de sistema
  (Configuración → Sistema → Sobre → Información del sistema → Variables de
  entorno).

### Verificar la instalación

```bash
terraform version
# Terraform v1.9.x
```

## Uso

```bash
cd terraform
terraform init

# Opción A: variables en línea
terraform plan \
  -var vercel_api_token="hcm_..." \
  -var netlify_token="nfp_..." \
  -var netlify_site_id="abc123-..." \
  -var rocca_database_url="postgresql://user:pass@host:5432/rocca"

# Opción B: archivo local terraform.tfvars (no commitear; ver terraform.tfvars.example)
terraform plan
terraform apply
```

Para re-deployar el frontend después de un build:

```bash
cd ../src/frontend && pnpm run build
cd ../terraform && terraform apply -target=terraform_data.netlify_deploy
```

## Outputs

- `api_url` — URL del backend en Vercel (`https://<vercel_project_name>.vercel.app`)
- `frontend_url` — `https://<netlify_site_name>.netlify.app`

## Notas

- El backend lee `ROCCA_DATABASE_URL` (PostgreSQL en prod) y
  `ROCCA_CORS_ORIGINS` (origen permitido para CORS; Terraform lo inyecta con
  la URL de Netlify).
- **Límites de Vercel con FastAPI** (función serverless):
  - Sin tareas de fondo largas ni WebSockets.
  - **Cold starts**: `crear_app()` crea el engine de SQLAlchemy y verifica
    tablas en cada arranque → la primera petición es más lenta.
  - **`ROCCA_DATABASE_URL` SIEMPRE debe ser PostgreSQL.** Si no se define,
    el código cae a `sqlite:///./rocca.db`, que en el filesystem efímero de
    Vercel se pierde entre peticiones.
  - Límite de tamaño de bundle de la función.
- Health check del backend: `GET /api/health` (ya no se configura en
  Terraform; verificar manualmente contra la URL de Vercel).
- El entrypoint `app/main.py` expone `app` a nivel de módulo; Vercel lo
  detecta solo (`framework = "fastapi"`). Si la versión del provider
  rechaza `framework`, usar `null` en lugar del valor.
- El frontend lee `VITE_API_BASE_URL` en build time; se fija manualmente en
  las variables de entorno de Netlify (ahora debe apuntar a
  `https://<vercel_project_name>.vercel.app`).
- Redeploys: `vercel_deployment` crea un deployment nuevo cuando cambia el
  hash de los archivos; editar código y correr `terraform apply` re-despliega.
- Alternative git-based: si se prefiere que Vercel despliegue en cada push,
  quitar `vercel_deployment` y agregar a `vercel_project.api`:

  ```hcl
  git_repository = {
    type = "github"
    repo = "guspaz0/2026-pp1-tt-procarne"
  }
  ```

  (Terraform solo manejaría proyecto y env vars.)
- State: no commitear `terraform.tfstate` ni `*.tfvars`. Para uso en equipo,
  usar un backend remoto (Terraform Cloud, S3).
