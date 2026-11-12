/**
 * API de Georreferenciación del Estado Argentino (datos.gob.ar).
 *
 * Fuente: https://github.com/datosgobar/georef-ar-api
 * Spec OpenAPI: docs/open-api/spec/openapi.json
 *
 * Se usa para obtener las localidades a partir de un nombre (búsqueda
 * libre con debounce desde el frontend). Es una API pública externa,
 * por lo que usa un `fetchBaseQuery` propio (sin el baseQuery con auth de
 * ROCCA) y un reducerPath independiente.
 */

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

/** Entidad de localidad según el schema `localidad` de la spec. */
export type Localidad = {
  id: string;
  nombre: string;
  provincia?: { id?: string; nombre?: string } | null;
  departamento?: { id?: string; nombre?: string } | null;
  municipio?: { id?: string; nombre?: string } | null;
  localidad_censal?: { id?: string; nombre?: string } | null;
  categoria?: string | null;
  centroide?: { lat: number; lon: number } | null;
};

/** Envoltorio de respuesta del endpoint `GET /localidades`. */
export type LocalidadesResponse = {
  cantidad: number;
  total: number;
  inicio: number;
  localidades: Localidad[];
};

/** Entidad de departamento según el schema `departamento` de la spec. */
export type Departamento = {
  id: string;
  nombre: string;
  nombre_completo?: string;
  provincia?: { id?: string; nombre?: string } | null;
  centroide?: { lat: number; lon: number } | null;
  categoria?: string | null;
};

/** Envoltorio de respuesta del endpoint `GET /departamentos`. */
export type DepartamentosResponse = {
  cantidad: number;
  total: number;
  inicio: number;
  departamentos: Departamento[];
};

export type BuscarLocalidadesParams = {
  /** Texto de búsqueda por nombre (parcial). */
  nombre: string;
  /** Nombre o ID de provincia para acotar la búsqueda (opcional). */
  provincia?: string;
  /** Cantidad máxima de resultados (por defecto 20). */
  max?: number;
};

const georefBaseQuery = fetchBaseQuery({
  baseUrl: "https://apis.datos.gob.ar/georef/api/v2.0",
  prepareHeaders: (headers) => {
    headers.set("Accept", "application/json");
    return headers;
  },
});

export const georefApi = createApi({
  reducerPath: "georefApi",
  baseQuery: georefBaseQuery,
  tagTypes: ["Localidad"],
  endpoints: (builder) => ({
    /**
     * Busca localidades por nombre (y opcionalmente provincia).
     *
     * La API soporta `nombre`, `provincia`, `max`, `inicio`, `campos`,
     * `aplanar`, `orden`. Aquí usamos `nombre` + `provincia` + `max`.
     */
    buscarLocalidades: builder.query<LocalidadesResponse, BuscarLocalidadesParams>({
      query: ({ nombre, provincia, max = 20 }) => {
        const params = new URLSearchParams();
        if (nombre) params.set("nombre", nombre);
        if (provincia) params.set("provincia", provincia);
        params.set("max", String(max));
        return { url: "/localidades", params };
      },
      providesTags: ["Localidad"],
    }),
    /**
     * Busca departamentos por nombre (y opcionalmente provincia).
     * Mismo patrón que `buscarLocalidades`, sobre `GET /departamentos`.
     */
    buscarDepartamentos: builder.query<
      DepartamentosResponse,
      BuscarLocalidadesParams
    >({
      query: ({ nombre, provincia, max = 20 }) => {
        const params = new URLSearchParams();
        if (nombre) params.set("nombre", nombre);
        if (provincia) params.set("provincia", provincia);
        params.set("max", String(max));
        return { url: "/departamentos", params };
      },
      providesTags: ["Localidad"],
    }),
  }),
});

export const { useBuscarLocalidadesQuery, useBuscarDepartamentosQuery } = georefApi;
