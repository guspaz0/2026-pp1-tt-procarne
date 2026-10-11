# ROCCA — Backend

API REST para el sistema de gestión de remitos cárnicos.

## Stack

| Componente   | Versión  |
|--------------|----------|
| Python       | 3.12+    |
| FastAPI      | ≥ 0.115  |
| SQLAlchemy   | ≥ 2.0    |
| Alembic      | ≥ 1.13   |
| Uvicorn      | ≥ 0.30   |

## Estructura

```
src/backend/
├── alembic.ini              # Configuración de Alembic
├── requirements.txt
├── app/
│   ├── __init__.py          # Ajusta sys.path para imports top-level
│   ├── main.py              # Punto de entrada (uvicorn app.main:app)
│   ├── app.py               # Clase RoccaApp + factory crear_app
│   ├── configs/
│   │   ├── db.py            # Base declarativa, engine, sesión
│   │   └── dao.py           # DAOs (SQLite / PostgreSQL)
│   └── modulos/
│       └── remitos_carnicos/
│           ├── operador/    # Entidad, DAO, servicio, controlador
│           ├── mercaderia/
│           └── remito/
└── migrations/
    ├── env.py               # Entorno de migraciones
    ├── script.py.mako       # Plantilla de migración
    └── versions/            # Migraciones generadas
```

## Base de datos embebida (Docker)

El proyecto incluye un PostgreSQL 16 en contenedor para desarrollo local.

### Comandos

```bash
cd src/backend

# Levantar Postgres
./scripts/db.sh up

# Aplicar migraciones
./scripts/db.sh migrate

# Ver estado
./scripts/db.sh status

# Detener (conserva datos)
./scripts/db.sh down

# Borrar todo y re-crear
./scripts/db.sh reset
```

### Variables de entorno

| Variable              | Default                          | Descripción                  |
|-----------------------|----------------------------------|------------------------------|
| `ROCCA_DATABASE_URL`  | `sqlite:///./rocca.db`           | URL de conexión a la BD      |

Cuando usás Postgres embebido:

```bash
export ROCCA_DATABASE_URL="postgresql+psycopg2://rocca:rocca@localhost:5432/rocca"
```

> **Nota:** El script `db.sh` ya exporta esta variable al ejecutar `migrate`.

## Levantar el servidor

### 1. Crear el entorno virtual

```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Levantar la base de datos

```bash
./scripts/db.sh up
./scripts/db.sh migrate
```

### 4. Ejecutar

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs interactivas: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Manejo de migraciones

Las migraciones se gestionan con **Alembic**. El `alembic.ini` está en la raíz de `src/backend` y las versiones se guardan en `migrations/versions/`.

### Comandos

```bash
cd src/backend

# Generar una migración nueva (autogenera a partir de los modelos ORM)
alembic revision --autogenerate -m "descripcion del cambio"

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar una migración específica
alembic upgrade <revision_id>

# Revertir la última migración
alembic downgrade -1

# Revertir a una revisión específica
alembic downgrade <revision_id>

# Ver el historial de migraciones
alembic history

# Ver el estado actual (aplicadas vs pendientes)
alembic current

# Generar SQL sin ejecutar (modo offline)
alembic upgrade head --sql > changes.sql
```

### Flujo típico

1. Modificar los modelos ORM en `app/modulos/.../entidad.py`.
2. Generar la migración:
   ```bash
   alembic revision --autogenerate -m "agregar campo X a remito"
   ```
3. Revisar el archivo generado en `migrations/versions/` (autogenerate puede omitir renames, datos, etc.).
4. Aplicar:
   ```bash
   alembic upgrade head
   ```
5. Commitar tanto los modelos como la migración.

### Nota

El `env.py` importa `configs.db.Base` y los módulos de `modulos/` para que Alembic detecte todos los modelos. Si agregás un módulo nuevo, asegurate de que sea importable desde `env.py` (o que se importe transitivamente).
