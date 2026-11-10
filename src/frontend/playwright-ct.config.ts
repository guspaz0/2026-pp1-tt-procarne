/**
 * Playwright Component Testing (CT) para ROCCA.
 *
 * Montará componentes React en un browser real con un store de Redux fresco
 * por test, y MSW (service worker) respondiendo a las peticiones de la API.
 *
 * Uso:
 *   npx playwright test -c playwright-ct.config.ts
 *
 * Los specs CT viven en src/ (testMatch *.ct.spec.tsx). El entry point de CT
 * es `playwright/index.tsx` (beforeMount con Provider + worker.start).
 *
 * `ctViteConfig` usa el Vite 5 + plugin-react 4.7 del proyecto (el harness de
 * CT trae por defecto un Vite/plugin-react más nuevo, incompatible con Vite 5).
 */
import { defineConfig, devices } from "@playwright/experimental-ct-react";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";

export default defineConfig({
  testDir: "./src",
  testMatch: "**/*.ct.spec.tsx",
  use: {
    ctPort: 3100,
    // El worker MSW se sirve desde public/ (mockServiceWorker.js).
    ctViteConfig: {
      publicDir: "public",
      plugins: [react(), tailwindcss()],
      resolve: {
        alias: {
          "@": fileURLToPath(new URL("./src", import.meta.url)),
        },
      },
    },
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
