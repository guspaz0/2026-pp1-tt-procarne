/**
 * INTEGRACIÓN — Ver Cartón F 102 desde el header (PageHeader → evento → Padrón).
 *
 * Flujo de integración entre componentes vía CustomEvent:
 *
 *   PageHeader "Ver Cartón F 102 Original"
 *     → onVerCarton (PaginaPadron) → window.dispatchEvent("rocca:ver-carton")
 *     → PadronSucursales escucha el evento → abre CartonF102Modal
 *     → useObtenerCartonF102Query (RTK Query) → PDF de la API (MSW) → iframe.
 *
 * Montamos PaginaPadron completa (ModuloILayout + PageHeader + Tabs + Padrón)
 * para cubrir la cadena de eventos de punta a punta.
 */
import React from "react";
import { describe, it, expect, beforeEach, vi, afterAll } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { PaginaPadron } from "../../../../src/routes/modulo-i/padron/PaginaPadron";
import { setupStore, type AppStore } from "../../../../src/store/store";
import { server } from "../../../mocks/server";
import { createHandlers } from "../../../mocks/handlers";
import { OPERADORES_MOCK as OPS } from "../../../mocks/data";

function mount(store: AppStore) {
  render(
    <Provider store={store}>
      <MemoryRouter initialEntries={["/operadores/padron"]}>
        <PaginaPadron />
      </MemoryRouter>
    </Provider>,
  );
}

describe("Integración · Ver Cartón desde el header", () => {
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

  it("el botón del header abre el cartón del primer operador filtrado", async () => {
    mount(store);
    // La lista se carga (RTK Query) en el Padrón y las tabs.
    await waitFor(() => {
      expect(screen.getAllByText(OPS[0].razon_social).length).toBeGreaterThan(0);
    });

    // Botón del PageHeader.
    await user.click(
      screen.getByRole("button", { name: /Ver Cartón F 102 Original/i }),
    );

    // El evento custom abre el modal con el N° del primer operador (100001).
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toHaveTextContent("100001");

    // El PDF llega desde MSW y se monta el iframe.
    await waitFor(() => {
      const iframe = dialog.querySelector("iframe");
      expect(iframe).not.toBeNull();
      expect(iframe?.getAttribute("src")).toBe("blob:mock-pdf-url");
    }, { timeout: 3000 });
  });
});
