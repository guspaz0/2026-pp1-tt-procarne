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

const KEY_USUARIO = "rocca_usuario";

function leerUsuario(): Usuario | null {
  try {
    const raw = localStorage.getItem(KEY_USUARIO);
    return raw ? (JSON.parse(raw) as Usuario) : null;
  } catch {
    return null;
  }
}

function guardarUsuario(usuario: Usuario | null) {
  try {
    if (usuario) localStorage.setItem(KEY_USUARIO, JSON.stringify(usuario));
    else localStorage.removeItem(KEY_USUARIO);
  } catch {
    /* localStorage puede no estar disponible */
  }
}

export interface AuthState {
  usuario: Usuario | null;
}

const initialState: AuthState = { usuario: leerUsuario() };

export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setSesion: (state, action: PayloadAction<{ usuario: Usuario | null }>) => {
      state.usuario = action.payload.usuario;
      guardarUsuario(action.payload.usuario);
    },
    cerrarSesion: (state) => {
      state.usuario = null;
      guardarUsuario(null);
    },
  },
});

export const { setSesion, cerrarSesion } = authSlice.actions;
export default authSlice.reducer;
