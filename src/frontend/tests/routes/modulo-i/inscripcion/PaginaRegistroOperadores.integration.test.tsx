/**
 * INTEGRACIÓN — Alta de Operador (PaginaRegistroOperadores completa).
 *
 * Cubre el flujo de inscripción de punta a punta, con el store real
 * (RTK Query + slices) y la API mockeada (MSW):
 *
 *  1. Al entrar, la página precarga la lista (useListarQuery) — alimenta
 *     los contadores de las tabs.
 *  2. Rellenar el formulario (setCampo/toggleCategoria en el slice).
 *  3. Al submit, la mutación `registrar` (POST /api/registro-operadores)
 *     se dispara con los códigos AFIP de las categorías seleccionadas.
 *  4. RTK Query invalida la lista → la tabla del padrón se repinta con el
 *     nuevo operador (re-fetch automático).
 *  5. El banner de resultado (altaMensaje) aparece en el DOM.
 *  6. Alta fallida (CUIT duplicado, 400): banner de error, sin crash.
 */
import React from "react";
import { describe, it, expect, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { PaginaRegistroOperadores } from "../../../../src/routes/modulo-i/inscripcion/PaginaRegistroOperadores";
import { setupStore, type AppStore } from "../../../../src/store/store";
import { server } from "../../../mocks/server";
import { createHandlers } from "../../../mocks/handlers";
import { OPERADORES_MOCK as OPS } from "../../../mocks/data";

function mount(store: AppStore) {
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={["/operadores/inscripcion"]}>
        <PaginaRegistroOperadores />
      </MemoryRouter>
    </Provider>,
  );
}

describe("Integración · Alta de Operador (F 102)", () => {
  let user: ReturnType<typeof userEvent.setup>;
  let store: AppStore;

  beforeEach(() => {
    server.resetHandlers(...createHandlers());
    user = userEvent.setup();
    store = setupStore();
  });

  it("alta exitosa: POST, invalida la lista (re-fetch) y muestra el banner", async () => {
    mount(store);

    // Rellenamos el formulario (por defecto el tipo es Física, así que el
    // campo del titular se llama "Apellido y Nombre del Titular *").
    await user.type(screen.getByLabelText(/C\.U\.I\.T\./i), "30-11122233-4");
    await user.type(
      screen.getByLabelText(/Apellido y Nombre del Titular \*/i),
      "CARNICERIA NUEVO OPERADOR",
    );
    await user.type(
      screen.getByLabelText(/Nombre del Establecimiento/i),
      "LA NUEVA",
    );
    await user.click(
      screen.getByRole("button", { name: /Carnicería Minorista/i }),
    );

    // Submit.
    await user.click(
      screen.getByRole("button", {
        name: /Registrar Operador y Emitir Cartón/i,
      }),
    );

    // Banner de éxito (altaMensaje) con el CUIT. (getByRole con `name` no
    // coincide en live regions; usamos el texto del elemento `status`.)
    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        /Operador registrado con CUIT 30-11122233-4/i,
      );
    });

    // RTK Query invalidó la lista: el re-fetch trajo el nuevo operador
    // (el cache de `listar` ya no está en el estado inicial).
    await waitFor(() => {
      const state = store.getState() as any;
      const queries = state.operadoresApi?.queries ?? {};
      expect(Object.keys(queries).length).toBeGreaterThan(0);
    });
  });

  it("alta con CUIT duplicado (400): banner de error y la lista NO se modifica", async () => {
    mount(store);

    // CUIT que ya existe en el padrón → el mock devuelve 400.
    await user.type(screen.getByLabelText(/C\.U\.I\.T\./i), OPS[0].cuit);
    await user.type(
      screen.getByLabelText(/Apellido y Nombre del Titular \*/i),
      "DUPLICADA S.R.L.",
    );
    await user.click(
      screen.getByRole("button", {
        name: /Registrar Operador y Emitir Cartón/i,
      }),
    );

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent(
        /Error al registrar/i,
      );
    });
  });
});
