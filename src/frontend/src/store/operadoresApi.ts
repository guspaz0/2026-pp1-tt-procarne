import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { Operador } from "../types";

/** Payload de alta (ROCCAOperadorIn del backend). */
export type OperadorIn = {
  cuit: string;
  razon_social: string;
  tipo: string;
  categoria?: string | null;
  domicilio_comercial?: string | null;
  telefono?: string | null;
  email?: string | null;
};

/**
 * API RTK Query para el backend FastAPI (ROCCA).
 *
 * Reemplaza los fetch manuales + async thunks: el cacheo, los estados
 * (isLoading/isError) y la invalidación tras cada alta quedan a cargo de
 * RTK Query, usando tags para refrescar el padrón de forma declarativa.
 *
 * En dev, Vite proxy-kea `/api` al backend (uvicorn :8000); en prod, el
 * backend sirve el build, así que la base queda relativa.
 */
const baseQuery = fetchBaseQuery({
  baseUrl: "/api",
  prepareHeaders: (headers) => {
    headers.set("Accept", "application/json");
    return headers;
  },
});

export const operadoresApi = createApi({
  reducerPath: "operadoresApi",
  baseQuery,
  tagTypes: ["Operador"],
  endpoints: (builder) => ({
    /**
     * Lista de operadores (padrón).
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
