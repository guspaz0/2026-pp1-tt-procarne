# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

# --- Backend (Render) ---

variable "render_api_key" {
  description = "API key de Render (https://dashboard.render.com/api-keys)"
  type        = string
  sensitive   = true
}

variable "render_owner_id" {
  description = "Owner ID de Render (usr-... o tea-...). Lo ves en la URL de tu perfil/equipo en el dashboard."
  type        = string
}

variable "github_repo" {
  description = "Repo GitHub del monorepo (owner/name)"
  type        = string
  default     = "guspaz0/2026-pp1-tt-procarne"
}

variable "github_branch" {
  description = "Rama a desplegar"
  type        = string
  default     = "backend"
}

variable "render_api_name" {
  description = "Nombre del web service en Render"
  type        = string
  default     = "rocca-api"
}

variable "rocca_database_url" {
  description = "URL de PostgreSQL (Render Postgres o Neon). Se inyecta como ROCCA_DATABASE_URL."
  type        = string
  sensitive   = true
}

# --- Frontend (Netlify) ---

variable "netlify_token" {
  description = "Personal access token de Netlify (https://app.netlify.com/user/applications#personal-access-tokens)"
  type        = string
  sensitive   = true
}

variable "netlify_site_id" {
  description = "ID del site en Netlify (lo ves en la URL del site en el dashboard)"
  type        = string
}

variable "netlify_site_name" {
  description = "Nombre del site en Netlify"
  type        = string
  default     = "procarne-sde"
}
