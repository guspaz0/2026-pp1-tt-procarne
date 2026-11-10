/**
 * Definición de rutas del sistema ROCCA.
 * Cada módulo del NavBar tiene su propia ruta.
 *
 * Autenticación (InsForge como IdP): el token se guarda en una cookie
 * HttpOnly que fija FastAPI al hacer login. El frontend NO lo lee: el
 * navegador lo envía automáticamente en cada petición. Para decidir si
 * una ruta está protegida, consultamos `/api/auth/me` (usa la cookie).
 */

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useMeQuery } from "./store/authApi";
import { useAppDispatch, useAppSelector } from "./store/hooks";
import { cerrarSesion, setSesion } from "./store/authSlice";
import { registerAuthGuard } from "./store/authGuard";
import { PaginaLogin } from "./routes/PaginaLogin";
import { PaginaInicio } from "./routes/PaginaInicio";
import { PaginaRegistroOperadores } from "./routes/modulo-i/inscripcion/PaginaRegistroOperadores";
import { PaginaPadron } from "./routes/modulo-i/padron/PaginaPadron";
import { PaginaJerarquia } from "./routes/modulo-i/jerarquia/PaginaJerarquia";
import { ModuloPage } from "./routes/ModuloPage";

/**
 * Hook que consulta `/api/auth/me` para saber si hay sesión activa.
 * Devuelve:
 *  - `cargando`: mientras se valida la cookie.
 *  - `autenticado`: true si `/me` devolvió un usuario.
 *  - `usuario`: los metadatos del usuario (si existe).
 */
export function useSesion() {
  const dispatch = useAppDispatch();
  const usuarioLocal = useAppSelector((s) => s.auth.usuario);
  const { data, isLoading, isError } = useMeQuery();

  // Sincroniza el usuario del query con el store local (una sola vez).
  useEffect(() => {
    if (data && (data.email || data.id)) {
      dispatch(setSesion({ usuario: data }));
    } else if (isError && !usuarioLocal) {
      dispatch(cerrarSesion());
    }
  }, [data, isError, usuarioLocal, dispatch]);

  const autenticado = !!(data && (data.email || data.id));
  return { cargando: isLoading, autenticado, usuario: data ?? usuarioLocal };
}

/**
 * Envuelve una ruta para exigir sesión activa (cookie de InsForge válida).
 * Si no hay sesión, redirige a /login recordando la ruta de origen.
 */
function Protegida({ children }: { children: ReactNode }) {
  const { cargando, autenticado } = useSesion();
  const location = useLocation();

  if (cargando) {
    return (
      <div
        role="status"
        style={{
          margin: "2rem",
          padding: "1rem",
          border: "1px solid #c9d2d8",
          borderRadius: "6px",
          background: "#fff",
        }}
      >
        Verificando sesión…
      </div>
    );
  }

  if (!autenticado) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}

export function AppRoutes() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Registra el guard de auth: cualquier 401 en la API limpia la sesión
  // y redirige a /login automáticamente.
  useEffect(() => {
    registerAuthGuard(navigate, () => dispatch(cerrarSesion()));
  }, [navigate, dispatch]);

  return (
    <Routes>
      {/* Login (público) */}
      <Route path="/login" element={<PaginaLogin />} />
      {/* Operadores — sub-rutas por tab */}
      <Route path="/operadores" element={<Navigate to="/operadores/padron" replace />} />
      <Route path="/operadores/padron" element={<Protegida><PaginaPadron /></Protegida>} />
      <Route path="/operadores/jerarquia" element={<Protegida><PaginaJerarquia /></Protegida>} />
      <Route path="/operadores/inscripcion" element={<Protegida><PaginaRegistroOperadores /></Protegida>} />

      {/* Remitos REC y Tránsito */}
      <Route
        path="/remitos"
        element={
          <Protegida>
            <ModuloPage
              titulo="Remitos REC y Tránsito"
              descripcion="Gestión de remitos de la Red de Comercialización (REC) y tránsitos de ganado y carnes entre jurisdicciones."
            />
          </Protegida>
        }
      />

      {/* Fiscalización en Ruta */}
      <Route
        path="/fiscalizacion"
        element={
          <Protegida>
            <ModuloPage
              titulo="Fiscalización en Ruta"
              descripcion="Control y fiscalización de transporte de carnes y ganado en ruta, con geolocalización y verificación de remitos."
            />
          </Protegida>
        }
      />

      {/* Monitor Estratégico */}
      <Route
        path="/monitor"
        element={
          <Protegida>
            <ModuloPage
              titulo="Monitor Estratégico"
              descripcion="Panel de indicadores estratégicos, tableros de control y trazabilidad de la cadena cárnica provincial."
            />
          </Protegida>
        }
      />

      {/* Portal Público */}
      <Route
        path="/portal"
        element={
          <ModuloPage
            titulo="Portal Público"
            descripcion="Consulta pública de operadores habilitados, cartones F 102 vigentes y datos abiertos de la cadena cárnica."
          />
        }
      />

      {/* Faena en Origen */}
      <Route
        path="/faena"
        element={
          <Protegida>
            <ModuloPage
              titulo="Faena en Origen"
              descripcion="Registro y control de faena en origen (establecimientos de cría y engorde) con trazabilidad de origen."
            />
          </Protegida>
        }
      />

      {/* Raíz: página de inicio con iframe del portal público */}
      <Route path="/" element={<PaginaInicio />} />

      {/* Fallback: cualquier ruta desconocida vuelve a Operadores */}
      <Route path="*" element={<Navigate to="/operadores" replace />} />
    </Routes>
  );
}
