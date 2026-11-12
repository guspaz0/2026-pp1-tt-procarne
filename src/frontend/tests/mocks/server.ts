/**
 * MSW server (Node) para tests de integración en Vitest.
 *
 * Intercepta el `fetch` que usa RTK Query dentro de jsdom. Los handlers
 * viven en `./handlers.ts` (compartidos también por la capa de browser).
 */
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);
