/**
 * INTEGRACIÓN — Cartón F 102 (PadronSucursales + CartonF102Modal + RTK Query).
 *
 * Flujo: desde la tabla del padrón se abre el modal de cartón (botón "Ver F102"),
 * el modal dispara `useObtenerCartonF102Query` (RTK Query), el PDF llega desde
 * la API mockeada (MSW) y se pinta en un <iframe>. Se cierra con "Cerrar".
 *
 * El modal usa `URL.createObjectURL` (no existe en jsdom) → lo mockeamos.
 */
import React from "react";
import { describe, it, expect, beforeEach, vi, afterAll } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { render } from "@testing-library/react";
import { PadronSucursales } from "../../../../src/routes/modulo-i/padron/PadronSucursales";
import { setupStore, type AppStore } from "../../../../src/store/store";
import { server } from "../../../mocks/server";
import { createHandlers } from "../../../mocks/handlers";
import { OPERADORES_MOCK as OPS } from "../../../mocks/data";

function mount(store: AppStore) {
  render(
    <Provider store={store}>
      <PadronSucursales />
    </Provider>,
  );
}

describe("Integración · Cartón F 102", () => {
  let user: ReturnType<typeof userEvent.setup>;
  let store: AppStore;

  beforeEach(() => {
    server.resetHandlers(...createHandlers());
    user = userEvent.setup();
    store = setupStore();
    // jsdom no implementa createObjectURL/revokeObjectURL. Se agregan como
    // propiedades a la clase real (no se reemplaza el constructor, que RTK
    // Query usa vía `new Request`).
    vi.stubGlobal(
      "URL",
      class extends URL {
        static createObjectURL() {
          return "blob:mock-pdf-url";
        }
        static revokeObjectURL() {}
      },
    );
  });

  afterAll(() => {
    vi.unstubAllGlobals();
  });

  it("abrir el cartón: dispara la query, el PDF llega de la API y se pinta el iframe", async () => {
    mount(store);
    await waitFor(() => {
      expect(screen.getAllByText(OPS[0].razon_social).length).toBeGreaterThan(0);
    });

    // Abro el cartón del primer operador (N° 100001).
    const botonesVer = screen.getAllByRole("button", { name: /Ver F102/i });
    await user.click(botonesVer[0]);

    // El modal aparece con el número de cartón.
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveTextContent("100001");

    // El PDF llega desde MSW (useObtenerCartonF102Query) y se monta el iframe.
    await waitFor(() => {
      const iframe = dialog.querySelector("iframe");
      expect(iframe).not.toBeNull();
      expect(iframe?.getAttribute("src")).toBe("blob:mock-pdf-url");
    }, { timeout: 3000 });

    // Lo cierro: el modal desaparece. Hay dos botones "Cerrar" (el icono X y
    // el de texto); ambos cierran, así que tomo el primero.
    await user.click(screen.getAllByRole("button", { name: /Cerrar/i })[0]);
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
  });
});
