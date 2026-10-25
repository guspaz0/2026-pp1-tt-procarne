-- =============================================================
-- ROCCA — Schema migration (PostgreSQL)
-- Auto-generated from ORM models (Base.metadata)
-- Usage: psql $ROCCA_DATABASE_URL -f migrate_schema.sql
-- =============================================================

BEGIN;

DROP TABLE IF EXISTS renglones_remito CASCADE;
DROP TABLE IF EXISTS remitos_carnicos CASCADE;
DROP TABLE IF EXISTS rocca_inscripciones CASCADE;
DROP TABLE IF EXISTS rocca_habilitaciones CASCADE;
DROP TABLE IF EXISTS rocca_domicilios_operativos CASCADE;
DROP TABLE IF EXISTS fiscalizacion_sanciones CASCADE;
DROP TABLE IF EXISTS fiscalizacion_infracciones CASCADE;
DROP TABLE IF EXISTS fiscalizacion_decomisos CASCADE;
DROP TABLE IF EXISTS fiscalizacion_actas CASCADE;
DROP TABLE IF EXISTS fiscalizacion_reincidencias CASCADE;
DROP TABLE IF EXISTS fiscalizacion_inspecciones CASCADE;
DROP TABLE IF EXISTS operador_categorias CASCADE;
DROP TABLE IF EXISTS operador_actividades CASCADE;
DROP TABLE IF EXISTS rocca_operadores CASCADE;
DROP TABLE IF EXISTS operadores CASCADE;
DROP TABLE IF EXISTS categorias_afip CASCADE;
DROP TABLE IF EXISTS registros_trazabilidad CASCADE;
DROP TABLE IF EXISTS situaciones CASCADE;
DROP TABLE IF EXISTS personas CASCADE;
DROP TABLE IF EXISTS mercaderias_genericas CASCADE;
DROP TABLE IF EXISTS actividades CASCADE;

CREATE TABLE actividades (
	id SERIAL NOT NULL,
	nombre VARCHAR(60) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (nombre)
);

CREATE TABLE fiscalizacion_inspecciones (
	id SERIAL NOT NULL,
	inspector VARCHAR(120) NOT NULL,
	operador_cuit VARCHAR(13),
	fecha TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	latitud FLOAT,
	longitud FLOAT,
	tipo VARCHAR(30) NOT NULL,
	resultado VARCHAR(30) NOT NULL,
	observaciones TEXT,
	enviada BOOLEAN NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE fiscalizacion_reincidencias (
	id SERIAL NOT NULL,
	operador_cuit VARCHAR(13) NOT NULL,
	cantidad INTEGER NOT NULL,
	ultima_fecha DATE NOT NULL,
	observaciones TEXT,
	PRIMARY KEY (id)
);

CREATE TABLE mercaderias_genericas (
	id SERIAL NOT NULL,
	codigo VARCHAR(20) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	unidad_medida VARCHAR(20),
	requiere_trazabilidad BOOLEAN NOT NULL,
	requiere_numero_tropa BOOLEAN NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE personas (
	id SERIAL NOT NULL,
	tipo VARCHAR(2) NOT NULL,
	tipo_documento VARCHAR(4) NOT NULL,
	identificador VARCHAR(13) NOT NULL,
	nombre VARCHAR(120),
	apellido VARCHAR(120),
	razon_social VARCHAR(255),
	domicilio VARCHAR(255),
	telefono VARCHAR(30),
	email VARCHAR(255),
	PRIMARY KEY (id),
	CONSTRAINT chk_identificador_longitud CHECK ((tipo_documento = 'DNI' AND LENGTH(identificador) = 8) OR (tipo_documento = 'CUIT' AND LENGTH(identificador) = 11)),
	CONSTRAINT chk_tipo_persona CHECK (tipo IN ('PF', 'PJ')),
	CONSTRAINT chk_tipo_documento CHECK (tipo_documento IN ('DNI', 'CUIT'))
);

CREATE TABLE registros_trazabilidad (
	id SERIAL NOT NULL,
	tipo_ingreso VARCHAR(30) NOT NULL,
	origen_provincia VARCHAR(120),
	origen_localidad VARCHAR(120),
	establecimiento_faena VARCHAR(255),
	numero_dte VARCHAR(30),
	numero_remito VARCHAR(30),
	cantidad_kg FLOAT NOT NULL,
	especie VARCHAR(20) NOT NULL,
	destino_tipo VARCHAR(40),
	destino_cuit VARCHAR(13),
	destino_razon_social VARCHAR(255),
	estado VARCHAR(20) NOT NULL,
	fecha_registro DATE NOT NULL,
	fecha_ingreso DATE,
	observaciones VARCHAR(500),
	creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE situaciones (
	id SERIAL NOT NULL,
	descripcion VARCHAR(40) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (descripcion)
);

CREATE TABLE categorias_afip (
	id SERIAL NOT NULL,
	actividad_id INTEGER NOT NULL,
	codigo VARCHAR(10) NOT NULL,
	descripcion VARCHAR(255) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(actividad_id) REFERENCES actividades (id)
);

CREATE TABLE fiscalizacion_actas (
	id SERIAL NOT NULL,
	inspeccion_id INTEGER NOT NULL,
	tipo VARCHAR(30) NOT NULL,
	numero VARCHAR(30),
	descripcion TEXT,
	estado VARCHAR(20) NOT NULL,
	fecha_firma TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	FOREIGN KEY(inspeccion_id) REFERENCES fiscalizacion_inspecciones (id)
);

CREATE TABLE fiscalizacion_decomisos (
	id SERIAL NOT NULL,
	inspeccion_id INTEGER NOT NULL,
	producto VARCHAR(255) NOT NULL,
	cantidad FLOAT NOT NULL,
	unidad VARCHAR(20) NOT NULL,
	motivo TEXT,
	destino VARCHAR(255),
	estado VARCHAR(20) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(inspeccion_id) REFERENCES fiscalizacion_inspecciones (id)
);

CREATE TABLE fiscalizacion_infracciones (
	id SERIAL NOT NULL,
	inspeccion_id INTEGER NOT NULL,
	operador_cuit VARCHAR(13),
	tipo VARCHAR(30) NOT NULL,
	gravedad VARCHAR(20) NOT NULL,
	descripcion TEXT,
	fecha DATE NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(inspeccion_id) REFERENCES fiscalizacion_inspecciones (id)
);

CREATE TABLE operadores (
	id SERIAL NOT NULL,
	persona_id INTEGER NOT NULL,
	domicilio_fiscal VARCHAR(255),
	PRIMARY KEY (id),
	FOREIGN KEY(persona_id) REFERENCES personas (id)
);

CREATE TABLE rocca_operadores (
	id SERIAL NOT NULL,
	persona_id INTEGER NOT NULL,
	tipo VARCHAR(40) NOT NULL,
	estado_registral VARCHAR(20) NOT NULL,
	fecha_inscripcion DATE NOT NULL,
	observaciones VARCHAR(500),
	PRIMARY KEY (id),
	FOREIGN KEY(persona_id) REFERENCES personas (id)
);

CREATE TABLE fiscalizacion_sanciones (
	id SERIAL NOT NULL,
	infraccion_id INTEGER NOT NULL,
	operador_cuit VARCHAR(13),
	tipo VARCHAR(30) NOT NULL,
	monto FLOAT,
	descripcion TEXT,
	estado VARCHAR(20) NOT NULL,
	fecha_aplicacion DATE NOT NULL,
	fecha_cumplimiento DATE,
	PRIMARY KEY (id),
	FOREIGN KEY(infraccion_id) REFERENCES fiscalizacion_infracciones (id)
);

CREATE TABLE operador_actividades (
	operador_id INTEGER NOT NULL,
	actividad_id INTEGER NOT NULL,
	PRIMARY KEY (operador_id, actividad_id),
	FOREIGN KEY(operador_id) REFERENCES operadores (id),
	FOREIGN KEY(actividad_id) REFERENCES actividades (id)
);

CREATE TABLE operador_categorias (
	id SERIAL NOT NULL,
	operador_id INTEGER NOT NULL,
	actividad_id INTEGER,
	categoria_id INTEGER NOT NULL,
	situacion_id INTEGER NOT NULL,
	desde_fecha VARCHAR(10),
	hasta_fecha VARCHAR(10),
	PRIMARY KEY (id),
	FOREIGN KEY(operador_id) REFERENCES operadores (id),
	FOREIGN KEY(actividad_id) REFERENCES actividades (id),
	FOREIGN KEY(categoria_id) REFERENCES categorias_afip (id),
	FOREIGN KEY(situacion_id) REFERENCES situaciones (id)
);

CREATE TABLE remitos_carnicos (
	id SERIAL NOT NULL,
	punto_emision VARCHAR(10) NOT NULL,
	numero_comprobante VARCHAR(20) NOT NULL,
	caso INTEGER NOT NULL,
	tipo_movimiento VARCHAR(3) NOT NULL,
	estado VARCHAR(2) NOT NULL,
	fecha_emision TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	fecha_vencimiento TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	hoja INTEGER NOT NULL,
	total_hojas INTEGER NOT NULL,
	titular_id INTEGER NOT NULL,
	depositario_id INTEGER,
	destinatario_id INTEGER,
	transportista_id INTEGER NOT NULL,
	chofer_apellido_nombre VARCHAR(120),
	chofer_documento VARCHAR(20),
	dominio_vehiculo VARCHAR(20),
	PRIMARY KEY (id),
	FOREIGN KEY(titular_id) REFERENCES operadores (id),
	FOREIGN KEY(depositario_id) REFERENCES operadores (id),
	FOREIGN KEY(destinatario_id) REFERENCES operadores (id),
	FOREIGN KEY(transportista_id) REFERENCES operadores (id)
);

CREATE TABLE rocca_domicilios_operativos (
	id SERIAL NOT NULL,
	operador_id INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	calle VARCHAR(255) NOT NULL,
	numero VARCHAR(20),
	localidad VARCHAR(120),
	departamento VARCHAR(120),
	provincia VARCHAR(120),
	codigo_postal VARCHAR(10),
	activo BOOLEAN NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(operador_id) REFERENCES rocca_operadores (id)
);

CREATE TABLE rocca_habilitaciones (
	id SERIAL NOT NULL,
	operador_id INTEGER NOT NULL,
	tipo VARCHAR(80) NOT NULL,
	numero VARCHAR(50),
	autoridad VARCHAR(120),
	fecha_emision DATE,
	fecha_vencimiento DATE,
	estado VARCHAR(20) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(operador_id) REFERENCES rocca_operadores (id)
);

CREATE TABLE rocca_inscripciones (
	id SERIAL NOT NULL,
	operador_id INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	organismo VARCHAR(120) NOT NULL,
	numero VARCHAR(50),
	fecha_inscripcion DATE,
	estado VARCHAR(20) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(operador_id) REFERENCES rocca_operadores (id)
);

CREATE TABLE renglones_remito (
	id SERIAL NOT NULL,
	remito_id INTEGER NOT NULL,
	mercaderia_id INTEGER NOT NULL,
	unidades DOUBLE PRECISION NOT NULL,
	kilos DOUBLE PRECISION NOT NULL,
	numero_tropa VARCHAR(50),
	PRIMARY KEY (id),
	FOREIGN KEY(remito_id) REFERENCES remitos_carnicos (id) ON DELETE CASCADE,
	FOREIGN KEY(mercaderia_id) REFERENCES mercaderias_genericas (id)
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
