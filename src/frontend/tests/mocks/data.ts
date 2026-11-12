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
    tipo_operador: "OPERADOR",
    tipo_operacion: "COMERCIALIZADOR",
    cuit: "30-71234567-8",
    razon_social: "CARNICERÍA LA NORITA",
    domicilio_comercial: "JOSE BENJAMIN ABALOS N. 4582, B. ALMIRANTE BROWN",
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
    tipo_operador: "OPERADOR",
    tipo_operacion: "COMERCIALIZADOR",
    cuit: "30-82345678-9",
    razon_social: "FRIGORÍFICO EL TRUFO S.R.L.",
    domicilio_comercial: "AV. SAN MARTÍN 1234, CAPITAL",
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
    tipo_operador: "OPERADOR_SUCURSAL",
    tipo_operacion: "COMERCIALIZADOR",
    cuit: "30-71234567-8", // Mismo CUIT que id=1 (sucursal de LA NORITA)
    razon_social: "CARNICERÍA LA NORITA SUC. 2",
    domicilio_comercial: "Mitre 567, LA BANDA",
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
    tipo_operador: "OPERADOR",
    tipo_operacion: "TRANSPORTISTA",
    cuit: "30-99988877-0",
    razon_social: "TRANSPORTES CARNE S.A.",
    domicilio_comercial: "Ruta Nacional 9, KM 45",
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
export function crearOperadorMock(cuit: string, razonSocial: string): Operador {
  return {
    id: Date.now(),
    tipo_operador: "OPERADOR",
    tipo_operacion: "COMERCIALIZADOR",
    cuit,
    razon_social: razonSocial,
    domicilio_comercial: "Domicilio de prueba",
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
  razon_social: "OPERADOR TEST",
  domicilio_comercial: "Calle Falsa 123",
  tipo: "FISICA",
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
