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
 */

import type { BaseQueryFn } from "@reduxjs/toolkit/query";
import type { NavigateFunction } from "react-router-dom";

/** Callback registrado por AppRoutes para redirigir a /login. */
let _navigate: NavigateFunction | null = null;

/** Callback registrado por AppRoutes para limpiar el estado de auth. */
let _onAuthExpired: (() => void) | null = null;

/**
 * Registra el navigate y el callback de limpieza.
 * Se llama una vez desde AppRoutes (useEffect).
 */
export function registerAuthGuard(navigate: NavigateFunction, onAuthExpired: () => void) {
  _navigate = navigate;
  _onAuthExpired = onAuthExpired;
}

/**
 * Limpia el estado de auth y redirige a /login.
 * Se usa internamente por el baseQuery wrapper.
 */
function handleAuth401() {
  _onAuthExpired?.();
  _navigate?.("/login", { replace: true });
}

/**
 * BaseQuery con detección de 401 global.
 *
 * Si la respuesta es 401 (y no es un endpoint de auth como /login o /signup),
 * limpia la sesión y redirige a /login. La respuesta 401 se propaga
 * normalmente para que el componente pueda manejarla si lo necesita.
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
        handleAuth401();
      }
    }

    return result;
  };
}
