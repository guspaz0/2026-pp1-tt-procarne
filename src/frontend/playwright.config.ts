import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E — ROCCA (Control Cadena Cárnica SDE).
 *
 * Se corre contra el Vite dev server (puerto 5173), que proxy-kea `/api`
 * al backend FastAPI (uvicorn :8000). Por eso el `webServer` arranca
 * `pnpm dev` y espera a que responda.
 *
 * Uso:
 *   npx playwright install chromium   # primera vez (browsers)
 *   npx playwright test               # suite completa
 *   npx playwright test --ui          # modo interactivo
 *   npx playwright show-report        # reporte HTML tras correr
 */
export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "html",
  use: {
    baseURL: "http://localhost:5173",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:5173",
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
