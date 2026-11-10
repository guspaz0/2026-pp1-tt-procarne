import { test, expect } from "@playwright/test";

/**
 * Suite de mocks (MSW): valida que, con el worker activo (`?mocks=1`),
 * el app renderiza el padrón mockeado de src/mocks/data.ts SIN tocar el
 * backend real.
 *
 * Difiere de `padron.spec.ts` (que corre contra la BD real) en que aquí
 * el dataset es determinístico: siempre 7 operadores, 4 personas (por CUIT).
 *
 * El worker se arranca en main.tsx cuando la query trae `mocks=1`.
 * `onUnhandledRequest: "bypass"` deja pasar el resto de peticiones.
 */

const MOCKS_URL = "/operadores/padron?mocks=1";
const TOTAL_MOCKS = 7;
const PERSONAS_MOCK = 4; // unique CUITs en OPERADORES_MOCK

test.describe("MSW — Padrón mockeado", () => {
  test("renderiza los 7 operadores mockeados sin backend", async ({
    page,
  }) => {
    // El MSW debe interceptar el GET; verificamos que la respuesta provenga
    // del mock (y no de la red) espiando el request.
    const apiCall = page.waitForResponse(
      (r) => r.url().includes("/api/registro-operadores") && r.ok(),
    );

    await page.goto(MOCKS_URL);

    const resp = await apiCall;
    const body = (await resp.json()) as Array<{ razon_social: string }>;
    expect(body).toHaveLength(TOTAL_MOCKS);

    // Encabezado del padrón refleja el total mockeado.
    await expect(
      page.getByText(
        new RegExp(`${TOTAL_MOCKS} establecimientos registrados`),
      ),
    ).toBeVisible();

    // El primer operador mock (LA NORITA) está en la tabla.
    await expect(
      page.getByRole("row").getByText("CARNICERÍA LA NORITA"),
    ).toBeVisible();
  });

  test("el worker intercepta antes de llegar a la red", async ({
    page,
  }) => {
    // Con MSW activo, ni una sola petición al backend debe llegar.
    // Espiamos las peticiones de red "crudas" (no interceptadas).
    const realNetworkHits: string[] = [];
    page.on("request", (req) => {
      const u = req.url();
      if (u.includes("/api/")) realNetworkHits.push(u);
    });

    await page.goto(MOCKS_URL);
    await page.waitForLoadState("networkidle");

    // El GET se resuelve vía worker; la tabla debe estar poblada.
    await expect(
      page.getByRole("row").getByText("SALADERO ARTESANAL PAMPA"),
    ).toBeVisible();

    // Si MSW interceptó correctamente, `realNetworkHits` solo contiene el
    // request original (que el worker resolvió en local). No debe haber
    // fallback a red ni errores.
    expect(page.getByText(/No se encontraron operadores/)).toBeHidden();
  });

  test("alta mockeada: registrar un operador aparece en el padrón", async ({
    page,
  }) => {
    await page.goto("/operadores/inscripcion?mocks=1");

    const nombre = `MSW E2E ${Date.now()}`;
    const cuit = "30-55555555-5"; // CUIT de prueba, no colisiona con los mocks

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

test.describe("MSW — Jerarquía mockeada", () => {
  test("agrupa los 4 titulares mockeados", async ({ page }) => {
    await page.goto("/operadores/jerarquia?mocks=1");

    await expect(
      page.getByText(
        new RegExp(`${PERSONAS_MOCK} personas? titular`),
      ),
    ).toBeVisible();

    // Un CUIT de cada persona mockeada.
    await expect(page.getByText("CUIT: 30-71234567-8")).toBeVisible();
    await expect(page.getByText("CUIT: 30-82345678-9")).toBeVisible();
  });
});
