/**
 * Utilidades reutilizables para Component Testing (CT).
 *
 * Sigue el patrón "renderWithProviders" de la guía de testing de Redux:
 * cada test recibe un store FRESCO (o uno preconfigurado con `preloadedState`),
 * el componente queda envuelto en <Provider store={...}>, y las peticiones
 * HTTP se interceptan con `page.route` (misma estrategia que ya usa
 * tests/playwright/index.tsx — sin MSW, más confiable en CT).
 *
 * Los specs CT declaran:
 *
 *   import { test, expect, withStore, mockAuthedApi } from "../../tests/ct-utils";
 *
 *   test("...", async ({ mount }) => {
 *     const { store } = await mount<WithStore>(
 *       <Componente />,
 *       { preloadedState: { formF102: ... } },
 *     );
 *     ...
 *   });
 *
 * La configuración global (Provider + rutas mockeadas) vive en
 * tests/playwright/index.tsx (beforeMount), que re-exporta la infra de acá.
 */
import { test as base, expect, beforeMount } from "@playwright/experimental-ct-react";
import { Provider } from "react-redux";
import { setupStore, type RootState, type AppStore } from "../src/store/store";
import { OPERADORES_MOCK, ACTIVIDADES_MOCK } from "./mocks/data";
import type { Operador } from "../src/types";

/** Extiende el fixture `mount` para devolver el store creado en beforeMount. */
export interface WithStore {
  store: AppStore;
}

export const test = base.extend<WithStore & HooksConfig>({});
export { expect };

/** Config que cada test puede pasar a `mount<WithStore & HooksConfig>(...)`. */
export interface HooksConfig {
  /** Estado inicial para los slices (p. ej. `formF102`, `auth`, `operadores`). */
  preloadedState?: Partial<RootState>;
  /**
   * Reemplaza la respuesta de `GET /api/registro-operadores` (lista).
   * Por defecto sirve `OPERADORES_MOCK`.
   */
  operadores?: Operador[];
  /**
   * Controla `GET /api/auth/me`:
   *  - `true` (default): usuario autenticado de prueba.
   *  - `false`: devuelve 401 (sin sesión).
   */
  authed?: boolean;
  /** Respuesta para `POST /api/auth/login` (default: login exitoso). */
  loginResponse?: { status?: number; body?: unknown };
  /** Si es `true`, el POST a `/api/registro-operadores` devuelve 400 CUIT duplicado. */
  duplicarAlta?: boolean;
}

export type { AppStore, RootState };

/** Usuario de prueba que sirve `GET /api/auth/me`. */
export const USUARIO_MOCK = {
  id: "test-user",
  email: "test@rocca.gob.ar",
  emailVerified: true,
  providers: ["email"],
  createdAt: new Date(2026, 0, 1).toISOString(),
  updatedAt: new Date(2026, 0, 1).toISOString(),
  user_metadata: { rol: "admin" },
};

/** Respuesta de `POST /api/auth/login` / `/auth/signup` por defecto. */
export const LOGIN_OK = {
  access_token: "fake-access-token",
  refresh_token: "fake-refresh-token",
  user: USUARIO_MOCK,
};

/**
 * Registra todas las rutas mockeadas de la API ROCCA en el `page` del test.
 * Se llama una vez en `beforeMount` (tests/playwright/index.tsx).
 */
export async function mockRoccaApi(
  page: {
    route(
      glob: string,
      handler: (route: {
        request(): { url(): string; method(): string; json(): Promise<any> };
        fulfill(options: { status: number; contentType: string; body: string }): Promise<void>;
      }) => void | Promise<void>,
    ): Promise<void>;
  },
  config: HooksConfig = {},
) {
  const operadores: Operador[] = config.operadores ? [...config.operadores] : [...OPERADORES_MOCK];
  let nextId = 1000;

  // GET/POST /api/registro-operadores — padrón de operadores.
  await page.route("**/api/registro-operadores**", async (route) => {
    const url = new URL(route.request().url());
    const method = route.request().method();

    if (url.pathname.endsWith("/catalogo/actividades") && method === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(ACTIVIDADES_MOCK),
      });
    }
    if (url.pathname.endsWith("/registro-operadores") && method === "GET") {
      const id = url.searchParams.get("id");
      if (id) {
        const op = operadores.find((o) => o.id === Number(id));
        return op
          ? route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(op) })
          : route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Operador no encontrado" }) });
      }
      return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(operadores) });
    }
    if (method === "POST") {
      const body = await route.request().json().catch(() => ({}));
      if (config.duplicarAlta || operadores.some((o) => o.cuit === body.cuit)) {
        return route.fulfill({
          status: 400,
          contentType: "application/json",
          body: JSON.stringify({ detail: `CUIT duplicado: ya existe un operador con CUIT ${body.cuit}` }),
        });
      }
      const nuevo: Operador = {
        id: nextId++,
        tipo_operador: "OPERADOR",
        tipo_operacion: "COMERCIALIZADOR",
        cuit: body.cuit,
        razon_social: body.razon_social,
        domicilio_comercial: body.domicilio_comercial ?? "Sin domicilio",
        telefono: body.telefono ?? null,
        email: body.email ?? null,
        tipo: body.tipo ?? "FISICA",
        categoria: body.categoria ?? null,
        estado_registral: "ACTIVO",
        alta_fecha: new Date().toISOString(),
        baja_fecha: null,
        creado_en: new Date().toISOString(),
      };
      operadores.push(nuevo);
      return route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify(nuevo) });
    }
    return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  // GET /api/f102?id={id} — cartón F 102 (PDF fake).
  await page.route("**/api/f102**", (route) => {
    const url = new URL(route.request().url());
    const op = operadores.find((o) => o.id === Number(url.searchParams.get("id")));
    if (!op) {
      return route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Operador no encontrado" }) });
    }
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        fileContents: Buffer.from("FAKE PDF CONTENT").toString("base64"),
        contentType: "application/pdf",
        fileDownloadName: `f102_${op.id}.pdf`,
        lastModified: new Date().toISOString(),
        entityTag: null,
        enableRangeProcessing: false,
      }),
    });
  });

  // Auth: GET /api/auth/me · POST /api/auth/login · /signup · /logout.
  await page.route("**/api/auth/**", (route) => {
    const url = new URL(route.request().url());
    const method = route.request().method();

    if (url.pathname.endsWith("/auth/me") && method === "GET") {
      return config.authed === false
        ? route.fulfill({ status: 401, contentType: "application/json", body: JSON.stringify({ detail: "No autenticado" }) })
        : route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(USUARIO_MOCK) });
    }
    if ((url.pathname.endsWith("/auth/login") || url.pathname.endsWith("/auth/signup")) && method === "POST") {
      const resp = config.loginResponse;
      return route.fulfill({
        status: resp?.status ?? 200,
        contentType: "application/json",
        body: JSON.stringify(resp?.body ?? LOGIN_OK),
      });
    }
    if (url.pathname.endsWith("/auth/logout") && method === "POST") {
      return route.fulfill({ status: 204 });
    }
    return route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
}
