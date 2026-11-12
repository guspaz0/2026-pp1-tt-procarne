/**
 * MSW handlers — simulan las rutas de la API de ROCCA.
 *
 * Se usan en los tests de integración (Vitest + RTL) para interceptar las
 * peticiones de RTK Query sin depender del backend real.
 *
 * Las URLs son **relativas** (`/api/...`): RTK Query usa `baseUrl: "/api"`
 * y en jsdom los requests son relativos a `http://localhost`, igual que en
 * la app real (Vite proxy).
 *
 * `createHandlers()` es una factory: cada llamada devuelve un array FRESCO
 * con su propio estado, así el estado del mock no se filtra entre tests.
 */
import { http, HttpResponse } from "msw";
import {
  OPERADORES_MOCK,
  ACTIVIDADES_MOCK,
  LOCALIDADES_MOCK,
  DEPARTAMENTOS_MOCK,
  crearOperadorMock,
} from "./data";
import type { Operador, OperadorIn } from "../../src/types";

export const USUARIO_MOCK = {
  id: "test-user",
  email: "test@rocca.gob.ar",
  emailVerified: true,
  providers: ["email"],
  createdAt: new Date(2026, 0, 1).toISOString(),
  updatedAt: new Date(2026, 0, 1).toISOString(),
  user_metadata: { rol: "admin" },
};

export const LOGIN_OK = {
  access_token: "fake-access-token",
  refresh_token: "fake-refresh-token",
  user: USUARIO_MOCK,
};

export type HandlerOptions = {
  /** Reemplaza la lista de operadores (GET/POST). */
  operadores?: Operador[];
  /** Si es true, `/api/auth/me` devuelve 401 (sin sesión). */
  unauthenticated?: boolean;
  /** Respuesta para POST /api/auth/login (por defecto: login exitoso). */
  loginResponse?: { status?: number; body?: unknown };
  /** Si es true, el POST a registro-operadores devuelve 400 (CUIT duplicado). */
  duplicarAlta?: boolean;
  /** Latencia artificial en ms para las respuestas (tests de estados loading). */
  delayMs?: number;
};

const wait = (ms?: number) =>
  ms ? new Promise((r) => setTimeout(r, ms)) : Promise.resolve();

/** Crea un set de handlers con estado propio (fresco por test si se rellama). */
export function createHandlers(options: HandlerOptions = {}) {
  const operadores: Operador[] = [
    ...(options.operadores ?? OPERADORES_MOCK),
  ];
  let nextId = 1000;

  const json = (body: unknown, init: { status?: number } = {}) =>
    HttpResponse.json(body, { status: init.status ?? 200 });

  return [
    // GET /api/registro-operadores/catalogo/actividades — catálogo de actividades
    http.get("/api/registro-operadores/catalogo/actividades", async () => {
      await wait(options.delayMs);
      return json(ACTIVIDADES_MOCK);
    }),

    // GET /api/registro-operadores — lista (y por id)
    http.get("/api/registro-operadores", async ({ request }) => {
      await wait(options.delayMs);
      const url = new URL(request.url);
      const id = url.searchParams.get("id");
      if (id) {
        const op = operadores.find((o) => o.id === Number(id));
        return op
          ? json(op)
          : json({ detail: "Operador no encontrado" }, { status: 404 });
      }
      return json(operadores);
    }),

    // POST /api/registro-operadores — alta de operador
    http.post("/api/registro-operadores", async ({ request }) => {
      await wait(options.delayMs);
      const data = (await request.json()) as OperadorIn;
      if (options.duplicarAlta || operadores.some((o) => o.cuit === data.cuit)) {
        return json(
          {
            detail: `CUIT duplicado: ya existe un operador con CUIT ${data.cuit}`,
          },
          { status: 400 },
        );
      }
      const nuevo = crearOperadorMock(data.cuit, data.razon_social);
      nuevo.id = nextId++;
      nuevo.tipo = data.tipo;
      nuevo.categoria = data.categoria ?? null;
      nuevo.domicilio_comercial = data.domicilio_comercial ?? "Sin domicilio";
      nuevo.telefono = data.telefono ?? null;
      nuevo.email = data.email ?? null;
      operadores.push(nuevo);
      return json(nuevo, { status: 201 });
    }),

    // GET /api/f102?id={id} — cartón F 102 (PDF base64 fake)
    http.get("/api/f102", ({ request }) => {
      const url = new URL(request.url);
      const op = operadores.find((o) => o.id === Number(url.searchParams.get("id")));
      if (!op) {
        return json({ detail: "Operador no encontrado" }, { status: 404 });
      }
      return json({
        fileContents: Buffer.from("FAKE PDF CONTENT").toString("base64"),
        contentType: "application/pdf",
        fileDownloadName: `f102_${op.id}.pdf`,
        lastModified: new Date().toISOString(),
        entityTag: null,
        enableRangeProcessing: false,
      });
    }),

    // GET /api/auth/me — usuario autenticado (o 401)
    http.get("/api/auth/me", async () => {
      await wait(options.delayMs);
      if (options.unauthenticated) {
        return json({ detail: "No autenticado" }, { status: 401 });
      }
      return json(USUARIO_MOCK);
    }),

    // POST /api/auth/login — login (o error configurable)
    http.post("/api/auth/login", async () => {
      await wait(options.delayMs);
      const resp = options.loginResponse;
      return json(resp?.body ?? LOGIN_OK, { status: resp?.status ?? 200 });
    }),

    // POST /api/auth/signup — registro (mismo contrato que login)
    http.post("/api/auth/signup", async () => {
      await wait(options.delayMs);
      const resp = options.loginResponse;
      return json(resp?.body ?? LOGIN_OK, { status: resp?.status ?? 200 });
    }),

    // POST /api/auth/logout
    http.post("/api/auth/logout", () => new HttpResponse(null, { status: 204 })),

    // GET https://apis.datos.gob.ar/georef/api/v2.0/localidades — API pública
    // de georreferenciación (datos.gob.ar). Se intercepta por URL absoluta
    // porque el baseQuery de georefApi usa ese origen (no /api).
    http.get("https://apis.datos.gob.ar/georef/api/v2.0/localidades", async ({ request }) => {
      await wait(options.delayMs);
      const url = new URL(request.url);
      const nombre = (url.searchParams.get("nombre") ?? "").toLowerCase();
      const filtradas = LOCALIDADES_MOCK.filter((l) =>
        l.nombre.toLowerCase().includes(nombre),
      );
      return json({
        cantidad: filtradas.length,
        total: filtradas.length,
        inicio: 0,
        localidades: filtradas,
      });
    }),

    // GET https://apis.datos.gob.ar/georef/api/v2.0/departamentos — API pública
    // de georreferenciación (datos.gob.ar).
    http.get("https://apis.datos.gob.ar/georef/api/v2.0/departamentos", async ({ request }) => {
      await wait(options.delayMs);
      const url = new URL(request.url);
      const nombre = (url.searchParams.get("nombre") ?? "").toLowerCase();
      const filtrados = DEPARTAMENTOS_MOCK.filter((d) =>
        d.nombre.toLowerCase().includes(nombre),
      );
      return json({
        cantidad: filtrados.length,
        total: filtrados.length,
        inicio: 0,
        departamentos: filtrados,
      });
    }),
  ];
}

/** Set de handlers por defecto (estado fresco) — para el server global de setup. */
export const handlers = createHandlers();
