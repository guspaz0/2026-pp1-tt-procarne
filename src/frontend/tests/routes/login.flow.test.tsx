/**
 * INTEGRACIÓN — Flujo de login (App completa: router + RTK Query + authSlice).
 *
 * Renderiza <App/> (con su <BrowserRouter>) sobre un store fresco por test y
 * verifica el comportamiento de usuario:
 *
 *  - La app redirige a /login cuando no hay sesión (cookie inválida, /me 401).
 *  - Con sesión (cookie válida, /me ok): el usuario aparece en el header.
 *  - Login exitoso: setSesion en el store + navegación a /operadores.
 *  - Login fallido: se muestra el error y NO se navega.
 *
 * La API se intercepta con MSW (tests/mocks).
 */
import React from "react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { MemoryRouter } from "react-router-dom";
import { setupStore, type AppStore } from "../../src/store/store";
import { server } from "../mocks/server";
import { createHandlers, USUARIO_MOCK } from "../mocks/handlers";

/**
 * Monta <AppRoutes> (sin BrowserRouter) dentro de un MemoryRouter con la
 * entrada inicial indicada, sobre el store indicado.
 */
function mount(routes: React.ReactNode, store: AppStore, entry = "/") {
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[entry]}>{routes}</MemoryRouter>
    </Provider>,
  );
}

// Importamos AppRoutes (las rutas) en vez de App (que trae su BrowserRouter)
// para poder controlar la ruta inicial con MemoryRouter.
import { AppRoutes } from "../../src/AppRoutes";

describe("Integración · Login", () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    server.resetHandlers(...createHandlers());
    vi.restoreAllMocks();
    user = userEvent.setup();
  });

  it("sin sesión, redirige a /login y muestra el formulario", async () => {
    // /me devuelve 401 → sin sesión.
    server.use(...createHandlers({ unauthenticated: true }));
    const store = setupStore();
    mount(<AppRoutes />, store, "/operadores");

    // La ruta protegida redirige a /login: el formulario es visible.
    const email = await screen.findByLabelText(/Email/);
    expect(email).toBeInTheDocument();
    expect(screen.getByLabelText(/Contraseña/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Ingresar/i })).toBeInTheDocument();

    // Sin sesión: el store no tiene usuario.
    expect(store.getState().auth.usuario).toBeNull();
  });

  it("con sesión activa, muestra el usuario en el header", async () => {
    // /me devuelve el usuario → sesión válida.
    const store = setupStore();
    mount(<AppRoutes />, store, "/operadores");

    await waitFor(() => {
      expect(store.getState().auth.usuario?.email).toBe(USUARIO_MOCK.email);
    });
    // El header muestra el email del usuario.
    expect(await screen.findByText(/test@rocca\.gob\.ar/i)).toBeInTheDocument();
  });

  it("login exitoso: guarda la sesión en el store y navega al padrón", async () => {
    const store = setupStore();
    mount(<AppRoutes />, store, "/login");

    await user.type(await screen.findByLabelText(/Email/), USUARIO_MOCK.email);
    await user.type(screen.getByLabelText(/Contraseña/), "rocca-2026");
    await user.click(screen.getByRole("button", { name: /Ingresar/i }));

    // setSesion se dispara: el store tiene el usuario.
    await waitFor(() => {
      expect(store.getState().auth.usuario?.email).toBe(USUARIO_MOCK.email);
    });

    // Se navegó a /operadores: el formulario de login desapareció.
    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /Ingresar/i })).toBeNull();
    });
    expect(screen.queryByLabelText(/Contraseña/)).toBeNull();
    // El header del módulo muestra el usuario.
    expect(screen.getByRole("button", { name: /Salir/i })).toBeInTheDocument();
  });

  it("login fallido: muestra el error y permanece en /login", async () => {
    server.use(
      ...createHandlers({
        loginResponse: {
          status: 400,
          body: { detail: "Credenciales inválidas" },
        },
      }),
    );
    const store = setupStore();
    mount(<AppRoutes />, store, "/login");

    await user.type(await screen.findByLabelText(/Email/), "bad@user.gob.ar");
    await user.type(screen.getByLabelText(/Contraseña/), "clave-mala");
    await user.click(screen.getByRole("button", { name: /Ingresar/i }));

    await waitFor(() => {
      expect(screen.getByText(/Credenciales inválidas/i)).toBeInTheDocument();
    });

    // No se autenticó: el store sigue vacío y el formulario visible.
    expect(store.getState().auth.usuario).toBeNull();
    expect(screen.getByRole("button", { name: /Ingresar/i })).toBeInTheDocument();
  });
});
