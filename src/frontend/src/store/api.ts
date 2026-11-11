/**
 * API central de ROCCA.
 *
 * Agrupa todas las APIs de RTK Query en un solo módulo para evitar
 * circular imports. Este módulo NO importa `store` ni `authGuard`
 * directamente: usa `baseQueryWithAuth` que se registra vía callback.
 */

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { Operador, OperadorIn, LoginResult, Usuario } from "../types";
import { baseQueryWithAuth } from "./authGuard";

/**
 * BaseQuery con detección de 401 global.
 * Las cookies de sesión (InsForge tokens) se envían automáticamente por el
 * navegador porque son HttpOnly. No necesitamos leerlas en JS.
 */
const baseQuery = baseQueryWithAuth(
  fetchBaseQuery({
    baseUrl: "/api",
    credentials: "include",
    prepareHeaders: (headers) => {
      headers.set("Accept", "application/json");
      return headers;
    },
  }),
);

/**
 * API de operadores (padrón, jerarquía, inscripción).
 */
export const operadoresApi = createApi({
  reducerPath: "operadoresApi",
  baseQuery,
  tagTypes: ["Operador"],
  endpoints: (builder) => ({
    /**
     * Lista de operadores (padrón). También alimenta la vista de Jerarquía.
     */
    listar: builder.query<Operador[], void>({
      query: () => "/registro-operadores",
      providesTags: [{ type: "Operador", id: "LIST" }] as const,
    }),
    /**
     * Obtiene un operador por id.
     */
    obtener: builder.query<Operador, number>({
      query: (id) => `/registro-operadores/${id}`,
      providesTags: (_r, _e, id) => [{ type: "Operador", id }],
    }),
    /**
     * Registra un nuevo operador (alta).
     */
    registrar: builder.mutation<Operador, OperadorIn>({
      query: (data) => ({
        url: "/registro-operadores",
        method: "POST",
        body: data,
      }),
      invalidatesTags: [{ type: "Operador", id: "LIST" }],
    }),
  }),
});

/**
 * API de autenticación (InsForge como IdP).
 * Se inyecta en `operadoresApi` para compartir el mismo baseQuery y middleware.
 */
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

// Re-exportar hooks para compatibilidad con imports existentes
export const { useListarQuery, useObtenerQuery, useRegistrarMutation } = operadoresApi;
export const { useLoginMutation, useSignupMutation, useMeQuery, useLogoutMutation } = authApi;
