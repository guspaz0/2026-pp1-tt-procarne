/**
 * Handlers de MSW para los endpoints de Operadores.
 *
 * Se comparten entre el browser worker (dev) y el setup de Node (tests).
 * Los handlers son factory functions para poder reiniciar el estado del
 * mock entre tests (p. ej. `createHandlers()` crea un array fresco).
 *
 * Endpoints cubiertos (ver operadoresApi.ts):
 *   GET  /api/registro-operadores          → listar
 *   POST /api/registro-operadores          → registrar
 */
import { http, HttpResponse, type RequestHandler } from "msw";
import { OPERADORES_MOCK, type OperadorMock } from "./data";

const BASE = "/api";

/**
 * Crea una colección de handlers con un estado inicial opcional.
 *
 * Por defecto sirve `OPERADORES_MOCK` (inmutable entre peticiones). Si
 * pasás `db` el mock muta ese array al registrar, imitando la persistencia
 * del backend real — útil para tests de flujo completo.
 */
/**
 * Agrupa los operadores por persona (CUIT), imitando /registro-operadores/jerarquia.
 * Devuelve el shape GrupoPersona[] que consume la vista de Jerarquía.
 */
function jerarquiaDe(db: OperadorMock[]) {
  const porCuit = new Map<string, OperadorMock[]>();
  for (const o of db) {
    const arr = porCuit.get(o.cuit) ?? [];
    arr.push(o);
    porCuit.set(o.cuit, arr);
  }
  return [...porCuit.entries()].map(([cuit, sucursales]) => ({
    persona_id: sucursales[0].persona_id,
    nombre: sucursales[0].razon_social,
    cuit,
    tipo_documento: "CUIT",
    tipo_persona: sucursales[0].tipo === "CARNICERIA" ? "fisica" : "juridica",
    sucursales,
  }));
}

export function createHandlers(
  db: OperadorMock[] = [...OPERADORES_MOCK],
): RequestHandler[] {
  return [
    http.get(`${BASE}/registro-operadores`, () => {
      // Copia defensiva para que el cliente no mutar el estado interno.
      return HttpResponse.json([...db]);
    }),

    http.get(`${BASE}/registro-operadores/jerarquia`, () => {
      return HttpResponse.json(jerarquiaDe(db));
    }),

    http.post(`${BASE}/registro-operadores`, async ({ request }) => {
      const body = (await request.json()) as {
        cuit: string;
        razon_social: string;
        tipo: string;
        categoria?: string | null;
        domicilio_comercial?: string | null;
        telefono?: string | null;
        email?: string | null;
      };

      // Simula la validación de CUIT único del backend.
      const yaExiste = db.some(
        (o) => o.cuit === body.cuit && o.razon_social === body.razon_social,
      );
      if (yaExiste) {
        return HttpResponse.json(
          { detail: "El CUIT ya está registrado para este establecimiento" },
          { status: 409 },
        );
      }

      const nuevo: OperadorMock = {
        id: db.length > 0 ? Math.max(...db.map((o) => o.id)) + 1 : 1,
        persona_id: 0,
        cuit: body.cuit,
        razon_social: body.razon_social,
        domicilio_comercial: body.domicilio_comercial ?? null,
        telefono: body.telefono ?? null,
        email: body.email ?? null,
        tipo: body.tipo,
        categoria: body.categoria ?? null,
        estado_registral: "ACTIVO",
        alta_fecha: new Date().toISOString(),
        baja_fecha: null,
        creado_en: new Date().toISOString(),
      };
      db.push(nuevo);
      return HttpResponse.json(nuevo, { status: 201 });
    }),
  ];
}

/** Handlers "por defecto" para arrancar rápido (dev). */
export const operadoresHandlers = createHandlers();
