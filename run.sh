#!/usr/bin/env bash
#
# ROCCA — Control Cadena Cárnica SDE
# Compila el frontend y levanta PostgreSQL + backend (FastAPI) + frontend (Vite) en dev.
#
# Uso:
#   ./run.sh            # build del frontend + postgres + backend :8000 + frontend :5173
#   ./run.sh --no-build # salta el build del frontend
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/src/backend"
FRONTEND="$ROOT/src/frontend"

SKIP_BUILD=0
[[ "${1:-}" == "--no-build" ]] && SKIP_BUILD=1

# URL de la base de datos (PostgreSQL local vía Docker)
export ROCCA_DATABASE_URL="${ROCCA_DATABASE_URL:-postgresql+psycopg://gusta:Gustavo10*@localhost:5432/rocca}"

# ------------------------------------------------------------------
# 0. Liberar puertos ocupados por procesos anteriores
# ------------------------------------------------------------------
_kill_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -ti:"$port" 2>/dev/null | xargs kill -9 2>/dev/null || true
  elif command -v fuser >/dev/null 2>&1; then
    fuser -k "$port"/tcp 2>/dev/null || true
  elif command -v ss >/dev/null 2>&1; then
    local pids
    pids=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oP 'pid=\K[0-9]+' | sort -u)
    [[ -n "$pids" ]] && kill -9 $pids 2>/dev/null || true
  fi
}
_kill_port 8000
_kill_port 5173

# ------------------------------------------------------------------
# 1. Verificar PostgreSQL (debe estar corriendo en localhost:5432)
# ------------------------------------------------------------------
echo "==> [1/4] Verificando PostgreSQL en localhost:5432..."
for i in $(seq 1 10); do
  if python3 -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('localhost',5432)); s.close()" 2>/dev/null; then
    break
  fi
  sleep 1
done
echo "    PostgreSQL accesible en localhost:5432"

# ------------------------------------------------------------------
# 2. Build del frontend (emite en backend/app/static)
# ------------------------------------------------------------------
if [[ "$SKIP_BUILD" -eq 0 ]]; then
  echo "==> [2/4] Compilando frontend (Vite + Tailwind)..."
  (
    cd "$FRONTEND"
    if [[ ! -d node_modules || package.json -nt node_modules || pnpm-lock.yaml -nt node_modules/.pnpm ]]; then
      pnpm install --ignore-workspace --silent
    fi
    pnpm build
  )
else
  echo "==> [2/4] Build del frontend omitido (--no-build)"
fi

# ------------------------------------------------------------------
# 3. Backend FastAPI (uvicorn) en :8000
# ------------------------------------------------------------------
echo "==> [3/4] Levantando backend FastAPI en http://localhost:8000 ..."
(
  cd "$BACKEND"
  if [[ ! -d ".venv" ]]; then
    python3 -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    pip install -q -r requirements.txt
  else
    # shellcheck disable=SC1091
    source .venv/bin/activate
  fi
  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
) &
BACKEND_PID=$!

# ------------------------------------------------------------------
# 4. Frontend Vite dev en :5173 (proxy /api -> :8000)
# ------------------------------------------------------------------
echo "==> [4/4] Levantando frontend Vite en http://localhost:5173 ..."
(
  cd "$FRONTEND"
  pnpm dev
) &
FRONTEND_PID=$!

# ------------------------------------------------------------------
# Limpieza al salir (Ctrl+C)
# ------------------------------------------------------------------
cleanup() {
  echo ""
  echo "Deteniendo procesos..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo "  PostgreSQL: localhost:5432 (gusta/rocca)"
echo "  Backend:    http://localhost:8000  (API + frontend compilado)"
echo "  Frontend:   http://localhost:5173  (Vite dev, proxy /api -> :8000)"
echo ""
echo "  Ctrl+C para detener todo."
echo ""

wait
