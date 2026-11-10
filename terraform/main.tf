# ---------------------------------------------------------------------------
# Deploy unificado — Vercel (FastAPI + React estático)
# El frontend se builda localmente (pnpm build) y se emite en
# src/backend/app/static/. Terraform sube todo src/backend a Vercel.
# ---------------------------------------------------------------------------

resource "vercel_project" "api" {
  name = var.vercel_project_name
  framework = "fastapi"

  root_directory = "src/backend"
}

data "vercel_project_directory" "app" {
   path = "${path.module}/../src/backend"
}

resource "vercel_deployment" "api" {
  project_id  = vercel_project.api.id
  files       = data.vercel_project_directory.app.files
  production  = true

  depends_on = [
    vercel_project_environment_variable.database_url,
    vercel_project_environment_variable.insforge_url,
    vercel_project_environment_variable.insforge_api_key
  ]
}

# --- Variables de entorno (se inyectan en la app FastAPI) ---
resource "vercel_project_environment_variable" "database_url" {
  project_id = vercel_project.api.id
  key        = "ROCCA_DATABASE_URL"
  value      = var.rocca_database_url
  target     = ["production", "preview"]
  sensitive  = true
}

resource "vercel_project_environment_variable" "insforge_url" {
  project_id = vercel_project.api.id
  key        = "INSFORGE_URL"
  value      = var.insforge_url
  target     = ["production", "preview"]
  sensitive  = false
}

resource "vercel_project_environment_variable" "insforge_api_key" {
  project_id = vercel_project.api.id
  key        = "INSFORGE_API_KEY"
  value      = var.insforge_api_key
  target     = ["production", "preview"]
  sensitive  = true
}
