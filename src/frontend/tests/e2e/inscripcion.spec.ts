import { test, expect, type Page } from "@playwright/test";

/**
 * Flujo completo: alta de un operador vía Formulario F 102.
 *
 * Crea un operador con CUIT aleatorio (idempotente por corrida) y verifica
 * que: (1) aparece el mensaje de éxito, (2) el operador se ve en el padrón
 * — lo que también valida la invalidación de tags del RTK Query tras el POST.
 */

/**
 * CUIT de persona jurídica válido (dígito verificador módulo 11).
 * El cuerpo aleatorio es único por corrida, así el test no colisiona con
 * datos previos.
 */
function cuitAleatorio(): string {
  const cuerpo = String(Math.floor(20_000_000_000 + Math.random() * 9_999_999_999));
  const pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2];
  const suma = pesos.reduce((acc, p, i) => acc + Number(cuerpo[i]) * p, 0);
  const verificador = (11 - (suma % 11)) % 11;
  const completo = `${cuerpo}${verificador}`;
  return `${completo.slice(0, 2)}-${completo.slice(2, 10)}-${completo.slice(10)}`;
}

/**
 * Completa el formulario en su estado inicial (persona física, CUIT 23-xxx).
 * `getByLabel` funciona porque TextField envuelve el input en un <label>.
 */
async function completarFormulario(page: Page, cuit: string, nombre: string) {
  await page.getByLabel(/C\.U\.I\.T/).fill(cuit);
  // Por defecto tipoPersona === "fisica" → el campo se llama "Apellido y Nombre del Titular".
  await page.getByLabel(/Apellido y Nombre del Titular/).fill(nombre);
  // Nombre del establecimiento (obligatorio: la API exige domicilio_comercial).
  await page.getByLabel(/Nombre del Establecimiento|Fantasia/).fill(`SUC. ${nombre}`);
  // Selecciona al menos una categoría cárnica (obligatorio).
  await page.getByRole("button", { name: /Carnicería Minorista/ }).click();
}

test.describe("Alta de operador (F 102)", () => {
  test("registra un operador y aparece en el padrón", async ({ page }) => {
    const cuit = cuitAleatorio();
    const nombre = `E2E TEST ${Date.now()}`;

    await page.goto("/operadores/inscripcion");

    await expect(
      page.getByRole("heading", { name: /Alta de Operador Cárnico/ }),
    ).toBeVisible();

    await completarFormulario(page, cuit, nombre);
    await page
      .getByRole("button", { name: /Registrar Operador y Emitir Cartón/ })
      .click();

    // Mensaje de éxito con el CUIT.
    await expect(
      page.getByRole("status").getByText(
        new RegExp(`Operador registrado con CUIT ${cuit}`),
      ),
    ).toBeVisible();

    // Navega al padrón: el nuevo operador debe estar renderizado
    // (valida invalidatesTags + selectItems). El nombre aparece en 2
    // celdas (establecimiento y persona titular) → .first().
    await page.getByRole("link", { name: /Padrón de Operadores/ }).click();
    await expect(
      page.getByText(nombre).first(),
    ).toBeVisible();
  });

  test("muestra error al registrar un CUIT duplicado", async ({
    page,
    request,
  }) => {
    const resp = await request.get("/api/registro-operadores");
    const existentes = (await resp.json()) as Array<{ cuit: string }>;
    if (existentes.length === 0) return;

    const cuitDuplicado = existentes[0].cuit;

    await page.goto("/operadores/inscripcion");
    await completarFormulario(page, cuitDuplicado, `DUP TEST ${Date.now()}`);
    await page
      .getByRole("button", { name: /Registrar Operador y Emitir Cartón/ })
      .click();

    await expect(
      page.getByRole("status").getByText(/Error al registrar/),
    ).toBeVisible();
  });
});

test.describe("Guard de autenticación", () => {
  test("redirige a /login si no hay sesión", async ({ page }) => {
    // Contexto sin el storageState de la sesión guardada.
    await page.context().clearCookies();

    await page.goto("/operadores/padron");

    // El guard de ruta redirige al login recordando la ruta de origen.
    await expect(page).toHaveURL(/\/login/);
  });
});
});
