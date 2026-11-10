#!/bin/bash
# Script para aplicar migraciones a la base de datos de producción (Insforge)
# Uso: ./scripts/apply_migrations.sh
# Requiere: ROCCA_DATABASE_URL en el entorno

set -e

# Verificar que ROCCA_DATABASE_URL esté definido
if [ -z "$ROCCA_DATABASE_URL" ]; then
    echo "Error: ROCCA_DATABASE_URL no está definido"
    echo "Ejemplo: export ROCCA_DATABASE_URL='postgresql://user:pass@host:5432/db'"
    exit 1
fi

# Verificar que sea PostgreSQL
if [[ "$ROCCA_DATABASE_URL" != postgresql* ]]; then
    echo "Error: ROCCA_DATABASE_URL no apunta a PostgreSQL"
    exit 1
fi

# Activar venv
source .venv/bin/activate

# Ejecutar migraciones
echo "Aplicando migraciones a la base de datos de producción..."
alembic upgrade head

echo "Migraciones aplicadas correctamente."
