/**
 * E2E contra el worker de MSW in-app (arrancado con `?mocks=1` en main.tsx).
 *
 * El service worker del navegador responde a /api/registro-operadores. Los
 * overrides por test se hacen vía `page.evaluate` sobre `window.__mswWorker`
 * (expuesto en main.tsx), p. ej. para simular error 500 o lista vacía.
 *
 * Correr:  npx playwright test tests/e2e/operadores.msw.spec.ts
 */
import { test, expect } from "@playwright/test";

const URL_PADRON = "/operadores/padron?mocks=1";
const URL_INSCRIPCION = "/operadores/inscripcion?mocks=1";

test.describe("E2E + worker MSW (in-app, ?mocks=1)", () => {
  test("muestra el padrón mockeado (handlers iniciales)", async ({ page }) => {
    await page.goto(URL_PADRON);
    await expect(page.getByText("CARNICERÍA LA NORITA").first()).toBeVisible();
    // El mock trae 7 operadores; el encabezado refleja el total.
    await expect(page.getByText(/7 establecimientos registrados/)).toBeVisible();
  });

  test("override por test: resetHandlers → lista vacía", async ({ page }) => {
    await page.goto(URL_PADRON);
    await expect(page.getByText("CARNICERÍA LA NORITA").first()).toBeVisible();
    // Override: quitamos los handlers por test → el GET no tiene respuesta
    // mockeada y el UI no muestra filas.
    await page.evaluate(() => (window as any).__mswWorker.resetHandlers());
    await page.reload();
    await expect(page.getByText("CARNICERÍA LA NORITA")).toHaveCount(0);
  });

  test("alta mockeada: registrar aparece en el padrón", async ({ page }) => {
    await page.goto(URL_INSCRIPCION);

    // CUIT único (no está en el seed del mock) para no chocar con el 409.
    const cuit = `30-9${Math.floor(10000000 + Math.random() * 89999999)}-5`;
    const establecimiento = `MSW SW ${Date.now()}`;
    await page.getByLabel(/C\.U\.I\.T/).fill(cuit);
    await page.getByLabel(/Apellido y Nombre del Titular/).fill("TITULAR PRUEBA");
    await page
      .getByLabel(/Nombre del Establecimiento|Fantasia/)
      .fill(establecimiento);
    await page
      .getByRole("button", { name: /Registrar Operador y Emitir Cartón/ })
      .click();

    // Confirmación de éxito (role="status").
    await expect(
      page
        .getByRole("status")
        .getByText(new RegExp(`Operador registrado con CUIT ${cuit}`)),
    ).toBeVisible();

    // El nuevo establecimiento aparece en el padrón (invalidation de RTK Query).
    await page.getByRole("link", { name: /Padrón de Operadores/ }).click();
    await expect(page.getByText(establecimiento)).toBeVisible();
  });
});
