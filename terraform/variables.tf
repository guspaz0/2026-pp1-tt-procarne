# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "vercel_api_token" {
  description = "API token de Vercel (https://vercel.com/account/tokens)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "vercel_project_name" {
  description = "Nombre del proyecto en Vercel (define la URL: <nombre>.vercel.app)"
  type        = string
  default     = "procarne"
}

variable "vercel_team_id" {
  description = "ID del team de Vercel que posee el proyecto. Sin este valor el provider no resuelve el proyecto (403 Forbidden)."
  type        = string
  default     = "team_jBuR0GcDPltyl5R6JqLOsSPO"
}

variable "rocca_database_url" {
  description = "URL de PostgreSQL (Insforge, Render Postgres o Neon). Se inyecta como ROCCA_DATABASE_URL."
  type        = string
  sensitive   = true
  default     = ""
}
