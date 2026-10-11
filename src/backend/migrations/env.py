"""Entorno de migraciones Alembic para ROCCA.

Se ejecuta desde el directorio ``src/backend``::

    alembic upgrade head
    alembic revision --autogenerate -m "descripcion"
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Asegurar que el directorio ``app`` esté en sys.path para poder importar
# ``configs`` y ``modulos`` como paquetes top-level.
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_APP_DIR = str(_BACKEND_DIR / "app")
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

# Importar Base y todos los modelos para que autogenerate los detecte.
from configs.db import Base  # noqa: E402
import modulos.remitos_carnicos.remitos_carnicos  # noqa: F401, E402  (registra modelos)

# ---------------------------------------------------------------------------
# Configuración de Alembic
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# URL de la base de datos (misma variable que usa la aplicación)
DATABASE_URL = os.environ.get(
    "ROCCA_DATABASE_URL",
    "sqlite:///./rocca.db",
)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones en modo offline (solo generar SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecutar migraciones en modo online (conexión real)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
