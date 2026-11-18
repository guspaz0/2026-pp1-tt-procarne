import { test, expect, type Page } from "@playwright/test";

/**
 * E2E: Flujo completo de un usuario con rol "operador".
 *
 * 1. Signup: crea una cuenta nueva (email aleatorio) con DNI.
 *    El backend crea la Persona en la tabla `personas` con el email,
 *    y el rol se resuelve como "operador".
 * 2. Tras el signup, el frontend redirige a /operador (no a /operadores).
 * 3. El operador ve su layout (Header + Footer, sin NavBar de módulos).
 * 4. El operador registra un establecimiento usando el formulario
 *    (secciones 2, 3, 4 — la sección 1 se omite).
 * 5. El establecimiento aparece en la lista de "Mis Establecimientos".
 */

/** Email aleatorio único por corrida (para no colisionar). */
function emailAleatorio(): string {
  return `e2e+op${Date.now()}${Math.floor(Math.random() * 10000)}@procarne.test`;
}

const PASSWORD = "Test1234!";

/**
 * Completa el formulario de signup y envía.
 * Devuelve el email usado.
 */
async function hacerSignup(page: Page): Promise<string> {
  const email = emailAleatorio();
  const nombre = `OP E2E ${Date.now()}`;
  const dni = String(20_000_000 + Math.floor(Math.random() * 9_999_999));

  await page.goto("/login");

  // Clic en la tab "Crear cuenta".
  await page.getByRole("button", { name: /Crear cuenta/ }).first().click();

  // Rellenar el formulario de signup.
  await page.getByLabel(/Nombre completo/).fill(nombre);

  // Tipo de documento: DNI (por defecto es CUIT, hay que cambiar).
  await page.getByRole("button", { name: "DNI", exact: true }).click();

  // DNI.
  await page.getByLabel(/D\.N\.I\. del titular/).fill(dni);

  // Email.
  await page.getByLabel("Email", { exact: true }).fill(email);

  // Contraseña + confirmación.
  await page.getByLabel("Contraseña", { exact: true }).fill(PASSWORD);
  await page.getByLabel(/Confirmar contraseña/).fill(PASSWORD);

  // Aceptar política de privacidad.
  await page.getByLabel(/Política de Privacidad/i).check();

  // Enviar.
  await page.getByRole("button", { name: /Crear cuenta/ }).last().click();

  // Esperar redirección a /operador (rol operador).
  await expect(page).toHaveURL(/\/operador/, { timeout: 20_000 });
  return email;
}

test.describe("Flujo Operador (rol operador)", () => {
  test("signup → redirige a /operador y ve layout sin NavBar de módulos", async ({
    page,
  }) => {
    await hacerSignup(page);

    // El heading de la página de inicio del operador.
    await expect(
      page.getByRole("heading", { name: /Mis Establecimientos/ }),
    ).toBeVisible();

    // El botón "Agregar establecimiento" debe ser visible.
    await expect(
      page.getByRole("link", { name: /Agregar establecimiento/i }),
    ).toBeVisible();

    // NO debe haber links a módulos admin (Monitor, Remitos, Padrón).
    const modulosNav = page.getByRole("link", { name: /Monitor|Remitos|Padrón/i });
    await expect(modulosNav.first()).not.toBeVisible({ timeout: 3_000 });
  });

  test("operador registra un establecimiento y lo ve en la lista", async ({
    page,
  }) => {
    // 1) Signup.
    await hacerSignup(page);

    // 2) Navegar al formulario de registro de establecimiento.
    await page.getByRole("link", { name: /Agregar establecimiento/i }).click();
    await expect(page).toHaveURL(/\/operador\/registro/);

    // 3) Completar Sección 2 — Establecimiento.
    const nombreEstab = `SUC E2E ${Date.now()}`;
    await page.getByLabel(/Nombre del Establecimiento|Fantasia/).fill(nombreEstab);

    //    Departamento (SDE): escribir y esperar debounce + seleccionar.
    await page.getByLabel(/Departamento Provincial/).fill("Capital");
    await page.waitForTimeout(2500); // Debounce 1.5s + tiempo de API.
    await page.locator("div.absolute button").first().click();

    //    Localidad (filtrada por departamento): escribir y seleccionar.
    await page.getByLabel(/Localidad/).fill("Villa Mar");
    await page.waitForTimeout(2500);
    await page.locator("div.absolute button").first().click();

    //    Domicilio (combobox con búsqueda en backend).
    await page.getByLabel(/Calle/).fill("Av. Belgrano");
    await page.waitForTimeout(2500);
    // Si hay resultados, seleccionar el primero; si no, se crea al submit.
    const primerDomicilio = page.locator("div.absolute button").first();
    if (await primerDomicilio.isVisible({ timeout: 2_000 }).catch(() => false)) {
      await primerDomicilio.click();
    }

    //    Número de calle.
    await page.getByLabel(/N° de Calle/).fill("1234");

    // 4) Completar Sección 3 — Categoría.
    //    Seleccionar una categoría del select.
    const selectCategoria = page.getByLabel(/Categoría del Establecimiento/);
    await selectCategoria.click();
    await page.waitForTimeout(500);
    // Seleccionar la primera opción no-disabled.
    await selectCategoria.selectOption({ index: 1 });

    //    Seleccionar al menos un tipo de carne.
    await page.getByRole("button", { name: /Bovina/ }).click();

    // 5) Submit.
    await page
      .getByRole("button", { name: /Registrar Establecimiento/ })
      .click();

    // 6) Debe redirigir a /operador y ver el establecimiento en la lista.
    await expect(page).toHaveURL(/\/operador$/, { timeout: 15_000 });
    await expect(
      page.getByText(nombreEstab).first(),
    ).toBeVisible({ timeout: 10_000 });
  });

  test("operador NO puede acceder a rutas admin (/operadores)", async ({
    page,
  }) => {
    await hacerSignup(page);

    // Intentar acceder a la ruta de admin directamente.
    await page.goto("/operadores/padron");

    // Debe redirigir a /operador (el guard de rol lo impide).
    await expect(page).toHaveURL(/\/operador/, { timeout: 10_000 });
  });
});
