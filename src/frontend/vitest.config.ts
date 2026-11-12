/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Config de Vitest — tests de integración del frontend ROCCA.
 *
 * Corren en jsdom (Node) con MSW interceptando la API. No requieren
 * navegador ni backend.
 *
 *   npx vitest run          # suite completa
 *   npx vitest              # modo watch
 */
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    include: ["src/**/*.test.{ts,tsx}", "tests/**/*.test.{ts,tsx}"],
    // Los specs de integración asertan sobre el DOM; los logs de React
    // (act warnings, MSW unhandled) son ruido en el reporte.
    silent: false,
    // Cada test usa su propio store (setupStore), sin estado global.
    restoreMocks: true,
    // RTK Query + user-event: dar algo de margen para los re-fetches.
    testTimeout: 10_000,
  },
});
