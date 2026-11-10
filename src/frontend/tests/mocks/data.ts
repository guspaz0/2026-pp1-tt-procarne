/**
 * Datos mock para los handlers de MSW.
 *
 * Reflejan el shape exacto de `ROCCAOperadorOut` del backend
 * (src/backend/app/modulos/registro_operadores/schema.py). Se usan tanto
 * en el browser worker (mocks/browser.ts) como en el setup de Node
 * (mocks/server.ts), así los dos entornos comparten el mismo padrón.
 */

export type OperadorMock = {
  id: number;
  persona_id: number;
  cuit: string;
  razon_social: string;
  domicilio_comercial: string | null;
  telefono: string | null;
  email: string | null;
  tipo: string;
  categoria: string | null;
  estado_registral: "ACTIVO" | "BAJADO";
  alta_fecha: string | null;
  baja_fecha: string | null;
  creado_en: string;
};

/**
 * Padrón de ejemplo: 7 establecimientos, 3 personas titulares (por CUIT).
 * Se elige un CUIT por persona para que la vista de Jerarquía agrupe bien.
 */
export const OPERADORES_MOCK: OperadorMock[] = [
  {
    id: 1,
    persona_id: 1,
    cuit: "30-71234567-8",
    razon_social: "CARNICERÍA LA NORITA",
    domicilio_comercial: "Av. Belgrano 1234, Santiago del Estero",
    telefono: "385-4123456",
    email: "lanorita@example.com",
    tipo: "CARNICERIA",
    categoria: "CARNICERIAS",
    estado_registral: "ACTIVO",
    alta_fecha: "2025-11-01T10:00:00",
    baja_fecha: null,
    creado_en: "2025-11-01T10:00:00",
  },
  {
    id: 2,
    persona_id: 1,
    cuit: "30-71234567-8",
    razon_social: "CARNICERÍA LA NORITA — SUC. AVENIDA",
    domicilio_comercial: "Avenida 5678, Santiago del Estero",
    telefono: "385-4123457",
    email: "sucursal@example.com",
    tipo: "CARNICERIA",
    categoria: "CARNICERIAS",
    estado_registral: "ACTIVO",
    alta_fecha: "2025-11-05T09:30:00",
    baja_fecha: null,
    creado_en: "2025-11-05T09:30:00",
  },
  {
    id: 3,
    persona_id: 2,
    cuit: "30-82345678-9",
    razon_social: "FRIGORÍFICO EL TRUFO S.R.L.",
    domicilio_comercial: "Ruta Nac. 15 km 420, Santiago del Estero",
    telefono: "385-5234567",
    email: "info@eltrufosrl.com",
    tipo: "FRIGORIFICO",
    categoria: "FRIGORIFICOS",
    estado_registral: "ACTIVO",
    alta_fecha: "2025-10-15T14:20:00",
    baja_fecha: null,
    creado_en: "2025-10-15T14:20:00",
  },
  {
    id: 4,
    persona_id: 2,
    cuit: "30-82345678-9",
    razon_social: "FRIGORÍFICO EL TRUFO — PLANTA 2",
    domicilio_comercial: "Parque Industrial, Santiago del Estero",
    telefono: "385-5234568",
    email: "planta2@eltrufosrl.com",
    tipo: "FRIGORIFICO",
    categoria: "FRIGORIFICOS",
    estado_registral: "ACTIVO",
    alta_fecha: "2025-10-20T11:00:00",
    baja_fecha: null,
    creado_en: "2025-10-20T11:00:00",
  },
  {
    id: 5,
    persona_id: 3,
    cuit: "20-93456789-0",
    razon_social: "DISTRIBUIDORA CÁRNICA SDE",
    domicilio_comercial: "Bv. San Martín 890, Santiago del Estero",
    telefono: "385-6345678",
    email: "ventas@disarcardsde.com",
    tipo: "DISTRIBUIDOR",
    categoria: "DISTRIBUCION",
    estado_registral: "ACTIVO",
    alta_fecha: "2025-09-30T08:45:00",
    baja_fecha: null,
    creado_en: "2025-09-30T08:45:00",
  },
  {
    id: 6,
    persona_id: 3,
    cuit: "20-93456789-0",
    razon_social: "DISTRIBUIDORA CÁRNICA SDE — DEP. LA BANDA",
    domicilio_comercial: "Calle 25 de Mayo 456, La Banda",
    telefono: "385-6345679",
    email: "labanda@disarcardsde.com",
    tipo: "DISTRIBUIDOR",
    categoria: "DISTRIBUCION",
    estado_registral: "BAJADO",
    alta_fecha: "2025-09-30T09:00:00",
    baja_fecha: "2026-01-10T12:00:00",
    creado_en: "2025-09-30T09:00:00",
  },
  {
    id: 7,
    persona_id: 4,
    cuit: "23-10101010-1",
    razon_social: "SALADERO ARTESANAL PAMPA",
    domicilio_comercial: "Calle 9 de Julio 77, Santiago del Estero",
    telefono: null,
    email: null,
    tipo: "SALADERO",
    categoria: "SALADEROS",
    estado_registral: "ACTIVO",
    alta_fecha: "2025-08-12T16:30:00",
    baja_fecha: null,
    creado_en: "2025-08-12T16:30:00",
  },
];
