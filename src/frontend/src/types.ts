/**
 * Tipos de dominio compartidos entre slices y componentes.
 */

/** Operador (sucursal) tal como lo devuelve la API ROCCA (ROCCAOperadorOut). */
export type Operador = {
  id: number;
  cuit: string;
  razon_social: string;
  domicilio_comercial: string | null;
  telefono: string | null;
  email: string | null;
  tipo: string;
  categoria: string | null;
  estado_registral: string;
  alta_fecha: string | null;
  baja_fecha: string | null;
  creado_en: string;
};
