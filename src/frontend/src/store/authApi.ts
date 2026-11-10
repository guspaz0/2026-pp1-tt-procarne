/**
 * API de autenticación de ROCCA (InsForge como IdP).
 *
 * El frontend habla SOLO con FastAPI. Los tokens se guardan en cookies
 * HttpOnly que fija el backend al hacer login. El frontend no necesita
 * leer los tokens: el navegador los envía automáticamente.
 */

import { operadoresApi } from "./operadoresApi";
import type { LoginResult, Usuario } from "../types";

export const authApi = operadoresApi.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<LoginResult, { email: string; password: string }>({
      query: (data) => ({
        url: "/auth/login",
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: data,
      }),
    }),
    signup: builder.mutation<
      LoginResult,
      { email: string; password: string; user_metadata?: Record<string, unknown> }
    >({
      query: (data) => ({
        url: "/auth/signup",
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: data,
      }),
    }),
    me: builder.query<Usuario, void>({
      query: () => "/auth/me",
    }),
    logout: builder.mutation<null, void>({
      query: () => ({
        url: "/auth/logout",
        method: "POST",
      }),
    }),
  }),
});

export const { useLoginMutation, useSignupMutation, useMeQuery, useLogoutMutation } =
  authApi;
