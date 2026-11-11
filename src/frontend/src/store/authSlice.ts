/**
 * Estado de autenticación de ROCCA (InsForge como IdP).
 *
 * El token de InsForge se guarda en una **cookie HttpOnly** que fija FastAPI
 * al hacer login (no es legible por JS). Este slice solo guarda los metadatos
 * del usuario (email, id, user_metadata) en memoria para mostrar el nombre
 * en el header; la autenticación real la resuelve el middleware de FastAPI
 * leyendo la cookie.
 */

import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { Usuario } from "../types";

/**
 * El usuario NO se persiste en localStorage: se obtiene siempre de
 * `/api/auth/me` (que valida la cookie). Esto evita el problema de
 * "usuario fantasma" al hacer refresh con la cookie expirada.
 */

export interface AuthState {
  usuario: Usuario | null;
}

const initialState: AuthState = { usuario: null };

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setSesion: (state, action: PayloadAction<{ usuario: Usuario | null }>) => {
      state.usuario = action.payload.usuario;
    },
    cerrarSesion: (state) => {
      state.usuario = null;
    },
  },
});

export const { setSesion, cerrarSesion } = authSlice.actions;
export default authSlice.reducer;
