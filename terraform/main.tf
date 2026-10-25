# ---------------------------------------------------------------------------
# Backend — Render (FastAPI)
# ---------------------------------------------------------------------------

resource "render_web_service" "api" {
  name             = var.render_api_name
  plan             = "starter"
  region           = "frankfurt"
  root_directory   = "src/backend"
  start_command    = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  health_check_path = "/api/health"

  runtime_source = {
    native_runtime = {
      auto_deploy   = true
      branch        = var.github_branch
      build_command = "pip install -r requirements.txt"
      repo_url      = "https://github.com/${var.github_repo}"
      runtime       = "python"
    }
  }

  env_vars = {
    "ROCCA_DATABASE_URL" = { value = var.rocca_database_url },
    "ROCCA_CORS_ORIGINS" = { value = "https://${var.netlify_site_name}.netlify.app" },
  }
}

# ---------------------------------------------------------------------------
# Frontend — Netlify
# El site se crea una vez en el UI de Netlify.
# El provider gestiona build settings y env vars; el deploy se hace con netlify-cli.
# ---------------------------------------------------------------------------

resource "netlify_site_build_settings" "frontend" {
  site_id           = var.netlify_site_id
  build_command     = "cd src/frontend && pnpm install --frozen-lockfile && pnpm run build"
  publish_directory = "src/frontend/dist"
  production_branch = var.github_branch
}

resource "netlify_environment_variable" "vite_api_base_url" {
  site_id = var.netlify_site_id
  key     = "VITE_API_BASE_URL"

  values = [
    {
      context = "all"
      value   = render_web_service.api.url
    }
  ]
}

# Deploy del build local de Vite
resource "terraform_data" "netlify_deploy" {
  # Re-deploy cuando cambie cualquier archivo en dist/
  triggers_replace = [
    sha1(join("", [for f in fileset("${path.module}/../src/frontend/dist", "**") : filemd5("${path.module}/../src/frontend/dist/${f}")]))
  ]

  provisioner "local-exec" {
    command     = "npx netlify-cli deploy --dir=../src/frontend/dist --prod --site=${var.netlify_site_id}"
    working_dir = path.module
    environment = {
      NETLIFY_AUTH_TOKEN = var.netlify_token
    }
  }
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
output "api_url" {
  value = render_web_service.api.url
}

output "frontend_url" {
  value = "https://${var.netlify_site_name}.netlify.app"
}
