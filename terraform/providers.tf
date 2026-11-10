# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5"

  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 5.0"
    }
  }
}

provider "vercel" {
  # Lee VERCEL_API_TOKEN del entorno (o vercel_token si se define abajo)
  api_token = var.vercel_api_token
  # El proyecto "procarne" vive dentro de un team. Sin `team` el provider
  # resuelve en el scope personal del token y la API responde 403 Forbidden.
  team = var.vercel_team_id
}
