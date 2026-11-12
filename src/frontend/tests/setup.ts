/**
 * Setup global de Vitest (entorno jsdom) para tests de integración.
 *
 * - `@testing-library/jest-dom`: matchers de DOM (toBeInTheDocument, etc.).
 * - MSW (`setupServer`): intercepta el fetch de RTK Query en Node/jsdom.
 * - Polyfills mínimos de jsdom que usa el stack (ResizeObserver, etc.).
 *
 * Se referencia desde `vitest.config.ts` vía `setupFiles`.
 */
import "@testing-library/jest-dom/vitest";
import { afterAll, afterEach, beforeAll } from "vitest";
import { server } from "./mocks/server";

// MSW: intercepta peticiones antes de los tests, resetea handlers por test,
// cierra después de todos.
// "warn" en vez de "error": la app dispara peticiones que no interesan al
// test (p. ej. /api/auth/logout del header); MSW las loguea sin tumbar el test.
// Un handler REAL olvidado se ve en la consola.
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// undici (fetch de Node) no resuelve URLs relativas contra `window.location`.
// Sin esto, `fetch("/api/...")` lanza "Failed to parse URL" antes de que MSW
// pueda interceptar. Se fija el origen global de undici (mismo mecanismo que
// usa Node para el flag --global-origin) con el mismo origen que jsdom.
// (Ver: https://github.com/nodejs/undici — Symbol.for("undici.globalOrigin.1")).
const undiciGlobalOrigin = Symbol.for("undici.globalOrigin.1");
(globalThis as Record<PropertyKey, unknown>)[undiciGlobalOrigin] = new URL(
  "http://localhost:3000",
);

// Polyfills mínimos para jsdom.
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
}
