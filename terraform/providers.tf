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
  # El token se toma de var.vercel_api_token, que puede poblarse de dos formas:
  #   1. terraform.tfvars  →  vercel_api_token = "vercel_xxx..."
  #   2. Env var           →  export TF_VAR_vercel_api_token="vercel_xxx..."
  #    (Terraform auto-mapea TF_VAR_<nombre> → variable <nombre>)
  api_token = var.vercel_api_token
  # team = var.vercel_team_id   # solo si se despliega bajo un team
}

