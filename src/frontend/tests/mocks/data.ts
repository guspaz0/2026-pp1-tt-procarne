/**
 * Datos mockeados para Component Testing (MSW).
 *
 * Representa un conjunto de operadores que la API `/api/registro-operadores`
 * devuelve. Se usa en los specs CT para simular respuestas del backend sin
 * depender de una BD real.
 */
import type { Operador, OperadorIn } from "../../src/types";

/** Operadores mockeados (padrón de prueba). */
export const OPERADORES_MOCK: Operador[] = [
  {
    id: 1,
    persona_id: 1,
    titular: "CARNICERÍA LA NORITA",
    cuit: "30-71234567-9",
    establecimiento_fantasia: "CARNICERÍA LA NORITA",
    domicilio: { id: 1, calle: "JOSE BENJAMIN ABALOS", numero: "4582", localidad: "SANTIAGO DEL ESTERO", provincia: "CAPITAL", codigo_postal: null },
    telefono: "(0385) 431-8910",
    email: "contacto@lanorita.com",
    tipo: "FISICA",
    categoria: "CARNICERIAS",
    estado_registral: "ACTIVO",
    alta_fecha: "2026-01-15T10:00:00Z",
    baja_fecha: null,
    creado_en: "2026-01-15T10:00:00Z",
  },
  {
    id: 2,
    persona_id: 2,
    titular: "FRIGORÍFICO EL TRUFO S.R.L.",
    cuit: "30-82345678-3",
    establecimiento_fantasia: "FRIGORÍFICO EL TRUFO S.R.L.",
    domicilio: { id: 2, calle: "AV. SAN MARTÍN", numero: "1234", localidad: "SANTIAGO DEL ESTERO", provincia: "CAPITAL", codigo_postal: null },
    telefono: "(0385) 442-7721",
    email: "admin@eltrufosrl.com",
    tipo: "JURIDICA",
    categoria: "SALA_DE_DESPOSTE",
    estado_registral: "ACTIVO",
    alta_fecha: "2026-02-20T14:30:00Z",
    baja_fecha: null,
    creado_en: "2026-02-20T14:30:00Z",
  },
  {
    id: 3,
    persona_id: 1,
    titular: "CARNICERÍA LA NORITA",
    cuit: "30-71234567-9", // Mismo CUIT que id=1 (sucursal de LA NORITA)
    establecimiento_fantasia: "CARNICERÍA LA NORITA SUC. 2",
    domicilio: { id: 3, calle: "Mitre", numero: "567", localidad: "LA BANDA", provincia: "SANTIAGO DEL ESTERO", codigo_postal: null },
    telefono: "(0385) 455-9012",
    email: "sucursal2@lanorita.com",
    tipo: "FISICA",
    categoria: "CARNICERIAS",
    estado_registral: "ACTIVO",
    alta_fecha: "2026-03-10T09:15:00Z",
    baja_fecha: null,
    creado_en: "2026-03-10T09:15:00Z",
  },
  {
    id: 4,
    persona_id: 4,
    titular: "TRANSPORTES CARNE S.A.",
    cuit: "30-99988877-9",
    establecimiento_fantasia: "TRANSPORTES CARNE S.A.",
    domicilio: { id: 4, calle: "Ruta Nacional 9", numero: null, localidad: "KM 45", provincia: "SANTIAGO DEL ESTERO", codigo_postal: null },
    telefono: null,
    email: null,
    tipo: "JURIDICA",
    categoria: "TRANSPONEDOR",
    estado_registral: "ACTIVO",
    alta_fecha: "2026-04-01T08:00:00Z",
    baja_fecha: null,
    creado_en: "2026-04-01T08:00:00Z",
  },
];

/** Catálogo de actividades económicas (códigos AFIP). */
export const ACTIVIDADES_MOCK = [
  { id: 1, codigo: "922210", nombre: "Carnicería Minorista" },
  { id: 2, codigo: "101120", nombre: "Despostadero / Ciclo II" },
  { id: 3, codigo: "101111", nombre: "Frigorífico / Ciclo I" },
  { id: 4, codigo: "463120", nombre: "Matarife Abastecedor" },
  { id: 5, codigo: "463110", nombre: "Distribuidor Mayorista" },
  { id: 6, codigo: "492110", nombre: "Transportista de Carnes" },
];

/**
 * Crea un operador de prueba con CUIT aleatorio (para tests de alta).
 * Útil para verificar que un POST crea correctamente un operador.
 */
export function crearOperadorMock(cuit: string, establecimientoFantasia: string): Operador {
  return {
    id: Date.now(),
    persona_id: 99,
    titular: establecimientoFantasia,
    cuit,
    establecimiento_fantasia: establecimientoFantasia,
    domicilio: { id: 99, calle: "Calle Prueba", numero: "1", localidad: "CAPITAL", provincia: "SDE", codigo_postal: null },
    telefono: null,
    email: null,
    tipo: "FISICA",
    categoria: "CARNICERIAS",
    estado_registral: "ACTIVO",
    alta_fecha: new Date().toISOString(),
    baja_fecha: null,
    creado_en: new Date().toISOString(),
  };
}

/** Payload de alta de prueba. */
export const OPERADOR_IN_MOCK: OperadorIn = {
  cuit: "30-12345678-9",
  establecimiento_fantasia: "OPERADOR TEST",
  domicilio: { calle: "Calle Falsa", numero: "123", localidad: "CAPITAL", provincia: "SDE" },
  tipo: "CARNICERIA",
  categoria: "CARNICERIAS",
  codigo_afip: ["922210"],
};

/* ------------------------------------------------------------------ */
/* Localidades (API de georreferenciación datos.gob.ar)                */
/* ------------------------------------------------------------------ */

/** Localidades mockeadas para el endpoint externo `GET /localidades`. */
export const LOCALIDADES_MOCK = [
  {
    id: "11001",
    nombre: "Villaguay",
    provincia: { id: "11", nombre: "Entre Ríos" },
    departamento: { id: "1101", nombre: "Villaguay" },
    municipio: { id: "110101", nombre: "Villaguay" },
    localidad_censal: { id: "11010101", nombre: "Villaguay" },
    categoria: "Localidad simple (LS)",
    centroide: { lat: -31.42, lon: -59.23 },
  },
  {
    id: "11002",
    nombre: "Villaguay Norte",
    provincia: { id: "11", nombre: "Entre Ríos" },
    departamento: { id: "1101", nombre: "Villaguay" },
    municipio: { id: "110101", nombre: "Villaguay" },
    localidad_censal: { id: "11010102", nombre: "Villaguay Norte" },
    categoria: "Localidad simple (LS)",
    centroide: { lat: -31.43, lon: -59.24 },
  },
  {
    id: "12001",
    nombre: "Concordia",
    provincia: { id: "11", nombre: "Entre Ríos" },
    departamento: { id: "12", nombre: "Concordia" },
    municipio: { id: "1201", nombre: "Concordia" },
    localidad_censal: { id: "120101", nombre: "Concordia" },
    categoria: "Localidad simple con entidad (LSE)",
    centroide: { lat: -31.31, lon: -58.03 },
  },
];

/** Departamentos mockeados para el endpoint externo `GET /departamentos`. */
export const DEPARTAMENTOS_MOCK = [
  {
    id: "9401",
    nombre: "Capital",
    nombre_completo: "Departamento Capital",
    provincia: { id: "94", nombre: "Santiago del Estero" },
    categoria: "Departamento",
  },
  {
    id: "9402",
    nombre: "Avellaneda",
    nombre_completo: "Departamento Avellaneda",
    provincia: { id: "94", nombre: "Santiago del Estero" },
    categoria: "Departamento",
  },
  {
    id: "9403",
    nombre: "Belgrano",
    nombre_completo: "Departamento Belgrano",
    provincia: { id: "94", nombre: "Santiago del Estero" },
    categoria: "Departamento",
  },
];
