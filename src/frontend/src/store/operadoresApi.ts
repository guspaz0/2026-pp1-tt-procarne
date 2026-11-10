import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { Operador, OperadorIn } from "../types";
import { baseQueryWithAuth } from "./authGuard";

const baseQuery = baseQueryWithAuth(
  fetchBaseQuery({
    baseUrl: "/api",
    // Las cookies de sesión (InsForge tokens) se envían automáticamente por el
    // navegador porque son HttpOnly. No necesitamos leerlas en JS.
    credentials: "include",
    prepareHeaders: (headers) => {
      headers.set("Accept", "application/json");
      return headers;
    },
  }),
);

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
     * Alta de un operador. Invalida la lista para refrescar Padrón/Jerarquía.
     */
    registrar: builder.mutation<Operador, OperadorIn>({
      query: (data) => ({
        url: "/registro-operadores",
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: data,
      }),
      invalidatesTags: () => [{ type: "Operador", id: "LIST" }] as const,
    }),
  }),
});

export const { useListarQuery, useRegistrarMutation } = operadoresApi;
