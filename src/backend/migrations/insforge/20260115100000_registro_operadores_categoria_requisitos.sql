-- InsForge Migration: Registro de Operadores — Categoría y Requisitos
-- Archivo: 20260115100000_registro_operadores_categoria_requisitos.sql
--
-- Aplica los cambios del Módulo I (Registro Provincial de Operadores)
-- a la base de datos PostgreSQL de InsForge.
--
-- Uso:
--   npx @insforge/cli db migrations up --all

-- 1. Agregar columna 'categoria' a rocca_operadores
ALTER TABLE public.rocca_operadores
  ADD COLUMN IF NOT EXISTS categoria VARCHAR(40);

CREATE INDEX IF NOT EXISTS ix_rocca_operadores_categoria
  ON public.rocca_operadores (categoria);

-- 2. Crear tabla rocca_requisitos_inscripcion
CREATE TABLE IF NOT EXISTS public.rocca_requisitos_inscripcion (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  operador_id BIGINT NOT NULL REFERENCES public.rocca_operadores(id) ON DELETE CASCADE,
  codigo VARCHAR(60) NOT NULL,
  descripcion VARCHAR(255),
  es_general BOOLEAN NOT NULL DEFAULT FALSE,
  cumplido BOOLEAN NOT NULL DEFAULT FALSE,
  fecha_cumplimiento TIMESTAMPTZ,
  observaciones VARCHAR(500),
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_rocca_requisitos_inscripcion_operador_id
  ON public.rocca_requisitos_inscripcion (operador_id);

CREATE INDEX IF NOT EXISTS ix_rocca_requisitos_inscripcion_codigo
  ON public.rocca_requisitos_inscripcion (codigo);
