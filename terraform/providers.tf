# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5"

  required_providers {
    vercel = {
      source  = "vercel/vercel"
      # --- fijar a la última versión del registry, ej. version = "~> 0.x"
    }
  }
}

provider "vercel" {
  # Lee VERCEL_API_TOKEN del entorno (o vercel_token si se define abajo)
  api_token = var.vercel_api_token
  # team = var.vercel_team_id   # solo si se despliega bajo un team
}

