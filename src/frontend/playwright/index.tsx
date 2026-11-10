/**
 * Entry point de Playwright Component Testing (CT).
 *
 * `beforeMount` se llama antes de CADA montaje de componente: arranca MSW
 * una sola vez por worker (el SW es global) y crea un store FRESCO por test
 * para evitar fugas de cache de RTK Query entre tests.
 *
 * El componente a montar se pasa en cada spec:
 *   await mount(<PadronSucursales onVerCarton={() => {}} />)
 */
import { beforeMount } from "@playwright/experimental-ct-react/hooks";
import { Provider } from "react-redux";
import { setupStore, type RootState } from "../src/store/store";
import { worker } from "../src/mocks/browser";

/** Config que cada test puede pasar a `mount<HooksConfig>(...)`. */
export type HooksConfig = {
  /** Estado inicial para los slices (p. ej. `formF102`). */
  preloadedState?: Partial<RootState>;
};

let started: Promise<unknown> | undefined;

beforeMount<HooksConfig>(async ({ App, hooksConfig }) => {
  // Arranca MSW una sola vez por worker (el service worker es global).
  started ??= worker.start({ onUnhandledRequest: "error", quiet: true });
  await started;
  // Store FRESCO por test: sin cache RTK Query residual.
  const store = setupStore(hooksConfig?.preloadedState);
  return (
    <Provider store={store}>
      <App />
    </Provider>
  );
});
