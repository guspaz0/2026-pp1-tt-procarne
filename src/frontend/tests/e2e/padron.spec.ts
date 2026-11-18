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
  test("renderiza los operadores devueltos por la API", async ({ page }) => {
    // Los tests corren EN PARALELO y otros specs (inscripción, jerarquía)
    // crean operadores sobre la misma BD mientras este test lee. Por eso NO
    // se puede tomar el conteo por API y luego afirmar que la página lo
    // refleja: entre el GET y el render, el número puede cambiar. En vez de
    // eso, se valida la CONSISTENCIA INTERNA de la página: el contador del
    // encabezado debe igualar el número de filas de datos renderizadas (y el
    // de la tab). Esto es cierto en CUALQUIER momento, haya 0 o N operadores.
    await page.goto("/operadores/padron");

    // Espera a que termine de cargar (ni "Cargando…" ni error en el tbody).
    const cuerpo = page.locator("tbody");
    await expect(cuerpo).not.toHaveText(/Cargando padrón|Error al cargar/);

    // El encabezado SIEMPRE se muestra ("N establecimiento(s) …"),
    // incluso con N=0 (donde además aparece el aviso de estado vacío).
    const encabezado = page.getByText(/\d+\s+establecimiento/);
    await expect(encabezado.first()).toBeVisible();

    const nPagina = Number(
      (await encabezado.first().innerText()).match(/(\d+)\s+establecimiento/)?.[1] ?? 0,
    );

    // Filas de datos = filas del tbody que no son el aviso de estado vacío.
    const filasDatos = page.locator("tbody tr").filter({
      hasNot: page.getByText(/No hay operadores|Aún no tiene operadores/),
    });

    // 1) Consistencia interna: el contador refleja las filas reales.
    await expect(filasDatos).toHaveCount(nPagina);

    // 2) La tab "Padrón" muestra el mismo total que el encabezado.
    await expect(
      page.getByRole("link", { name: /Padrón de Operadores/ }),
    ).toContainText(String(nPagina));
  });

  test("filtra por razón social / CUIT y limpia el filtro", async ({
    page,
    request,
  }) => {
    const resp = await request.get("/api/registro-operadores");
    const operadores = (await resp.json()) as Array<{
      establecimiento_fantasia: string;
      cuit: string;
    }>;
    if (operadores.length === 0) return;

    // Busca un operador cuyo CUIT sea ÚNICO en la BD: el test filtra por
    // CUIT y espera que quede una sola fila, así que no sirve cualquier
    // operador (la BD puede tener varios con el mismo CUIT).
    const conteo = new Map<string, number>();
    for (const o of operadores) {
      const c = o.cuit.toUpperCase();
      conteo.set(c, (conteo.get(c) ?? 0) + 1);
    }
    const objetivo = operadores.find((o) => (conteo.get(o.cuit.toUpperCase()) ?? 0) === 1);
    if (!objetivo) return; // No hay ningún CUIT único: no se puede probar el filtro.

    await page.goto("/operadores/padron");

    // Espera a que la tabla esté poblada antes de filtrar.
    await expect(
      page.getByRole("row").getByText(objetivo.establecimiento_fantasia).first(),
    ).toBeVisible();

    // Busca un CUIT único: debe quedar solo esa fila.
    const busqueda = page.getByPlaceholder(/Buscar por N° Cartón/);
    await busqueda.fill(objetivo.cuit);

    const filas = page.getByRole("row").filter({
      hasText: objetivo.establecimiento_fantasia,
    });
    await expect(filas).toHaveCount(1);

    // Limpiar el filtro restaura la lista completa.
    await busqueda.fill("");
    await expect(
      page.getByRole("row").getByText(objetivo.establecimiento_fantasia).first(),
    ).toBeVisible();
  });

  test("abre y cierra el Cartón F 102 desde la tabla", async ({ page }) => {
    await page.goto("/operadores/padron");

    // La primera fila de datos (skip el header) es la que usamos. El N° de
    // cartón (100000+id) aparece en la primera celda, así que leemos el id
    // DESDE LA PÁGINA (no de una API call aparte que pueda desfasarse con el
    // re-fetch de la página cuando otros tests crean operadores en paralelo).
    const filas = page.getByRole("row");
    await expect(filas).not.toHaveCount(0);
    const primera = filas.nth(1);
    await expect(primera).toBeVisible();

    // El N° de cartón es la primera celda; extraemos el número para armar
    // el aria-label del modal esperado.
    const numeroTexto = (await primera.locator("td").first().innerText()).trim();
    const numero = parseInt(numeroTexto.replace(/[^0-9]/g, ""), 10);
    if (Number.isNaN(numero)) return;

    await primera.getByRole("button", { name: /Ver F102/ }).click();

    const modal = page.getByRole("dialog", {
      name: new RegExp(`Cartón F 102 ${numero}`),
    });
    await expect(modal).toBeVisible();
    // El contenido es un <iframe> con el PDF: verificá que carga (no queda en
    // "Generando…" ni en estado de error) y que muestra el número del cartón.
    await expect(modal).toContainText(`N° ${numero}`);
    await expect(
      modal.getByText(/Generando Cartón F 102/),
    ).toHaveCount(0);

    // El botón de cierre tiene aria-label="Cerrar" (el "✕" es solo texto
    // visible). Hay otro botón "Cerrar" dentro del viewer del PDF → .first().
    await modal.getByRole("button", { name: "Cerrar" }).first().click();
    await expect(modal).toBeHidden();
  });

  test("el botón Ver Cartón del PageHeader abre el cartón del primer operador", async ({
    page,
  }) => {
    await page.goto("/operadores/padron");

    // Igual que arriba: leemos el N° de cartón de la primera fila desde la
    // propia página, no de una API call aparte.
    const filas = page.getByRole("row");
    await expect(filas).not.toHaveCount(0);
    const primera = filas.nth(1);
    await expect(primera).toBeVisible();

    const numeroTexto = (await primera.locator("td").first().innerText()).trim();
    const numero = parseInt(numeroTexto.replace(/[^0-9]/g, ""), 10);
    if (Number.isNaN(numero)) return;

    await page
      .getByRole("button", { name: /Ver Cartón F 102 Original/ })
      .click();

    await expect(
      page.getByRole("dialog", {
        name: new RegExp(`Cartón F 102 ${numero}`),
      }),
    ).toBeVisible();
  });
});
