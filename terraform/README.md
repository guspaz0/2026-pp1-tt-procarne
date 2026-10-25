# ROCCA — Terraform (Render + Netlify)

Deploy del monorepo:

- **Backend** (FastAPI, `src/backend`) → **Render** web service.
- **Frontend** (Vite/React, `src/frontend`) → **Netlify** site (deploy vía `netlify-cli`).

## Estructura

```
terraform/
├── main.tf               # Recursos: render_web_service.api + terraform_data.netlify_deploy, outputs
├── providers.tf          # required_providers + provider render
├── variables.tf          # Variables (secciones backend y frontend)
└── README.md
```

## Requisitos

- Terraform >= 1.5 (cómo instalarlo: [Instalar Terraform](#instalar-terraform))
- `netlify-cli` instalado (`npm i -g netlify-cli`)
- API key de Render: <https://dashboard.render.com/api-keys>
- Owner ID de Render (lo ves en la URL de tu perfil/equipo en el dashboard)
- Personal access token de Netlify: <https://app.netlify.com/user/applications#personal-access-tokens>
- Site de Netlify creado manualmente en el dashboard (el provider no soporta creación de sites)

## Variables

| Variable             | Sensitive | Descripción                                              | Default                    |
|----------------------|-----------|----------------------------------------------------------|----------------------------|
| `render_api_key`     | sí        | API key de Render                                        | —                          |
| `render_owner_id`    | no        | Owner ID (`usr-...` o `tea-...`)                         | —                          |
| `github_repo`        | no        | `owner/name` del monorepo en GitHub                      | `guspaz0/2026-pp1-tt-procarne` |
| `github_branch`      | no        | Rama a desplegar                                         | `main`                     |
| `render_api_name`    | no        | Nombre del web service en Render                         | `rocca-api`                |
| `rocca_database_url` | sí        | URL de PostgreSQL (Render Postgres / Neon)                | —                          |
| `netlify_token`      | sí        | Personal access token de Netlify                         | —                          |
| `netlify_site_id`    | no        | ID del site en Netlify (lo ves en la URL del dashboard)   | —                          |
| `netlify_site_name`  | no        | Nombre del site en Netlify                               | `rocca`                    |

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
unzip terraform_1.9.8_linux_amd64.zip
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
  -var render_api_key="rnd_..." \
  -var render_owner_id="usr-..." \
  -var netlify_token="nfp_..." \
  -var netlify_site_id="abc123-..." \
  -var rocca_database_url="postgresql://user:pass@host:5432/rocca"

# Opción B: archivo local terraform.tfvars (no commitear)
terraform plan
terraform apply
```

Para re-deployar el frontend después de un build:

```bash
cd ../src/frontend && pnpm run build
cd ../terraform && terraform apply -target=terraform_data.netlify_deploy
```

## Outputs

- `api_url` — URL del backend en Render
- `frontend_url` — `https://<netlify_site_name>.netlify.app`

## Notas

- El backend lee `ROCCA_DATABASE_URL` (PostgreSQL en prod) y
  `ROCCA_CORS_ORIGINS` (origen permitido para CORS; Terraform lo inyecta con
  la URL de Netlify).
- El frontend lee `VITE_API_BASE_URL` en build time; se fija manualmente en
  las variables de entorno de Netlify.
- Health check del backend: `GET /api/health` (configurado en Render).
- El backend se detecta como Python por `requirements.txt` en
  `src/backend`; el start command es
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
