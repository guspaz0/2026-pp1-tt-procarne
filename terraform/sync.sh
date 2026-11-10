#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# sync.sh — regenera deploy/backend: una copia limpia de src/backend para
# desplegar en Vercel SIN conexión a GitHub.
#
# Excluye el entorno virtual local (.venv), cachés de Python y el SQLite de
# desarrollo. Vercel instala las dependencias por sí mismo a partir de
# requirements.txt.
#
# Uso:  ./sync.sh   (desde la carpeta terraform/)
# ---------------------------------------------------------------------------
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/../src/backend"
DEST="$HERE/../deploy/backend"

echo ">> Copiando $SRC -> $DEST (excluyendo .venv, __pycache__, .pytest_cache, *.db)"

rm -rf "$DEST"
mkdir -p "$DEST"

# rsync es la forma más fiable de copiar con exclusiones.
rsync -a \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '*.db' \
  --exclude '.git' \
  "$SRC"/ "$DEST"/

# Resumen
COUNT="$(find "$DEST" -type f | wc -l | tr -d ' ')"
SIZE="$(du -sh "$DEST" | cut -f1)"
echo ">> Listo: $COUNT archivos, $SIZE"
echo ">> Ahora ejecuta: terraform apply"
