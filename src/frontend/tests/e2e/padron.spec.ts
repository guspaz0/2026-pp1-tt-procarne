import { test, expect } from "@playwright/test";

/**
 * Padrón de Operadores — la suite que valida el selector RTK Query:
 * los operadores deben SERVENIR (fetched) Y RENDERIZARSE en la tabla.
 *
 * Requiere backend FastAPI corriendo en :8000 con datos en la tabla
 * `operadores` (la misma que lee la API /api/registro-operadores).
 *
 * La API exige sesión (middleware de autenticación): la cookie de prueba
 * la provee `auth.setup.ts` vía `storageState` (ver playwright.config.ts).
 */
test.describe("Padrón de Operadores", () => {
  test("renderiza los operadores devueltos por la API", async ({
    page,
    request,
  }) => {
    // Baseline: cuántos operadores tiene la API.
    const resp = await request.get("/api/registro-operadores");
    expect(resp.ok()).toBeTruthy();
    const operadores = (await resp.json()) as Array<{
      id: number;
      cuit: string;
      razon_social: string;
    }>;

    await page.goto("/operadores/padron");

    if (operadores.length === 0) {
      // Sin datos en la BD: al menos no debe mostrar error de carga.
      await expect(
        page.getByText(/No se encontraron operadores/),
      ).toBeVisible();
      return;
    }

    // 1) El contador del encabezado refleja el total.
    await expect(
      page.getByText(
        new RegExp(`${operadores.length} establecimientos registrados`),
      ),
    ).toBeVisible();

    // 2) La fila de CADA operador devuelto por la API está renderizada.
    //    (Antes del fix, queries["listar"] era undefined → 0 filas.)
    for (const op of operadores) {
      await expect(
        page.getByRole("row").getByText(op.razon_social).first(),
      ).toBeVisible();
    }

    // 3) El contador de la tab "Padrón" muestra el total.
    const tabPadron = page.getByRole("link", {
      name: /Padrón de Operadores/,
    });
    await expect(tabPadron).toContainText(String(operadores.length));
  });

  test("filtra por razón social / CUIT y limpia el filtro", async ({
    page,
    request,
  }) => {
    const resp = await request.get("/api/registro-operadores");
    const operadores = (await resp.json()) as Array<{
      razon_social: string;
      cuit: string;
    }>;
    if (operadores.length === 0) return;

    const objetivo = operadores[0];

    await page.goto("/operadores/padron");

    // Espera a que la tabla esté poblada antes de filtrar.
    await expect(
      page.getByRole("row").getByText(objetivo.razon_social).first(),
    ).toBeVisible();

    // Busca un CUIT único: debe quedar solo esa fila.
    const busqueda = page.getByPlaceholder(/Buscar por N° Cartón/);
    await busqueda.fill(objetivo.cuit);

    const filas = page.getByRole("row").filter({
      hasText: objetivo.razon_social,
    });
    await expect(filas).toHaveCount(1);

    // Limpiar el filtro restaura la lista completa.
    await busqueda.fill("");
    await expect(
      page.getByRole("row").getByText(objetivo.razon_social).first(),
    ).toBeVisible();
  });

  test("abre y cierra el Cartón F 102 desde la tabla", async ({ page, request }) => {
    const resp = await request.get("/api/registro-operadores");
    const operadores = (await resp.json()) as Array<{
      id: number;
      razon_social: string;
    }>;
    if (operadores.length === 0) return;

    await page.goto("/operadores/padron");

    const op = operadores[0];
    const fila = page.getByRole("row").getByText(op.razon_social).first();
    await expect(fila).toBeVisible();

    await fila
      .locator("xpath=ancestor::tr")
      .getByRole("button", { name: /Ver Cartón F 102/ })
      .click();

    const modal = page.getByRole("dialog", {
      name: new RegExp(`Cartón F 102 10${op.id}`),
    });
    await expect(modal).toBeVisible();
    await expect(modal).toContainText(op.razon_social);

    await modal.getByRole("button", { name: "✕" }).click();
    await expect(modal).toBeHidden();
  });

  test("el botón Ver Cartón del PageHeader abre el cartón del primer operador", async ({
    page,
    request,
  }) => {
    const resp = await request.get("/api/registro-operadores");
    const operadores = (await resp.json()) as Array<{
      id: number;
      razon_social: string;
    }>;
    if (operadores.length === 0) return;

    await page.goto("/operadores/padron");
    await expect(
      page.getByRole("row").getByText(operadores[0].razon_social).first(),
    ).toBeVisible();

    await page
      .getByRole("button", { name: /Ver Cartón F 102 Original/ })
      .click();

    await expect(
      page.getByRole("dialog", {
        name: new RegExp(`Cartón F 102 10${operadores[0].id}`),
      }),
    ).toBeVisible();
  });
});
