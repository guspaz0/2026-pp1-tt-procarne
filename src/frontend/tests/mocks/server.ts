/**
 * Setup de MSW para Node (tests de integración / Playwright fixtures).
 *
 * Se usa desde los tests para arrancar un worker de Node que intercepta
 * fetch a nivel de proceso. Útil para:
 *   - Testear el store + RTK Query sin depender del backend.
 *   - Validar la lógica de invalidación de tags.
 *
 * Ejemplo:
 *   import { server } from "./mocks/server";
 *   beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
 *   afterEach(() => server.resetHandlers());
 *   afterAll(() => server.close());
 */
import { setupServer } from "msw/node";
import { createHandlers } from "./handlers";

export const server = setupServer(...createHandlers());
