/**
 * Utilidad de render reutilizable para tests de integración (Vitest + RTL).
 *
 * Sigue el patrón "renderWithProviders" de la guía de testing de Redux:
 * - Crea un store FRESCO por cada render (o acepta uno ya creado).
 * - Envuelve el componente en <Provider store={...}> (y en <MemoryRouter>
 *   si el componente usa react-router).
 * - Devuelve `store` para que el test pueda dispatchear acciones o
 *   inspeccionar el estado después de interactuar.
 *
 * Uso:
 *
 *   import { renderWithProviders } from "../../tests/render";
 *
 *   const { user, store } = renderWithProviders(<PadronSucursales />, {
 *     preloadedState: { ... },   // opcional: estado inicial de slices
 *     withRouter: true,          // opcional: envolver en MemoryRouter
 *   });
 *   expect(store.getState().auth.usuario).toBeNull();
 */
import React, { type PropsWithChildren } from "react";
import { render, type RenderOptions } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { Provider } from "react-redux";
import { MemoryRouter, type RouterProps } from "react-router-dom";
import { setupStore, type AppStore, type RootState } from "../src/store/store";

/** Opciones extendidas sobre el `render` estándar de RTL. */
export interface RenderWithProvidersOptions
  extends Omit<RenderOptions, "wrapper"> {
  /** Estado inicial para los slices (p. ej. `formF102`, `auth`). */
  preloadedState?: Partial<RootState>;
  /** Store ya creado (si se pasa, `preloadedState` se ignora). */
  store?: AppStore;
  /** Envolver el componente en <MemoryRouter> (componentes con router). */
  withRouter?: boolean;
  /** Props del MemoryRouter (initialEntries, etc.). */
  routerProps?: RouterProps;
}

export interface RenderWithProvidersResult {
  /** Store creado para este render (para dispatch/inspección posterior). */
  store: AppStore;
  /** Instancia de user-event preconfigurada. */
  user: ReturnType<typeof userEvent.setup>;
}

/**
 * Renderiza un componente conectado a Redux con un store fresco por test.
 */
export function renderWithProviders(
  ui: React.ReactElement,
  options: RenderWithProvidersOptions = {},
) {
  const {
    preloadedState,
    store,
    withRouter = false,
    routerProps,
    ...renderOptions
  } = options;

  // Store fresco por test: evita que el cache de RTK Query se filtre.
  const storeInstance = store ?? setupStore(preloadedState);

  const Wrapper = ({ children }: PropsWithChildren) => {
    let tree: React.ReactElement = (
      <Provider store={storeInstance}>{children}</Provider>
    );
    if (withRouter) {
      tree = <MemoryRouter {...routerProps}>{tree}</MemoryRouter>;
    }
    return tree;
  };

  return {
    store: storeInstance,
    user: userEvent.setup(),
    ...render(ui, { wrapper: Wrapper as RenderOptions["wrapper"], ...renderOptions }),
  };
}
