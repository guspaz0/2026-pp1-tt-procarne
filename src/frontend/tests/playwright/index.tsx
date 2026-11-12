/**
 * Entry point de Playwright Component Testing (CT) — ROCCA.
 *
 * `beforeMount` se llama antes de CADA montaje de componente:
 * - Intercepta peticiones HTTP con `page.route` (misma infra que
 *   `mockRoccaApi` en tests/ct-utils.ts; sin MSW, más confiable en CT)
 * - Crea un store FRESCO por test (evita fugas de cache de RTK Query)
 * - Expone el store al spec vía el fixture `store` (ver tests/ct-utils.ts)
 *
 * Los specs CT hacen:
 *   import { test, expect } from "../../tests/ct-utils";
 *   test("...", async ({ mount, store }) => {
 *     await mount(<Componente />, { preloadedState: {...} });
 *   });
 */
import { beforeMount } from "@playwright/experimental-ct-react/hooks";
import { Provider } from "react-redux";
import { setupStore } from "../../src/store/store";
import { mockRoccaApi, type HooksConfig, type WithStore } from "../ct-utils";

export type { HooksConfig, WithStore } from "../ct-utils";

beforeMount<HooksConfig & WithStore>(async ({ App, page, hooksConfig }) => {
  // Rutas mockeadas de la API (padrón, f102, auth) según la config del test.
  await mockRoccaApi(page, hooksConfig);

  // Store FRESCO por test: sin cache RTK Query residual.
  const store = setupStore(hooksConfig?.preloadedState);

  // `store` queda disponible en el fixture del spec (ver WithStore).
  (hooksConfig as WithStore).store = store;

  return <Provider store={store}>{App}</Provider>;
});
