import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Operador } from "../types";
import { operadoresApi } from "./api";
import type { RootState } from "./store";

/**
 * Slice de UI del padrón de operadores (Módulo I).
 *
 * La carga/creación de datos vive en `operadoresApi` (RTK Query); este slice
 * solo conserva el estado local de la interfaz: el texto de búsqueda del
 * Padrón y el mensaje del último alta.
 */

export type OperadoresUiState = {
  /** Texto de búsqueda aplicado a la vista Padrón de Operadores. */
  busqueda: string;
  /** Resultado del último alta (mensaje para la UI). */
  altaMensaje: string | null;
};

const initialState: OperadoresUiState = {
  busqueda: "",
  altaMensaje: null,
};

const operadoresSlice = createSlice({
  name: "operadores",
  initialState,
  reducers: {
    setBusqueda(state, action: PayloadAction<string>) {
      state.busqueda = action.payload;
    },
    setAltaMensaje(state, action: PayloadAction<string | null>) {
      state.altaMensaje = action.payload;
    },
  },
});

export const { setBusqueda, setAltaMensaje } = operadoresSlice.actions;
export default operadoresSlice.reducer;

/**
 * Selectores derivados (operan sobre el cache de RTK Query).
 */

/**
 * Extrae la lista de operadores del cache de RTK Query.
 *
 * NO hardcodear la queryCacheKey: RTK Query serializa el endpoint `listar`
 * sin args como `"listar(undefined)"`, no `"listar"`. Usamos la API oficial
 * `api.util.selectInternalState` para resolverla de forma estable.
 */
export const selectItems = (state: RootState): Operador[] => {
  const entries = operadoresApi.util.selectEntriesForEndpoint(state, "listar");
  return entries[0]?.data ?? [];
};

/** Operadores filtrados por la búsqueda activa (razón social, CUIT o domicilio). */
export const selectOperadoresFiltrados = (state: RootState): Operador[] => {
  const items = selectItems(state);
  const q = state.operadores.busqueda.trim().toLowerCase();
  if (!q) return items;
  return items.filter(
    (o) =>
      o.razon_social.toLowerCase().includes(q) ||
      o.cuit.toLowerCase().includes(q) ||
      (o.domicilio_comercial ?? "").toLowerCase().includes(q),
  );
};

export type GrupoPersona = {
  cuit: string;
  nombre: string;
  sucursales: Operador[];
};

/**
 * Agrupa las sucursales por persona titular (clave: CUIT).
 * Si varios operadores comparten CUIT se agrupan; si es único,
 * cada operador es su propia persona (1 sucursal).
 */
export const selectGruposPorPersona = (state: RootState): GrupoPersona[] => {
  const items = selectItems(state);
  const porCuit = new Map<string, Operador[]>();
  for (const op of items) {
    const clave = op.cuit.toUpperCase();
    const lista = porCuit.get(clave) ?? [];
    lista.push(op);
    porCuit.set(clave, lista);
  }
  return Array.from(porCuit.entries()).map(([cuit, sucursales]) => ({
    cuit,
    nombre: sucursales[0].razon_social.split(" - ")[0],
    sucursales,
  }));
};
