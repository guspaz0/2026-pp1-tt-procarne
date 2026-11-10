import { test, expect } from "@playwright/test";

/**
 * Sanity: la app carga, el header ROCCA aparece y el login funciona.
 *
 * Con la sesión guardada por `auth.setup.ts` (storageState), la ruta raíz
 * redirige al padrón de operadores; sin sesión, redirige al login.
 */
test.describe("Shell de la aplicación", () => {
  test("carga el header ROCCA y redirige de / al padrón", async ({ page }) => {
    await page.goto("/");

    // Redirect / -> /operadores -> /operadores/padron (con sesión activa).
    await expect(page).toHaveURL(/\/operadores\/padron$/);

    // Header global
    await expect(page.getByRole("banner")).toContainText("ROCCA");

    // Tabs del módulo I
    await expect(
      page.getByRole("link", { name: /Padrón de Operadores/ }),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: /Jerarquía/ }),
    ).toBeVisible();
  });

  test("navega entre las sub-rutas del módulo I", async ({ page }) => {
    await page.goto("/operadores/padron");

    await page
      .getByRole("link", { name: /Jerarquía: Personas y Sucursales/ })
      .click();
    await expect(page).toHaveURL(/\/operadores\/jerarquia$/);
    await expect(
      page.getByRole("heading", { name: /Jerarquía/ }),
    ).toBeVisible();

    await page
      .getByRole("link", { name: /Formulario de Inscripción/ })
      .click();
    await expect(page).toHaveURL(/\/operadores\/inscripcion$/);
    await expect(
      page.getByRole("heading", { name: /Alta de Operador Cárnico/ }),
    ).toBeVisible();
  });
});
