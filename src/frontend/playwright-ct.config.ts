/**
 * Playwright Component Testing (CT) para ROCCA.
 *
 * Montará componentes React en un browser real con un store de Redux fresco
 * por test, y MSW (service worker) respondiendo a las peticiones de la API.
 *
 * Uso:
 *   npx playwright test -c playwright-ct.config.ts
 *
 * Los specs CT viven en tests/ (testMatch *.ct.spec.tsx). El entry point de CT
 * es `tests/playwright/index.tsx` (beforeMount con Provider + worker.start).
 *
 * NOTA sobre versiones: @playwright/experimental-ct-core trae su propio
 * Vite 8 + @vitejs/plugin-react 6.x, así que el app debe correr sobre Vite 6+
 * para que el plugin (que importa `vite/internal`) funcione. Si el proyecto
 * sigue en Vite 5, la capa CT no arranca (ver TESTING.md).
 */
import { defineConfig, devices } from "@playwright/experimental-ct-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.ct.spec.tsx",
  use: {
    ctPort: 3100,
    // Pantalla al FINAL de cada test (pasa y falla).
    screenshot: "on",
    // El worker MSW se sirve desde public/ (mockServiceWorker.js).
    // El plugin de React lo inyecta el framework de CT (plugin-react 6.x);
    // acá solo agregamos Tailwind (compatible con Vite 5..8).
    ctViteConfig: {
      publicDir: "public",
      plugins: [tailwindcss()],
    },
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        // El bundle de headless shell del sandbox está incompleto (sin ICU) y
        // cdn.playwright.dev está bloqueado por allowlist. Se usa el Edge
        // instalado en la máquina; sobreescribir con CHROMIUM_EXECUTABLE_PATH
        // o dejarlo vacío para el Chromium de Playwright (máquina normal).
        executablePath:
          process.env.CHROMIUM_EXECUTABLE_PATH ||
          "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
      },
    },
  ],
});
