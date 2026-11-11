/**
 * Guard de autenticación global para RTK Query.
 *
 * Envuelve el baseQuery y detecta respuestas 401 en cualquier endpoint.
 * Cuando se detecta un 401 (cookie borrada/expirada), limpia el estado de
 * autenticación en el store y redirige a /login.
 *
 * Esto permite que el usuario sea redirigido automáticamente sin necesidad
 * de que haga clic en "Salir": si la cookie desaparece o expira, la próxima
 * llamada a la API devuelve 401 y el guard actúa.
 *
 * IMPORTANTE: Este módulo NO importa `store` ni `operadoresApi` directamente
 * para evitar circular imports (store → operadoresApi → authGuard → store).
 * En su lugar, usa callbacks registrados vía `registerAuthGuard`.
 */

import type { BaseQueryFn } from "@reduxjs/toolkit/query";
import type { NavigateFunction } from "react-router-dom";

/** Callbacks registrados por AppRoutes para evitar circular imports. */
let _navigate: NavigateFunction | null = null;
let _onAuth401: (() => void) | null = null;

/**
 * Registra el navigate y el handler de 401.
 * Se llama una vez desde AppRoutes (useEffect) o desde el módulo que
 * tiene acceso a `store` y `operadoresApi` sin crear ciclos.
 */
export function registerAuthGuard(
  navigate: NavigateFunction,
  onAuth401?: () => void,
) {
  _navigate = navigate;
  if (onAuth401) {
    _onAuth401 = onAuth401;
  }
}

/**
 * BaseQuery con detección de 401 global.
 *
 * Si la respuesta es 401 (y no es un endpoint de auth que lo espera),
 * invoca el handler registrado (que limpia el store y redirige).
 * La respuesta 401 se propaga normalmente para que el componente
 * pueda manejarla si lo necesita.
 */
export function baseQueryWithAuth(
  baseQuery: BaseQueryFn,
): BaseQueryFn {
  return async (args, api, extraOptions) => {
    const result = await baseQuery(args, api, extraOptions);

    // Detectar 401 en cualquier endpoint (excepto los de auth que lo esperan).
    if (result.error) {
      const status = (result.error as { status?: number }).status;
      const url = typeof args === "string" ? args : args.url;
      const isAuthEndpoint = url?.includes("/auth/login") || url?.includes("/auth/signup");

      if (status === 401 && !isAuthEndpoint) {
        // Invocar el handler registrado (limpia store + redirige).
        _onAuth401?.();
      }
    }

    return result;
  };
}
