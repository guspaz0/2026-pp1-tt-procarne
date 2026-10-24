# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5"

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.3"
    }
  }
}

provider "render" {
  # RENDER_API_KEY (https://dashboard.render.com/api-keys)
  # RENDER_OWNER_ID (usr-... o tea-..., lo ves en la URL de tu perfil en el dashboard)
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}
