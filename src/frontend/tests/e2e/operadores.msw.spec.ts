/**
 * E2E con MSW a nivel de Playwright (@msw/playwright).
 *
 * A diferencia de mocks.spec.ts (worker in-app `?mocks=1`), aquí MSW
 * intercepta a nivel de Playwright: no hay service worker ni código de MSW
 * en la app. Esto permite overrides POR TEST (error 500, lista vacía, etc.).
 *
 * Correr:  npx playwright test tests/e2e/operadores.msw.spec.ts
 */
import { http, HttpResponse } from "msw";
import { test, expect } from "./fixtures";

test.describe("E2E + @msw/playwright", () => {
  test("muestra el padrón mockeado (handlers iniciales)", async ({ page }) => {
    await page.goto("/operadores/padron");
    await expect(page.getByText("CARNICERÍA LA NORITA")).toBeVisible();
    await expect(
      page.getByText("7 establecimientos registrados"),
    ).toBeVisible();
  });

  test("override por test: lista vacía", async ({ page, network }) => {
    network.use(
      http.get("/api/registro-operadores", () => HttpResponse.json([])),
    );
    await page.goto("/operadores/padron");
    await expect(
      page.getByText(/No se encontraron operadores/),
    ).toBeVisible();
  });

  test("override por test: la API falla (500)", async ({ page, network }) => {
    network.use(
      http.get(
        "/api/registro-operadores",
        () => new HttpResponse(null, { status: 500 }),
      ),
    );
    await page.goto("/operadores/padron");

    // RTK Query marca el query en error; el UI no debe mostrar la tabla
    // con datos ni el estado de carga perpetuo.
    await expect(page.getByText("CARNICERÍA LA NORITA")).toBeHidden();
  });

  test("alta mockeada: registrar aparece en el padrón", async ({ page }) => {
    await page.goto("/operadores/inscripcion");

    const nombre = `MSW PW ${Date.now()}`;
    const cuit = "30-77777777-7";
    await page.getByLabel(/C\.U\.I\.T/).fill(cuit);
    await page.getByLabel(/Apellido y Nombre del Titular/).fill(nombre);
    await page.getByRole("button", { name: /Carnicería Minorista/ }).click();
    await page
      .getByRole("button", { name: /Registrar Operador y Emitir Cartón/ })
      .click();

    await expect(
      page.getByRole("status").getByText(new RegExp(`CUIT ${cuit}`)),
    ).toBeVisible();

    await page.getByRole("link", { name: /Padrón de Operadores/ }).click();
    await expect(page.getByRole("row").getByText(nombre)).toBeVisible();
  });
});
