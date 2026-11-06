# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "vercel_api_token" {
  description = "API token de Vercel (https://vercel.com/account/tokens). Alternativa: exportar VERCEL_API_TOKEN."
  type        = string
  sensitive   = true
  default     = ""
}

variable "vercel_project_name" {
  description = "Nombre del proyecto en Vercel (define la URL: <nombre>.vercel.app)"
  type        = string
  default     = "procarne"
}

variable "github_repo" {
  description = "Repositorio GitHub en formato owner/name (ej. guspaz0/2026-pp1-tt-procarne)"
  type        = string
  default     = "guspaz0/2026-pp1-tt-procarne"
}

variable "rocca_database_url" {
  description = "URL de PostgreSQL (Insforge, Render Postgres o Neon). Se inyecta como ROCCA_DATABASE_URL."
  type        = string
  sensitive   = true
}
