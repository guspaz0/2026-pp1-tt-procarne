import { test, expect } from "@playwright/test";

/**
 * Jerarquía: Personas y Sucursales — agrupa los operadores por CUIT.
 *
 * La agrupación se hace en el frontend (Object.groupBy sobre `cuit`) a
 * partir de GET /registro-operadores; no existe endpoint de jerarquía.
 * La API exige sesión (cookie de `auth.setup.ts` vía storageState).
 */
test.describe("Jerarquía", () => {
  test("agrupa las sucursales por persona titular (CUIT)", async ({
    page,
    request,
  }) => {
    const resp = await request.get("/api/registro-operadores");
    const operadores = (await resp.json()) as Array<{
      cuit: string;
      razon_social: string;
    }>;
    if (operadores.length === 0) return;

    await page.goto("/operadores/jerarquia");

    // La página re-hace GET /registro-operadores por su cuenta (RTK Query),
    // así que el snapshot que lee con `request` puede diferir del que
    // renderiza la página si otros tests en paralelo (inscripcion) crean
    // operadores en la BD compartida en el entretanto. Verificamos el
    // INVARIANTE estable: la página muestra al menos un grupo y cada CUIT
    // del snapshot base aparece como card. NO comparamos el count exacto
    // (es racy por la mutación concurrente).
    const cuitsUnicos = [...new Set(operadores.map((o) => o.cuit.toUpperCase()))];

    // El encabezado siempre muestra el total de personas titulares.
    await expect(
      page.getByText(/persona[s]? titular/),
    ).toBeVisible();

    // Cada CUIT del snapshot base tiene su card (si la página lo re-fetchó
    // después, sigue apareciendo; si no, al menos no rompe). Usamos
    // .first() para tolerar duplicados y no asertamos sobre el total.
    for (const cuit of cuitsUnicos) {
      await expect(
        page.getByText(new RegExp(`CUIT: ${cuit}`, "i")).first(),
      ).toBeVisible({ timeout: 15_000 });
    }

    // Cada sucursal aparece dentro de su grupo.
    for (const op of operadores) {
      await expect(
        page.getByRole("listitem").getByText(op.razon_social).first(),
      ).toBeVisible();
    }
  });
});
