-- =============================================================
-- ROCCA — Schema migration (PostgreSQL)
-- Drop old tables and recreate to match current ORM models.
-- Usage: psql $ROCCA_DATABASE_URL -f migrate_schema.sql
-- =============================================================

BEGIN;

-- ---------------------------------------------------------
-- 1. Drop old/changed tables (order matters for FKs)
-- ---------------------------------------------------------
DROP TABLE IF EXISTS operador_categorias CASCADE;
DROP TABLE IF EXISTS situaciones CASCADE;
DROP TABLE IF EXISTS personas CASCADE;
DROP TABLE IF EXISTS categorias_afip CASCADE;
DROP TABLE IF EXISTS actividades CASCADE;
DROP TABLE IF EXISTS mercaderias_genericas CASCADE;
DROP TABLE IF EXISTS operadores CASCADE;
DROP TABLE IF EXISTS rocca_operadores CASCADE;

-- ---------------------------------------------------------
-- 2. Recreate tables matching ORM models
-- ---------------------------------------------------------

-- Actividades ganaderas
CREATE TABLE IF NOT EXISTS actividades (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL
);

-- Catálogo de categorías AFIP por actividad
CREATE TABLE IF NOT EXISTS categorias_afip (
    id SERIAL PRIMARY KEY,
    actividad_id INTEGER NOT NULL REFERENCES actividades(id),
    codigo VARCHAR(10) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    UNIQUE (actividad_id, codigo)
);

-- Catálogo de situaciones (estado de inscripción)
CREATE TABLE IF NOT EXISTS situaciones (
    id SERIAL PRIMARY KEY,
    descripcion VARCHAR(40) NOT NULL UNIQUE
);

-- Personas (física o jurídica)
CREATE TABLE IF NOT EXISTS personas (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(2) NOT NULL CHECK (tipo IN ('PF', 'PJ')),
    tipo_documento VARCHAR(4) NOT NULL CHECK (tipo_documento IN ('DNI', 'CUIT')),
    identificador VARCHAR(13) NOT NULL UNIQUE,
    nombre VARCHAR(120),
    apellido VARCHAR(120),
    razon_social VARCHAR(255),
    domicilio VARCHAR(255),
    telefono VARCHAR(30),
    email VARCHAR(255),
    CONSTRAINT chk_identificador_longitud
        CHECK ((tipo_documento = 'DNI' AND LENGTH(identificador) = 8)
            OR (tipo_documento = 'CUIT' AND LENGTH(identificador) = 11))
);

-- Mercaderías genéricas
CREATE TABLE IF NOT EXISTS mercaderias_genericas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NOT NULL,
    unidad_medida VARCHAR(20),
    requiere_trazabilidad BOOLEAN NOT NULL DEFAULT FALSE,
    requiere_numero_tropa BOOLEAN NOT NULL DEFAULT FALSE
);

-- Operadores (solo referencia a persona + datos específicos)
CREATE TABLE IF NOT EXISTS operadores (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER NOT NULL UNIQUE REFERENCES personas(id),
    domicilio_fiscal VARCHAR(255)
);

-- Inscripción de un operador en una categoría de una actividad
CREATE TABLE IF NOT EXISTS operador_categorias (
    id SERIAL PRIMARY KEY,
    operador_id INTEGER NOT NULL REFERENCES operadores(id),
    actividad_id INTEGER REFERENCES actividades(id),
    categoria_id INTEGER NOT NULL REFERENCES categorias_afip(id),
    situacion_id INTEGER NOT NULL REFERENCES situaciones(id),
    desde_fecha VARCHAR(10),
    hasta_fecha VARCHAR(10)
);

-- Operadores ROCCA (registro provincial)
CREATE TABLE IF NOT EXISTS rocca_operadores (
    id SERIAL PRIMARY KEY,
    persona_id INTEGER REFERENCES personas(id),
    cuit VARCHAR(13) NOT NULL UNIQUE,
    razon_social VARCHAR(255) NOT NULL,
    tipo_operador VARCHAR(30),
    estado_registral VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    tipo_inscripcion VARCHAR(20) NOT NULL DEFAULT 'NACIONAL'
);

COMMIT;

-- Verificación
SELECT 'actividades' AS tabla, COUNT(*) FROM actividades
UNION ALL SELECT 'categorias_afip', COUNT(*) FROM categorias_afip
UNION ALL SELECT 'situaciones', COUNT(*) FROM situaciones
UNION ALL SELECT 'personas', COUNT(*) FROM personas
UNION ALL SELECT 'mercaderias_genericas', COUNT(*) FROM mercaderias_genericas
UNION ALL SELECT 'operadores', COUNT(*) FROM operadores
UNION ALL SELECT 'operador_categorias', COUNT(*) FROM operador_categorias
UNION ALL SELECT 'rocca_operadores', COUNT(*) FROM rocca_operadores;
