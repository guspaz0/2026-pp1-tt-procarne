/**
 * Component Test (CT) para el Padrón de Sucursales.
 *
 * Monta el componente en un browser real con un store fresco por test
 * (ver playwright/index.tsx) y MSW respondiendo a /api/registro-operadores
 * con los mocks de src/mocks/data.ts (7 operadores).
 *
 * Correr:  npx playwright test -c playwright-ct.config.ts
 */
import { test, expect } from "@playwright/experimental-ct-react";
import type { HooksConfig } from "../../../playwright";
import { PadronSucursales } from "./PadronSucursales";

test("renderiza los 7 operadores mockeados", async ({ mount }) => {
  const component = await mount<HooksConfig>(<PadronSucursales />);

  // El mock sirve 7 establecimientos; el encabezado refleja el total.
  await expect(
    component.getByText("7 establecimientos registrados"),
  ).toBeVisible();

  // El primer operador mock (LA NORITA) está en la tabla.
  await expect(component.getByText("CARNICERÍA LA NORITA")).toBeVisible();
});

test("filtra por CUIT del operador mockeado", async ({ mount }) => {
  const component = await mount<HooksConfig>(<PadronSucursales />);

  // CUIT de LA NORITA en el mock.
  await component.getByPlaceholder(/Buscar por N° Cartón/).fill("30-71234567-8");
  await expect(component.getByText("CARNICERÍA LA NORITA")).toBeVisible();

  // Un CUIT de otra persona no aparece.
  await expect(component.getByText("FRIGORÍFICO EL TRUFO S.R.L.")).toBeHidden();
});
