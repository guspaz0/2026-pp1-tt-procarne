import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

/**
 * Slice del formulario de inscripción / Cartón F 102.
 *
 * Mantiene el estado del formulario fuera del componente `FormularioF102`,
 * permitiendo resetearlo (p. ej. al volver al Padrón) desde cualquier parte.
 */

export type FormF102 = {
  tipoPersona: "fisica" | "juridica";
  personaExistente: boolean;
  cuit: string;
  titular: string;
  dni: string;
  telefono: string;
  email: string;
  nombreEstablecimiento: string;
  departamento: string;
  domicilio: string;
  habilitacionSanitaria: string;
  categorias: string[];
  tiposCarne: string[];
  requisitos: Record<string, boolean>;
  // selloAgrotraza: boolean; // [AGROTRAZA] desactivado
};

export const FORM_INICIAL: FormF102 = {
  tipoPersona: "fisica",
  personaExistente: false,
  cuit: "",
  titular: "",
  dni: "",
  telefono: "",
  email: "",
  nombreEstablecimiento: "",
  // Se rellena en `resetearFormulario` con el primer departamento disponible.
  departamento: "",
  domicilio: "",
  habilitacionSanitaria: "",
  categorias: [],
  tiposCarne: [],
  requisitos: {},
  // selloAgrotraza: false, // [AGROTRAZA] desactivado
};

type FormState = {
  form: FormF102;
};

const initialState: FormState = { form: { ...FORM_INICIAL } };

const formF102Slice = createSlice({
  name: "formF102",
  initialState,
  reducers: {
    setCampo: {
      reducer(
        state,
        action: PayloadAction<{ key: keyof FormF102; value: FormF102[keyof FormF102] }>,
      ) {
        (state.form[action.payload.key] as FormF102[keyof FormF102]) = action.payload.value;
      },
      prepare(key: keyof FormF102, value: FormF102[keyof FormF102]) {
        return { payload: { key, value } };
      },
    },
    toggleCategoria(state, action: PayloadAction<string>) {
      const id = action.payload;
      const c = state.form.categorias;
      state.form.categorias = c.includes(id) ? c.filter((x) => x !== id) : [...c, id];
    },
    toggleCarne(state, action: PayloadAction<string>) {
      const t = action.payload;
      const c = state.form.tiposCarne;
      state.form.tiposCarne = c.includes(t) ? c.filter((x) => x !== t) : [...c, t];
    },
    toggleRequisito(state, action: PayloadAction<string>) {
      const id = action.payload;
      state.form.requisitos[id] = !state.form.requisitos[id];
    },
    /** Vuelve el formulario a su estado inicial, opcionalmente fijando el departamento por defecto. */
    resetearFormulario(state, action: PayloadAction<string>) {
      state.form = { ...FORM_INICIAL, departamento: action.payload };
    },
  },
});

export const { setCampo, toggleCategoria, toggleCarne, toggleRequisito, resetearFormulario } =
  formF102Slice.actions;
export default formF102Slice.reducer;
