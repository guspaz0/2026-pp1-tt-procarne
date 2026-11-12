/**
 * INTEGRACIÓN — Padrón de Operadores (PadronSucursales + RTK Query + Redux).
 *
 * Verifica el flujo completo de la lista:
 *
 *  1. El componente dispara `useListarQuery` (RTK Query) → la lista llega
 *     desde la API mockeada (MSW) y se pinta en la tabla.
 *  2. El contador de establecimientos refleja la cantidad de items.
 *  3. Escribir en la caja de búsqueda dispatchea `setBusqueda` (slice) y la
 *     tabla se filtra en vivo (el selector `selectOperadoresFiltrados` cruza
 *     el cache de RTK Query con el estado del slice).
 *  4. Al vaciar la búsqueda, vuelve la lista completa.
 *  5. Si la API falla, se muestra el estado de error.
 *
 * Renderizamos el componente de la sección (sin AppLayout) pero CON el store
 * real de RTK Query, para probar la integración componente → API → Redux.
 */
import React from "react";
import { describe, it, expect, beforeEach } from "vitest";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { render } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { PadronSucursales } from "../../../../src/routes/modulo-i/padron/PadronSucursales";
import { setupStore, type AppStore } from "../../../../src/store/store";
import { server } from "../../../mocks/server";
import { createHandlers } from "../../../mocks/handlers";
import { OPERADORES_MOCK as OPS, crearOperadorMock } from "../../../mocks/data";

function mount(store: AppStore) {
  render(
    <Provider store={store}>
      <PadronSucursales />
    </Provider>,
  );
}

describe("Integración · Padrón de Operadores", () => {
  let user: ReturnType<typeof userEvent.setup>;
  let store: AppStore;

  beforeEach(() => {
    server.resetHandlers(...createHandlers());
    user = userEvent.setup();
    store = setupStore();
  });

  it("carga la lista desde la API (RTK Query) y la pinta en la tabla", async () => {
    mount(store);

    // Al llegar la respuesta de MSW, se pintan las filas.
    // La razón social aparece en dos celdas por fila (Establecimiento y
    // Persona Titular), por eso usamos getAllByText.
    await waitFor(() => {
      expect(screen.getAllByText(OPS[0].razon_social).length).toBeGreaterThan(0);
    }, { timeout: 3000 });

    // El contador de establecimientos refleja la cantidad de items.
    expect(screen.getByText(/establecimientos registrados/i)).toHaveTextContent(
      String(OPS.length),
    );

    // Cada operador de la API aparece en la tabla.
    for (const op of OPS) {
      expect(screen.getAllByText(op.razon_social).length).toBeGreaterThan(0);
    }
  });

  it("filtra la lista en vivo al escribir en la búsqueda (slice + selector)", async () => {
    // Sembramos un operador con un CUIT único para buscar.
    const unico = crearOperadorMock("30-99999999-9", "CARNICERIA UNICA TEST");
    server.use(...createHandlers({ operadores: [...OPS, unico] }));
    mount(store);

    await waitFor(() => {
      expect(screen.getAllByText("CARNICERIA UNICA TEST").length).toBeGreaterThan(0);
    });

    // Antes de filtrar: hay N+1 establecimientos.
    expect(screen.getByText(/establecimientos registrados/i)).toHaveTextContent(
      String(OPS.length + 1),
    );

    // Escribimos el CUIT único: solo queda esa fila.
    const input = screen.getByPlaceholderText(/Buscar por N° Cartón/i);
    await user.type(input, "30-99999999-9");

    await waitFor(() => {
      expect(screen.getAllByText("CARNICERIA UNICA TEST").length).toBeGreaterThan(0);
    });
    // Los demás operadores desaparecen de la tabla.
    expect(screen.queryAllByText(OPS[0].razon_social).length).toBe(0);
    // El contador refleja la filtración.
    expect(screen.getByText(/establecimientos registrados/i)).toHaveTextContent("1");
  });

  it("muestra 'No se encontraron operadores' cuando la búsqueda no coincide", async () => {
    mount(store);
    await waitFor(() => {
      expect(screen.getAllByText(OPS[0].razon_social).length).toBeGreaterThan(0);
    });

    const input = screen.getByPlaceholderText(/Buscar por N° Cartón/i);
    await user.type(input, "ZZZ-NONE-MATCH");

    await waitFor(() => {
      expect(screen.getByText(/No se encontraron operadores/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/establecimientos registrados/i)).toHaveTextContent("0");
  });

  it("al vaciar la búsqueda, vuelve a mostrar toda la lista", async () => {
    mount(store);
    await waitFor(() => {
      expect(screen.getAllByText(OPS[0].razon_social).length).toBeGreaterThan(0);
    });

    const input = screen.getByPlaceholderText(/Buscar por N° Cartón/i);
    await user.type(input, OPS[0].razon_social);
    await waitFor(() => {
      // Queda una sola fila (la razón social se pinta en dos celdas de esa fila).
      expect(screen.getAllByText(OPS[0].razon_social).length).toBe(2);
    });

    // Vaciamos la búsqueda (jsdom no soporta bien {SelectAll}/Backspace en
    // cadena; usamos change para limpiar el input controlado).
    fireEvent.change(input, { target: { value: "" } });

    await waitFor(() => {
      expect(screen.getAllByText(OPS[0].razon_social).length).toBeGreaterThan(0);
    });
    // El contador vuelve a N.
    expect(screen.getByText(/establecimientos registrados/i)).toHaveTextContent(
      String(OPS.length),
    );
  });

  it("muestra el estado de error si la API falla", async () => {
    // Override: fuerza un 500 en la lista.
    server.use(
      http.get("/api/registro-operadores", () =>
        HttpResponse.json({ detail: "Boom interno" }, { status: 500 }),
      ),
    );
    mount(store);

    await waitFor(
      () => {
        expect(screen.getByText(/Error al cargar el padrón/i)).toBeInTheDocument();
      },
      { timeout: 3000 },
    );
  });
});
