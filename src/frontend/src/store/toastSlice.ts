/**
 * Toast Manager — Slice de Redux + acciones.
 *
 * Permite mostrar notificaciones transitorias (toasts) en cualquier parte
 * de la app sin acoplar el componente que las dispara al que las muestra.
 */

import { createSlice, nanoid, type PayloadAction } from "@reduxjs/toolkit";

export type ToastTipo = "exito" | "error" | "info" | "warning";

export interface Toast {
  id: string;
  tipo: ToastTipo;
  titulo: string;
  mensaje?: string;
  /** Duración en ms antes de auto-cerrar (null = no cierra solo). */
  duracion: number | null;
}

interface ToastState {
  items: Toast[];
}

const initialState: ToastState = { items: [] };

const toastSlice = createSlice({
  name: "toasts",
  initialState,
  reducers: {
    agregarToast: {
      reducer(state, action: PayloadAction<Toast>) {
        state.items.push(action.payload);
      },
      prepare(tipo: ToastTipo, titulo: string, opts?: { mensaje?: string; duracion?: number | null }) {
        const duracion = opts?.duracion !== undefined ? opts.duracion : (tipo === "error" ? 8000 : 5000);
        return {
          payload: {
            id: nanoid(),
            tipo,
            titulo,
            mensaje: opts?.mensaje,
            duracion,
          },
        };
      },
    },
    quitarToast(state, action: PayloadAction<string>) {
      state.items = state.items.filter((t) => t.id !== action.payload);
    },
    limpiarToasts(state) {
      state.items = [];
    },
  },
});

export const { agregarToast, quitarToast, limpiarToasts } = toastSlice.actions;
export default toastSlice.reducer;

/**
 * Hook de conveniencia: `const toast = useToast()` → `toast.exito("...", "...")`
 */
import { useDispatch } from "react-redux";
import type { AppDispatch } from "./store";

export function useToast() {
  const dispatch = useDispatch<AppDispatch>();
  return {
    exito: (titulo: string, mensaje?: string, duracion?: number | null) =>
      dispatch(agregarToast("exito", titulo, { mensaje, duracion })),
    error: (titulo: string, mensaje?: string, duracion?: number | null) =>
      dispatch(agregarToast("error", titulo, { mensaje, duracion })),
    info: (titulo: string, mensaje?: string, duracion?: number | null) =>
      dispatch(agregarToast("info", titulo, { mensaje, duracion })),
    warning: (titulo: string, mensaje?: string, duracion?: number | null) =>
      dispatch(agregarToast("warning", titulo, { mensaje, duracion })),
    dismiss: (id: string) => dispatch(quitarToast(id)),
  };
}
