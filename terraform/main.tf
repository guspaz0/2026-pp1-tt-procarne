# ---------------------------------------------------------------------------
# Deploy — Vercel (FastAPI) conectado a GitHub: redeploy automático por push
# ---------------------------------------------------------------------------

resource "vercel_project" "api" {
  name = var.vercel_project_name

  # Carpeta raíz dentro del repositorio (Vercel instala dependencias y builda).
  root_directory = "src/backend"

  # Conecta el proyecto a GitHub: cada push genera un deployment
  # automático (main → producción, demás branches → preview).
  # Requiere que la integración GitHub de Vercel tenga acceso al repo
  # (GitHub → Settings → Connections → Applications → Vercel → All repos).
  git_repository = {
    type = "github"
    repo = var.github_repo
  }
}

resource "vercel_project_environment_variable" "database_url" {
  project_id = vercel_project.api.id
  key        = "ROCCA_DATABASE_URL"
  value      = var.rocca_database_url
  target     = ["production", "preview"]
  sensitive  = true
}
