/**
 * INTEGRACIÓN — Formulario F 102 (FormularioF102 + formF102Slice).
 *
 * Verifica el flujo completo del formulario conectado al store:
 *
 *  1. Al montar, `resetearFormulario` se dispara y el select de
 *     Departamento se rellena con el primer valor (Capital, SdeE).
 *  2. Escribir en los campos dispatchea `setCampo` → el valor se refleja
 *     tanto en el DOM como en el store.
 *  3. Cambiar el tipo de persona a "Física" hace aparecer el campo D.N.I.
 *  4. Tocar una categoría de actividad toggla `toggleCategoria` en el store
 *     (el checkbox visual y el array del slice se sincronizan).
 *  5. Tocar un chip de tipo de carne toggla `toggleCarne`.
 *  6. Al submit, `onRegistrar` recibe el estado completo del formulario.
 *
 * Renderizamos el formulario sobre un store fresco por test.
 */
import React from "react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Provider } from "react-redux";
import { render } from "@testing-library/react";
import { FormularioF102 } from "../../../../src/routes/modulo-i/inscripcion/FormularioF102";
import { setupStore, type AppStore } from "../../../../src/store/store";
import type { FormF102 } from "../../../../src/store/formF102Slice";

function mount(
  store: AppStore,
  onRegistrar?: (data: FormF102) => void,
  onCancelar?: () => void,
) {
  render(
    <Provider store={store}>
      <FormularioF102 onRegistrar={onRegistrar} onCancelar={onCancelar} />
    </Provider>,
  );
}

describe("Integración · Formulario F 102", () => {
  let user: ReturnType<typeof userEvent.setup>;
  let store: AppStore;

  beforeEach(() => {
    vi.restoreAllMocks();
    user = userEvent.setup();
    store = setupStore();
  });

  it("al montar, el select de Departamento se rellena con el primer valor", async () => {
    mount(store);
    const dep = screen.getByLabelText(/Departamento Provincial/i) as HTMLSelectElement;
    // El effect dispara resetearFormulario(Capital, SdeE) → el select se actualiza.
    await waitFor(() => {
      expect(dep.value).toBe("Capital, Santiago del Estero");
    });
    expect(store.getState().formF102.form.departamento).toBe(
      "Capital, Santiago del Estero",
    );
  });

  it("escribir en un campo dispatchea setCampo (DOM y store se sincronizan)", async () => {
    mount(store);
    const cuit = screen.getByLabelText(/C\.U\.I\.T\./i);
    await user.type(cuit, "23-30917912-9");

    expect(cuit).toHaveValue("23-30917912-9");
    expect(store.getState().formF102.form.cuit).toBe("23-30917912-9");
  });

  it("cambiar a Persona Física muestra el campo D.N.I.", async () => {
    mount(store);
    // El formulario arranca en Física; lo pasamos a Jurídica para verificar
    // que el campo DNI desaparece.
    const tipo = screen.getByLabelText(/Tipo de Persona/i) as HTMLSelectElement;
    await user.selectOptions(tipo, "Persona Jurídica (Empresa / Sociedad)");
    await waitFor(() => {
      expect(screen.queryByLabelText(/^D\.N\.I\.$/)).toBeNull();
    });

    // Volvemos a Física: aparece el campo DNI y el store refleja el cambio.
    await user.selectOptions(tipo, "Persona Física (Humana / Titular)");
    await waitFor(() => {
      expect(screen.getByLabelText(/^D\.N\.I\.$/)).toBeInTheDocument();
    });
    expect(store.getState().formF102.form.tipoPersona).toBe("fisica");
  });

  it("tocar una categoría toggla toggleCategoria en el store", async () => {
    mount(store);
    const card = screen.getByRole("button", { name: /Carnicería Minorista/i });
    await user.click(card);

    await waitFor(() => {
      expect(store.getState().formF102.form.categorias).toContain("CARNICERIAS");
    });
    // Tocar de nuevo la deselecciona.
    await user.click(card);
    await waitFor(() => {
      expect(store.getState().formF102.form.categorias).not.toContain(
        "CARNICERIAS",
      );
    });
  });

  it("tocar un chip de tipo de carne toggla toggleCarne en el store", async () => {
    mount(store);
    const chip = screen.getByRole("button", { name: /Bovina/i });
    await user.click(chip);

    await waitFor(() => {
      expect(store.getState().formF102.form.tiposCarne).toContain("Bovina");
    });
    await user.click(chip);
    await waitFor(() => {
      expect(store.getState().formF102.form.tiposCarne).not.toContain("Bovina");
    });
  });

  it("al submit, onRegistrar recibe el estado completo del formulario", async () => {
    const onRegistrar = vi.fn();
    mount(store, onRegistrar);

    // Rellenamos un par de campos.
    await user.type(screen.getByLabelText(/C\.U\.I\.T\./i), "23-30917912-9");
    // Por defecto el tipo de persona es Física, así que el campo del titular
    // se llama "Apellido y Nombre del Titular *" (no "Razón Social *").
    await user.type(
      screen.getByLabelText(/Apellido y Nombre del Titular \*/i),
      "LA NORITA S.R.L.",
    );
    await user.type(
      screen.getByLabelText(/Nombre del Establecimiento/i),
      "LA NORITA",
    );
    // Seleccionamos una categoría.
    await user.click(screen.getByRole("button", { name: /Carnicería Minorista/i }));

    // Enviamos el formulario.
    await user.click(
      screen.getByRole("button", {
        name: /Registrar Operador y Emitir Cartón/i,
      }),
    );

    expect(onRegistrar).toHaveBeenCalledTimes(1);
    const enviado = onRegistrar.mock.calls[0][0] as FormF102;
    expect(enviado.cuit).toBe("23-30917912-9");
    expect(enviado.titular).toBe("LA NORITA S.R.L.");
    expect(enviado.nombreEstablecimiento).toBe("LA NORITA");
    expect(enviado.categorias).toContain("CARNICERIAS");
    expect(enviado.departamento).toBe("Capital, Santiago del Estero");
  });
});
