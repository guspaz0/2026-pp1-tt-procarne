/**
 * Tipos compartidos de la aplicación ROCCA.
 */

/** Domicilio estructurado. */
export interface Domicilio {
  id: number;
  calle: string;
  numero: string | null;
  localidad: string;
  provincia: string;
  codigo_postal: string | null;
}

/** Operador (F 102 / F 102A) — padrón de la cadena cárnica. */
export interface Operador {
  id: number;
  /** Id de la persona titular (sucursal de esa persona). */
  persona_id: number | null;
  /** Tipo de establecimiento (FRIGORIFICO, CARNICERIA, …). */
  tipo: string;
  razon_social: string;
  domicilio: Domicilio | null;
  telefono: string | null;
  /** CUIT de la persona titular (resuelto desde la persona). */
  cuit: string | null;
  /** Nombre de la persona titular. */
  titular: string | null;
  categoria: string | null;
  estado_registral: string;
  alta_fecha: string | null;
  baja_fecha: string | null;
  creado_en: string;
}

/** Persona titular (PF/PJ) con sus datos y domicilio estructurado. */
export interface Persona {
  id: number;
  tipo: "PF" | "PJ";
  tipo_documento: string;
  identificador: string;
  nombre: string;
  email: string | null;
  domicilio: Domicilio | null;
}

/** Jerarquía de una persona: la persona y sus operadores (sucursales). */
export interface JerarquiaPersona {
  persona: Persona;
  operadores: Operador[];
}

/** Payload de alta de operador (POST /api/registro-operadores). */
export interface OperadorIn {
  /** Tipo de establecimiento (FRIGORIFICO, CARNICERIA, …). */
  tipo: string;
  razon_social: string;
  /**
   * CUIT de la persona titular. Opcional: si no se pasa, el backend lo toma
   * de la sesión (el usuario autenticado ya está vinculado a su Persona).
   */
  cuit?: string | null;
  domicilio?: {
    calle: string;
    numero?: string | null;
    localidad: string;
    provincia: string;
    codigo_postal?: string | null;
  } | null;
  telefono?: string | null;
  /** Email de contacto de la persona titular (se guarda en personas.email). */
  email?: string | null;
  categoria?: string | null;
  /** Códigos AFIP del catálogo de actividades que realiza el operador (N:M). */
  codigo_afip?: string[];
}

/** Payload de alta de usuario (POST /api/auth/signup). */
export interface SignupPayload {
  email: string;
  password: string;
  name?: string;
  /** Número de documento del titular (CUIT de 11 dígitos o DNI de 8). */
  cuit?: string;
  /** Tipo de documento: "CUIT" o "DNI". */
  tipo_documento?: "CUIT" | "DNI";
  user_metadata?: Record<string, unknown>;
}

/** Formatea un Domicilio estructurado como string legible. */
export function formatearDomicilio(d: Domicilio | null | undefined): string {
  if (!d) return "";
  const partes = [d.calle];
  if (d.numero) partes.push(`N°${d.numero}`);
  const calle = partes.join(" ");
  return `${calle} - ${d.localidad}, ${d.provincia}`;
}

/**
 * Parsea un string de domicilio completo (formato F102: "CALLE N°123 - LOCALIDAD, PROVINCIA")
 * en un objeto Domicilio estructurado para enviar al backend.
 */
export function parsearDomicilio(texto: string): NonNullable<OperadorIn["domicilio"]> {
  const resultado: NonNullable<OperadorIn["domicilio"]> = {
    calle: texto,
    numero: null,
    localidad: "",
    provincia: "",
    codigo_postal: null,
  };
  if (!texto) return resultado;

  // Separar calle del resto con " - " (último guion con espacios)
  let parteCalle = texto;
  let parteResto = "";
  const idxSep = texto.lastIndexOf(" - ");
  if (idxSep !== -1) {
    parteCalle = texto.slice(0, idxSep);
    parteResto = texto.slice(idxSep + 3);
  }

  // Separar localidad y provincia con ", "
  if (parteResto.includes(", ")) {
    const idxComa = parteResto.lastIndexOf(", ");
    resultado.localidad = parteResto.slice(0, idxComa).trim();
    resultado.provincia = parteResto.slice(idxComa + 2).trim();
  } else {
    resultado.localidad = parteResto.trim();
  }

  // Extraer número: "N°123" o "Nº123" o "N° 123/45"
  const numMatch = parteCalle.match(/N[°º]\s*(\d+[\d/]*)/i);
  if (numMatch) {
    resultado.numero = numMatch[1];
    const idxNum = parteCalle.indexOf(numMatch[0]);
    const calleLimpia = parteCalle.slice(0, idxNum).replace(/[\s\-]+$/, "").trim();
    resultado.calle = calleLimpia || parteCalle;
  } else {
    resultado.calle = parteCalle.trim();
  }

  return resultado;
}

/** Usuario autenticado (modelo de InsForge, camelCase). */
export interface Usuario {
  id?: string;
  email?: string;
  emailVerified?: boolean;
  providers?: string[];
  createdAt?: string;
  updatedAt?: string;
  user_metadata?: Record<string, unknown>;
}

/** Resultado de login/signup: InsForge devuelve los tokens + usuario. */
export interface LoginResult {
  access_token?: string;
  refresh_token?: string;
  user?: Usuario;
}
