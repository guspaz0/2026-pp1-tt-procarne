# ROCCA — Control Cadena Cárnica SDE
# Compila el frontend y levanta backend (FastAPI) + frontend (Vite) en dev.
#
# Uso:
#   .\run.ps1            # build del frontend + backend :8000 + frontend :5173
#   .\run.ps1 -NoBuild   # salta el build del frontend
#
param(
    [switch]$NoBuild
)

$ErrorActionPreference = "Stop"

$ROOT = $PSScriptRoot
$BACKEND = Join-Path $ROOT "src\backend"
$FRONTEND = Join-Path $ROOT "src\frontend"

# URL de la base de datos
$env:ROCCA_DATABASE_URL = if ($env:ROCCA_DATABASE_URL) { $env:ROCCA_DATABASE_URL }
    else { "postgresql+psycopg://gusta:Gustavo10*@localhost:5432/rocca" }

# ------------------------------------------------------------------
# 0. Liberar puertos ocupados por procesos anteriores
# ------------------------------------------------------------------
foreach ($port in @(8000, 5173)) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conns) {
        $conns | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    }
}

# ------------------------------------------------------------------
# 1. Verificar PostgreSQL (debe estar corriendo en localhost:5432)
# ------------------------------------------------------------------
Write-Host "==> [1/4] Verificando PostgreSQL en localhost:5432..."
$pgOk = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("localhost", 5432)
        $tcp.Close()
        $pgOk = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $pgOk) {
    Write-Error "PostgreSQL no accesible en localhost:5432. Verificar que esté corriendo."
}
Write-Host "    PostgreSQL accesible en localhost:5432"

# ------------------------------------------------------------------
# 2. Build del frontend (emite en backend/app/static)
# ------------------------------------------------------------------
if (-not $NoBuild) {
    Write-Host "==> [2/4] Compilando frontend (Vite + Tailwind)..."
    Push-Location $FRONTEND
    try {
        if (-not (Test-Path "node_modules")) {
            pnpm install --ignore-workspace --silent
        }
        pnpm build
    } finally {
        Pop-Location
    }
} else {
    Write-Host "==> [2/4] Build del frontend omitido (-NoBuild)"
}

# ------------------------------------------------------------------
# 3. Backend FastAPI (uvicorn) en :8000
# ------------------------------------------------------------------
Write-Host "==> [3/4] Levantando backend FastAPI en http://localhost:8000 ..."

# Activar venv de Windows
$VENV_ACTIVATE = Join-Path $BACKEND ".venv\Scripts\Activate.ps1"
$VENV_BIN = Join-Path $BACKEND ".venv\Scripts"

$backendScript = @"
Set-Location '$BACKEND'
if (-not (Test-Path '$VENV_ACTIVATE')) {
    python -m venv .venv
}
. '$VENV_ACTIVATE'
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"@

$BACKEND_JOB = Start-Job -ScriptBlock ([scriptblock]::Create($backendScript))

# ------------------------------------------------------------------
# 4. Frontend Vite dev en :5173 (proxy /api -> :8000)
# ------------------------------------------------------------------
Write-Host "==> [4/4] Levantando frontend Vite en http://localhost:5173 ..."
$FRONTEND_JOB = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    pnpm dev
} -ArgumentList $FRONTEND

# ------------------------------------------------------------------
# Limpieza al salir (Ctrl+C)
# ------------------------------------------------------------------
Write-Host ""
Write-Host "  PostgreSQL: localhost:5432 (gusta/rocca)"
Write-Host "  Backend:    http://localhost:8000  (API + frontend compilado)"
Write-Host "  Frontend:   http://localhost:5173  (Vite dev, proxy /api -> :8000)"
Write-Host ""
Write-Host "  Ctrl+C para detener todo."
Write-Host ""

try {
    while (-not $BACKEND_JOB.HasExited -and -not $FRONTEND_JOB.HasExited) {
        Start-Sleep -Seconds 2
        Receive-Job -Job $BACKEND_JOB -Keep 2 -ErrorAction SilentlyContinue | Write-Host
        Receive-Job -Job $FRONTEND_JOB -Keep 2 -ErrorAction SilentlyContinue | Write-Host
    }
} finally {
    Write-Host ""
    Write-Host "Deteniendo procesos..."
    Stop-Job -Job $BACKEND_JOB -ErrorAction SilentlyContinue
    Stop-Job -Job $FRONTEND_JOB -ErrorAction SilentlyContinue
    Remove-Job -Job $BACKEND_JOB, $FRONTEND_JOB -Force -ErrorAction SilentlyContinue
}
