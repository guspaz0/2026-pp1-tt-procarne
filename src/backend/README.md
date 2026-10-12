# ROCCA — Backend

API REST para el sistema de gestión de remitos electrónicos cárnicos, con un
módulo genérico de datos compartidos (personas y mercaderías) que sirve de
base a los módulos de negocio.

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
├── pytest.ini               # Configuración de pytest
├── app/
│   ├── __init__.py          # Ajusta sys.path para imports top-level
│   ├── main.py              # Punto de entrada (uvicorn app.main:app)
│   ├── app.py               # Clase RoccaApp + factory crear_app
│   ├── configs/
│   │   ├── db.py            # Base declarativa, engine, sesión
│   │   └── dao.py           # DAOs (SQLite / PostgreSQL)
│   └── modulos/
│       ├── genericos/       # Entidades transversales compartidas
│       │   ├── base.py      # Entidad (ABC) con id UUID
│       │   ├── enums.py     # TipoPersona (FISICA / JURIDICA)
│       │   ├── persona/     # Persona, PersonaFisica, PersonaJuridica + DAO/servicio
│       │   └── mercaderia/  # Mercaderia (entidad única) + DAO/servicio
│       └── remitos_carnicos/
│           ├── operador/    # Operador (extiende PersonaJuridica), categorías AFIP
│           └── remito/      # Remito electrónico y renglones (mercadería de genéricos)
├── migrations/
│   ├── env.py               # Entorno de migraciones
│   ├── script.py.mako       # Plantilla de migración
│   ├── seed_categorias_afip.sql
│   ├── seed_mercaderias.sql         # → mercaderias_genericas
│   ├── seed_operadores.sql          # → personas (jurídicas, bovinos)
│   ├── seed_operadores_porcinos.sql # → personas (jurídicas, porcinos)
│   └── versions/            # Migraciones generadas
└── tests/
    ├── conftest.py          # Prepara sys.path para importar `app`
    ├── fixtures.py          # Fixtures compartidas (db_engine, db_dao, api_client)
    └── modulos/
        └── remitos_carnicos/
```

## Modelo de dominio

El dominio se organiza en dos capas:

- **`modulos/genericos`** — entidades transversales reutilizables por
  cualquier módulo de negocio:
  - `Persona` (abstracta) → `PersonaFisica` (DNI + CUIT opcional, p. ej.
    monotributistas) y `PersonaJuridica` (identificada únicamente por CUIT).
  - `Mercaderia` (entidad única y concreta): código, descripción, unidad
    de medida, trazabilidad y requerimiento de N° de tropa.
- **`modulos/remitos_carnicos`** — entidades y servicios del sector F
  (cadena cárnica). `Operador` extiende `PersonaJuridica` y cumple los
  roles de titular, depositario, destinatario o transportista. El remito
  referencia la mercadería del catálogo genérico.

En la base de datos, las tablas se separan por módulo:

| Tabla                   | Módulo          | Descripción                              |
|-------------------------|-----------------|------------------------------------------|
| `personas`              | genericos       | Personas físicas y jurídicas             |
| `mercaderias_genericas` | genericos       | Catálogo único de mercaderías               |
| `operadores`            | remitos_carnicos| Operadores del padrón AFIP (cadena cárnica) |
| `remitos_carnicos`      | remitos_carnicos| Remitos electrónicos                     |
| `renglones_remito`      | remitos_carnicos| Renglones de mercadería por remito       |
| `actividades` / `categorias_afip` / `operador_categorias` | remitos_carnicos | Categorías AFIP |

## Base de datos

El proyecto usa **SQLite** por defecto (`sqlite:///./rocca.db`) y soporta
**PostgreSQL** para producción mediante la variable de entorno
`ROCCA_DATABASE_URL`.

| Variable             | Default                | Descripción               |
|----------------------|------------------------|---------------------------|
| `ROCCA_DATABASE_URL` | `sqlite:///./rocca.db` | URL de conexión a la BD    |

Para usar PostgreSQL:

```bash
export ROCCA_DATABASE_URL="postgresql+psycopg2://rocca:rocca@localhost:5432/rocca"
```

## Levantar el servidor

### 1. Crear el entorno virtual

```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones (crea el esquema + carga seeds)

```bash
alembic upgrade head
```

La migración inicial (`10e08db1c14d`) crea todas las tablas y carga los
archivos de seed:

- `seed_categorias_afip.sql` — actividades y categorías AFIP
- `seed_mercaderias.sql` — 327 códigos de la tabla AFIP → `mercaderias_genericas`
- `seed_operadores.sql` — 72.943 personas jurídicas (bovinos)
- `seed_operadores_porcinos.sql` — 3.166 personas jurídicas (porcinos)

### 4. Ejecutar

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs interactivas: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Manejo de migraciones

Las migraciones se gestionan con **Alembic**. El `alembic.ini` está en la
raíz de `src/backend` y las versiones se guardan en `migrations/versions/`.

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

1. Modificar los modelos ORM en `app/modulos/.../dao.py`.
2. Generar la migración:
   ```bash
   alembic revision --autogenerate -m "agregar campo X a remito"
   ```
3. Revisar el archivo generado en `migrations/versions/` (autogenerate puede
   omitir renames, datos, etc.).
4. Aplicar:
   ```bash
   alembic upgrade head
   ```
5. Commitar tanto los modelos como la migración.

### Nota

El `env.py` importa `configs.db.Base` y los módulos de `modulos/` para que
Alembic detecte todos los modelos. Si agregás un módulo nuevo, asegurate de
que sea importable desde `env.py` (o que se importe transitivamente).

## Tests

La suite de tests usa **pytest** con una base de datos SQLite en memoria por
test (fixtures compartidas en `tests/fixtures.py`).

```bash
cd src/backend

# Ejecutar toda la suite
pytest

# Ejecutar un módulo específico
pytest tests/modulos/remitos_carnicos

# Ejecutar un archivo específico
pytest tests/modulos/remitos_carnicos/test_remitos.py -v
```

Las fixtures principales:

| Fixture             | Descripción                                          |
|---------------------|------------------------------------------------------|
| `db_engine`         | Motor SQLite en memoria con todas las tablas creadas  |
| `db_session_factory`| Fábrica de sesiones vinculada al motor en memoria     |
| `db_dao`            | DAO de base de datos (SQLite) para inyección en módulos |
| `api_client`        | Cliente HTTP de FastAPI con la BD en memoria inyectada |

## Convenciones

- **Idioma**: código y docstrings en español.
- **Arquitectura**: SOLID + Dependency Injection (los servicios reciben DAOs
  por inyección; los DAOs reciben la fábrica de sesiones).
- **Por subpaquete de entidad**: `entidad.py` (dominio), `dao.py` (ORM),
  `schema.py` (Pydantic), `servicio.py` (negocio), `controlador.py` (router).
- **Herencia de dominio**: las entidades específicas de un módulo heredan de
  las entidades genéricas de `modulos/genericos`, no de las de otros módulos
  de negocio.
- **Resolución de relaciones**: las `relationship()` usan el path completo
  del módulo (p. ej. `modulos.genericos.mercaderia.dao.Mercaderia`) para
  evitar ambigüedad entre clases de distintos módulos.
