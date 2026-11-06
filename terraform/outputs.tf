# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "app_url" {
  description = "Endpoint URL de la API FastAPI desplegada en Vercel (ej. https://procarne.vercel.app)."
  value = "https://${vercel_project.api.name}.vercel.app"
}

output "git_repository" {
  description = "Repositorio GitHub conectado al proyecto Vercel (ej. guspaz0/2026-pp1-tt-procarne)."
  value = vercel_project.api.git_repository
}
