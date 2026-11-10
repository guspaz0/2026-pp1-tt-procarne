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

    // Grupos esperados: unique CUITs.
    const cuitsUnicos = [...new Set(operadores.map((o) => o.cuit.toUpperCase()))];

    // El encabezado muestra el total de personas y sucursales.
    await expect(
      page.getByText(
        new RegExp(`${cuitsUnicos.length} personas? titular`),
      ),
    ).toBeVisible();

    // Cada persona (CUIT único) tiene su card.
    for (const cuit of cuitsUnicos) {
      await expect(
        page.getByText(new RegExp(`CUIT: ${cuit.toUpperCase()}`, "i")).first(),
      ).toBeVisible();
    }

    // Cada sucursal aparece dentro de su grupo.
    for (const op of operadores) {
      await expect(
        page.getByRole("listitem").getByText(op.razon_social).first(),
      ).toBeVisible();
    }
  });
});
