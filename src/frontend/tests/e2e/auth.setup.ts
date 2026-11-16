import { test as setup, expect } from "@playwright/test";

/**
 * Setup global de autenticación (auth.setup.ts).
 *
 * Corre ANTES del resto de la suite (project `setup` con `dependencies` en
 * `playwright.config.ts`) y deja una sesión activa (cookie HttpOnly
 * `rocca_access_token`) en el `storageState` compartido, que los tests de E2E
 * reutilizan. (`globalSetup` es otra cosa: crea la BD temporal para el
 * backend, no el auth.)
 *
 * Requiere una cuenta de prueba existente en InsForge. Las credenciales se
 * toman de ROCCA_E2E_EMAIL / ROCCA_E2E_PASSWORD, leídas de:
 *   1. El entorno real (CI, neotest con `env` en el task, export en el shell).
 *   2. El archivo `src/frontend/.env` (fallback) — el CLI de Playwright NO
 *      carga .env por sí solo, así que lo leemos aquí manualmente para que
 *      `playwright test` funcione igual desde neotest, CI o a mano.
 *
 * Si no hay credenciales por ninguna vía, el setup deja el storageState
 * vacío ({} commitado) y los tests que dependen de sesión fallan con 401.
 */

import { readFileSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const STATE_PATH = "tests/e2e/.auth/user.json";

/**
 * Lee `KEY=VALUE` de `src/frontend/.env` si la variable no está ya en el
 * entorno. Así neotest-playwright (y cualquier otro invocador) hereda las
 * credenciales sin configuración extra. El entorno real siempre gana.
 */
function leerEnvDeDotenv(): void {
  if (process.env.ROCCA_E2E_EMAIL && process.env.ROCCA_E2E_PASSWORD) return;
  const __dirname = dirname(fileURLToPath(import.meta.url));
  const envPath = `${__dirname}/../../.env`;
  try {
    const contenido = readFileSync(envPath, "utf8");
    for (const linea of contenido.split("\n")) {
      const m = linea.match(/^\s*(ROCCA_E2E_(?:EMAIL|PASSWORD))\s*=\s*(.*)\s*$/);
      if (m && process.env[m[1]] === undefined) {
        // Quita comillas opcionales alrededor del valor.
        process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
      }
    }
  } catch {
    // Sin .env no hay credenciales: se deja el storageState vacío.
  }
}

setup("loguea el usuario de prueba y guarda el storageState", async ({ page }) => {
  leerEnvDeDotenv();
  const email = process.env.ROCCA_E2E_EMAIL;
  const password = process.env.ROCCA_E2E_PASSWORD;
  if (!email || !password) {
    // Sin credenciales no hay sesión: se deja un storageState vacío.
    // (El archivo ya existe commitado con {}, así que basta con no tocarlo.)
    return;
  }

  await page.goto("/login");
  await page.getByLabel(/Email/).first().fill(email);
  // El label es "Contraseña*" (TextField con `required` agrega el asterisco
  // sin espacio dentro del <label>).
  await page.getByLabel(/Contraseña\*?/).fill(password);
  await page.getByRole("button", { name: /Ingresar/ }).click();

  // Tras el login, la app redirige a /operadores (o a la ruta de origen).
  await expect(page).toHaveURL(/\/operadores/, { timeout: 15_000 });

  // La cookie de acceso (HttpOnly) queda guardada en el storageState.
  await page.context().storageState({ path: STATE_PATH });
});
