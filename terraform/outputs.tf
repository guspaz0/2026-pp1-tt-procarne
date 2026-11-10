# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "app_url" {
  description = "Endpoint URL de la API FastAPI desplegada en Vercel (ej. https://procarne.vercel.app)."
  value       = "https://${vercel_project.api.name}.vercel.app"
}

output "deployment_url" {
  description = "URL del deployment de producción actual (cambia en cada apply)."
  value       = vercel_deployment.api.url
}

output "deployment_id" {
  description = "ID del deployment de producción actual."
  value       = vercel_deployment.api.id
}
