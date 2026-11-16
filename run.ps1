# ROCCA — Control Cadena Cárnica SDE
# Compila el frontend y levanta backend (FastAPI) + frontend (Vite) en dev.
#
# Uso:
#   .\run.ps1            # build del frontend + backend :8000 + frontend :5173
#   .\run.ps1 -NoBuild   # salta el build del frontend
#   .\run.ps1 -E2E       # SOLO backend :8000 con SQLite temporal (sin PG ni
#                        # frontend). Para que el fixture de Playwright o un
#                        # `pnpm dev` manual se conecten a un backend aislado.
#
param(
    [switch]$NoBuild,
    [switch]$E2E
)

$ErrorActionPreference = "Stop"

$ROOT = $PSScriptRoot
$BACKEND = Join-Path $ROOT "src\backend"
$FRONTEND = Join-Path $ROOT "src\frontend"

# ------------------------------------------------------------------
# Modo -E2E: solo backend en :8000 con un SQLite temporal limpio.
# Sin PostgreSQL, sin frontend, sin build. InsForge sigue siendo el IdP real.
# ------------------------------------------------------------------
if ($E2E) {
    $VENV_PY = Join-Path $BACKEND ".venv\Scripts\python.exe"
    if (-not (Test-Path $VENV_PY)) {
        Write-Error "Venv de Python no encontrado en $VENV_PY. Creadlo primero: python -m venv .venv"
    }

    # SQLite temporal; se borra al salir.
    $E2E_DB = Join-Path $env:TEMP "rocca-e2e-$(Get-Random).db"
    $env:ROCCA_DATABASE_URL = "sqlite:///$($E2E_DB -replace '\\','/')"

    Write-Host "==> [e2e] Levantando backend FastAPI en :8000 con SQLite temporal:"
    Write-Host "    $($env:ROCCA_DATABASE_URL)"
    Write-Host "    (sin PostgreSQL, sin frontend; InsForge sigue siendo el IdP real)"
    Write-Host ""

    Push-Location $BACKEND
    try {
        & $VENV_PY -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    } finally {
        Pop-Location
    }
    Remove-Item $E2E_DB -Force -ErrorAction SilentlyContinue
    exit 0
}

# URL de la base de datos
$env:ROCCA_DATABASE_URL = if ($env:ROCCA_DATABASE_URL) { $env:ROCCA_DATABASE_URL }
    else { "postgresql+psycopg://gusta:Gustavo10*@localhost:5432/rocca" }

# ------------------------------------------------------------------
# 0. Liberar puertos ocupados por procesos anteriores
# ------------------------------------------------------------------
foreach ($port in @(8001, 5173)) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conns) {
        $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $pids) {
            Write-Host "    Matando proceso $procId en puerto $port..."
            taskkill /F /PID $procId 2>$null | Out-Null
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
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
# 3. Backend FastAPI (uvicorn) en :8001
# ------------------------------------------------------------------
Write-Host "==> [3/4] Levantando backend FastAPI en http://localhost:8001 ..."

# Activar venv de Windows
$VENV_ACTIVATE = Join-Path $BACKEND ".venv\Scripts\Activate.ps1"
$VENV_BIN = Join-Path $BACKEND ".venv\Scripts"

$backendScript = @"
Set-Location '$BACKEND'
if (-not (Test-Path '$VENV_ACTIVATE')) {
    python -m venv .venv
}
. '$VENV_ACTIVATE'
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
"@

$BACKEND_JOB = Start-Job -ScriptBlock ([scriptblock]::Create($backendScript))

# ------------------------------------------------------------------
# 4. Frontend Vite dev en :5173 (proxy /api -> :8001)
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
Write-Host "  Backend:    http://localhost:8001  (API + frontend compilado)"
Write-Host "  Frontend:   http://localhost:5173  (Vite dev, proxy /api -> :8001)"
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
