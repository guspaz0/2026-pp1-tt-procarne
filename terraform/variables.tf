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


variable "rocca_database_url" {
  description = "URL de PostgreSQL (Insforge, Render Postgres o Neon). Se inyecta como ROCCA_DATABASE_URL."
  type        = string
  sensitive   = true
  default     = ""
}

variable "insforge_url" {
  description = "URL del proyecto Insforge. Se inyecta como INSFORGE_URL."
  type        = string
}

variable "insforge_api_key" {
  description = "API Key del proyecto Insforge. Se inyecta como INSFORGE_API_KEY."
  type        = string
  sensitive   = true
}
