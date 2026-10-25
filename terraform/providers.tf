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
    netlify = {
      source  = "netlify/netlify"
      version = "~> 0.4"
    }
  }
}

provider "render" {
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}

provider "netlify" {
  token = var.netlify_token
}
