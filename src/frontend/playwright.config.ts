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
  testMatch: /.*\.spec\.ts/,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "retain-on-failure",
    // Pantalla al FINAL de cada test (pasa y falla).
    screenshot: "on",
    // Sesión compartida: auth.setup.ts loguea y guarda la cookie HttpOnly
    // en este storageState; todos los tests la reutilizan (la API exige
    // autenticación vía middleware de InsForge).
    storageState: "tests/e2e/.auth/user.json",
  },
  projects: [
    {
      // Login de prueba: corre solo una vez, antes del resto de la suite.
      name: "setup",
      testMatch: /auth\.setup\.ts$/,
    },
    {
      name: "chromium",
      testIgnore: /auth\.setup\.ts$/,
      use: {
        ...devices["Desktop Chrome"],
        // El headless shell del sandbox está incompleto (sin ICU: icudtl.dat
        // no found) y la cache de browsers (~/Library/Caches/ms-playwright)
        // no es legible desde el sandbox. Se usa el Edge instalado vía
        // `channel` (resuelve la app por nombre, sin leer la cache).
        // IMPORTANTE: cerrá Edge antes de correr (el profile queda bloqueado
        // por ProcessSingleton si hay una instancia abierta).
        channel: "msedge",
      },
    },
  ],
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:5173",
    reuseExistingServer: true,
    timeout: 60_000,
  },
});

// No usamos globalSetup: el project `setup` (auth.setup.ts) loguea y
// persiste el storageState que el project `chromium` reutiliza.
