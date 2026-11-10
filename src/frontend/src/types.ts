/**
 * Tipos compartidos de la aplicación ROCCA.
 */

/** Operador (F 102 / F 102A) — padrón de la cadena cárnica. */
export interface Operador {
  id: number;
  tipo_operador: "OPERADOR" | "OPERADOR_SUCURSAL";
  tipo_operacion: "COMERCIALIZADOR" | "TRANSPORTISTA";
  cuit: string;
  razon_social: string;
  domicilio_comercial: string;
  telefono: string | null;
  email: string | null;
  /** Tipo de persona: FISICA o JURIDICA. (Acepta también PRODUCTOR/COMERCIALIZADOR por compatibilidad con formularios legacy.) */
  tipo: "FISICA" | "JURIDICA" | "PRODUCTOR" | "COMERCIALIZADOR";
  categoria: string | null;
  estado_registral: "ACTIVO" | "BAJA" | "BLOQUEADO";
  alta_fecha: string | null;
  baja_fecha: string | null;
  creado_en: string;
}

/** Payload de alta de operador (POST /api/registro-operadores). */
export interface OperadorIn {
  tipo_operacion?: "COMERCIALIZADOR" | "TRANSPORTISTA";
  cuit: string;
  razon_social: string;
  domicilio_comercial: string;
  telefono?: string | null;
  email?: string | null;
  /** Tipo de persona: FISICA/JURIDICA, o PRODUCTOR/COMERCIALIZADOR (legacy). */
  tipo: "FISICA" | "JURIDICA" | "PRODUCTOR" | "COMERCIALIZADOR";
  categoria?: string | null;
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
