# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5"

  required_providers {
    vercel = {
      source  = "vercel/vercel"
      #version = "~> 5.0"
    }
  }
}

provider "vercel" {
  api_token = var.vercel_api_token
}
