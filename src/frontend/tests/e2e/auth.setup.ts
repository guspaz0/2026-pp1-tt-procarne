import { test as setup, expect } from "@playwright/test";

/**
 * Setup global de autenticación (auth.setup.ts).
 *
 * Corre ANTES del resto de la suite (ver `globalSetup` en playwright.config.ts)
 * y deja una sesión activa (cookie HttpOnly `rocca_access_token`) en el
 * `storageState` compartido, que los tests de E2E reutilizan.
 *
 * Requiere una cuenta de prueba existente en InsForge, configurada vía
 * variables de entorno:
 *   ROCCA_E2E_EMAIL / ROCCA_E2E_PASSWORD
 *
 * Si no están definidas, el setup deja el storageState vacío y los tests
 * que dependen de sesión fallan (el middleware devuelve 401).
 */

const STATE_PATH = "tests/e2e/.auth/user.json";

setup("loguea el usuario de prueba y guarda el storageState", async ({ page }) => {
  const email = process.env.ROCCA_E2E_EMAIL;
  const password = process.env.ROCCA_E2E_PASSWORD;
  if (!email || !password) {
    // Sin credenciales no hay sesión: se deja un storageState vacío.
    await setup.fixtures.page.context().storageState({ path: STATE_PATH });
    return;
  }

  await page.goto("/login");
  await page.getByLabel(/Email/).fill(email);
  await page.getByLabel(/^Contraseña$/).fill(password);
  await page.getByRole("button", { name: /Ingresar/ }).click();

  // Tras el login, la app redirige a /operadores (o a la ruta de origen).
  await expect(page).toHaveURL(/\/operadores/, { timeout: 15_000 });

  // La cookie de acceso (HttpOnly) queda guardada en el storageState.
  await page.context().storageState({ path: STATE_PATH });
});
