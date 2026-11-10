/**
 * Fixture de Playwright para E2E con MSW a nivel de Playwright.
 *
 * Usa `@msw/playwright` (v0.7.0) → `defineNetworkFixture`, que intercepta
 * las peticiones a nivel de Playwright (page.route) — NO requiere service
 * worker ni código de MSW en la app. Permite overrides POR TEST vía
 * `network.use(...)` sin tocar el bundle de dev.
 *
 * El fixture recibe `context` (el BrowserContext de Playwright), así que
 * se define con `base.extend` y se resuelve por test.
 *
 * Uso:
 *   import { test, expect } from "./fixtures";
 *   test("...", async ({ page, network }) => {
 *     network.use(http.get("/api/registro-operadores", () =>
 *       new HttpResponse(null, { status: 500 })));
 *     await page.goto("/operadores/padron");
 *   });
 */
import { test as base, expect } from "@playwright/test";
import { defineNetworkFixture } from "@msw/playwright";
import type { BrowserContext } from "@playwright/test";
import { createHandlers } from "../../src/mocks/handlers";

// `defineNetworkFixture` no expone tipos en 0.7.0; el network resultante
// tiene .use / .enable / .disable / .resetHandlers / .restoreHandlers.
type NetworkFixture = ReturnType<typeof defineNetworkFixture>;

export const test = base.extend<{ network: NetworkFixture }>({
  network: async ({ context }, use) => {
    const network = defineNetworkFixture({
      handlers: createHandlers(),
      context: context as unknown as BrowserContext,
    });
    await network.enable();
    await use(network);
    await network.disable();
  },
});

export { expect };
