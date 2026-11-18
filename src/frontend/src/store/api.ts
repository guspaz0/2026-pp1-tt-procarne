/**
 * API central de ROCCA.
 *
 * Agrupa todas las APIs de RTK Query en un solo módulo para evitar
 * circular imports. Este módulo NO importa `store` ni `authGuard`
 * directamente: usa `baseQueryWithAuth` que se registra vía callback.
 */

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { Operador, OperadorIn, LoginResult, Usuario, SignupPayload } from "../types";
import { baseQueryWithAuth } from "./authGuard";

export type FileTangoInfo = {
  fileContents: string;
  contentType: string;
  fileDownloadName: string;
  lastModified: string | null;
  entityTag: string | null;
  enableRangeProcessing: boolean;
};

/** Requisito de papeleo de una categoría (backend: modulos.registro_operadores). */
export type CategoriaRequisito = {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string | null;
  obligatorio: boolean;
};

/** Categoría de operador con sus requisitos de papeleo. */
export type CategoriaCarnicaApi = {
  id: number;
  nombre: string;
  descripcion?: string | null;
  ciclo?: string | null;
  requisitos: CategoriaRequisito[];
};

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
    /**
     * Obtiene el Cartón F 102 (formulario mockeado) como PDF base64.
     * Usa la Vercel Serverless Function (Node.js + pdfme) directamente.
     */
    obtenerCartonF102: builder.query<FileTangoInfo, number>({
      query: (id) => `/f102?id=${id}`,
    }),
    /**
     * Categorías de actividad cárnica con sus requisitos de papeleo
     * (para el select de categorías del formulario F 101).
     */
    listarCategorias: builder.query<CategoriaCarnicaApi[], void>({
      query: () => "/registro-operadores/categorias",
    }),
    /**
     * Sube un archivo de imagen para un requisito específico.
     */
    subirArchivoRequisito: builder.mutation<
      { operador_requisito_id: number; archivo_id: number; url: string; estado: string },
      { operadorId: number; requisitoCategoriaId: number; file: File }
    >({
      query: ({ operadorId, requisitoCategoriaId, file }) => {
        const formData = new FormData();
        formData.append("file", file);
        return {
          url: `/registro-operadores/${operadorId}/requisitos/${requisitoCategoriaId}/archivo`,
          method: "POST",
          body: formData,
        };
      },
    }),
    /**
     * Lista archivos subidos para un requisito específico.
     */
    listarArchivosRequisito: builder.query<
      Array<{ documento_id: number; archivo_id: number; nombre: string; url: string; fecha_carga: string | null }>,
      { operadorId: number; requisitoCategoriaId: number }
    >({
      query: ({ operadorId, requisitoCategoriaId }) =>
        `/registro-operadores/${operadorId}/requisitos/${requisitoCategoriaId}/archivos`,
    }),
    /**
     * Busca domicilios existentes por calle, localidad y departamento.
     */
    buscarDomicilios: builder.query<
      Array<{ id: number; calle: string; numero: string | null; localidad: string; departamento: string; provincia: string; codigo_postal: string | null }>,
      { calle: string; localidad?: string; departamento?: string }
    >({
      query: ({ calle, localidad, departamento }) => {
        const params = new URLSearchParams();
        params.set("calle", calle);
        if (localidad) params.set("localidad", localidad);
        if (departamento) params.set("departamento", departamento);
        return { url: `/domicilios?${params.toString()}` };
      },
    }),
    /**
     * Crea un domicilio nuevo.
     */
    crearDomicilio: builder.mutation<
      { id: number; calle: string; numero: string | null; localidad: string; departamento: string; provincia: string; codigo_postal: string | null },
      { calle: string; numero?: string; localidad: string; departamento: string; provincia?: string; codigo_postal?: string }
    >({
      query: (data) => {
        const params = new URLSearchParams();
        params.set("calle", data.calle);
        if (data.numero) params.set("numero", data.numero);
        params.set("localidad", data.localidad);
        params.set("departamento", data.departamento);
        if (data.provincia) params.set("provincia", data.provincia);
        if (data.codigo_postal) params.set("codigo_postal", data.codigo_postal);
        return { url: `/domicilios?${params.toString()}`, method: "POST" };
      },
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
    signup: builder.mutation<LoginResult, SignupPayload>({
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
    changePassword: builder.mutation<{ detail: string }, { new_password: string }>({
      query: (data) => ({
        url: "/auth/change-password",
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: data,
      }),
    }),
  }),
});

// Re-exportar hooks para compatibilidad con imports existentes
export const { useListarQuery, useObtenerQuery, useRegistrarMutation, useObtenerCartonF102Query, useListarCategoriasQuery, useBuscarDomiciliosQuery, useCrearDomicilioMutation } = operadoresApi;
export const { useLoginMutation, useSignupMutation, useMeQuery, useLogoutMutation, useChangePasswordMutation } = authApi;
