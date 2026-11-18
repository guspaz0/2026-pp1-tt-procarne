/**
 * Definición de rutas del sistema ROCCA.
 *
 * Autenticación (InsForge como IdP): el token se guarda en una cookie
 * HttpOnly que fija FastAPI al hacer login. El frontend NO lo lee: el
 * navegador lo envía automáticamente en cada petición. Para decidir si
 * una ruta está protegida, consultamos `/api/auth/me` (usa la cookie).
 *
 * Roles:
 * - `admin`: acceso a /admin/* (padrón, jerarquía, inscripción, etc.)
 * - `operador`: acceso a /operador/* (sus establecimientos, registro)
 */

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { useMeQuery } from "./store/api";
import { useAppDispatch, useAppSelector } from "./store/hooks";
import { cerrarSesion, setSesion } from "./store/authSlice";
import { registerAuthGuard } from "./store/authGuard";
import { operadoresApi } from "./store/api";
import { store } from "./store/store";
import { PaginaLogin } from "./routes/PaginaLogin";
import { PaginaInicio } from "./routes/PaginaInicio";
import { PaginaRegistroOperadores } from "./routes/modulo-i/inscripcion/PaginaRegistroOperadores";
import { PaginaPadron } from "./routes/modulo-i/padron/PaginaPadron";
import { PaginaJerarquia } from "./routes/modulo-i/jerarquia/PaginaJerarquia";
import { ModuloPage } from "./routes/ModuloPage";
import { PaginaOperadorInicio } from "./routes/operador/PaginaOperadorInicio";
import { PaginaOperadorDetalle } from "./routes/operador/PaginaOperadorDetalle";
import { PaginaOperadorRegistro } from "./routes/operador/PaginaOperadorRegistro";
import { CambioContraseñaForzado } from "./routes/CambioContraseñaForzado";
import type { Rol } from "./types";

/**
 * Hook que consulta `/api/auth/me` para saber si hay sesión activa.
 * Devuelve:
 *  - `cargando`: mientras se valida la cookie.
 *  - `autenticado`: true si `/me` devolvió un usuario.
 *  - `usuario`: los metadatos del usuario (si existe).
 *  - `rol`: el rol del usuario ("admin" | "operador").
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
  const usuario = data ?? usuarioLocal;
  const rol: Rol | null = (usuario?.rol as Rol) ?? null;

  return { cargando: isLoading, autenticado, usuario, rol };
}

/**
 * Envuelve una ruta para exigir sesión activa (cookie de InsForge válida).
 * Si no hay sesión, redirige a /login recordando la ruta de origen.
 * Si el usuario tiene `must_change_password`, muestra la pantalla de cambio.
 */
function Protegida({ children }: { children: ReactNode }) {
  const { cargando, autenticado, usuario } = useSesion();
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

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

  // Forzar cambio de contraseña si el flag está activo.
  if (usuario?.must_change_password) {
    return (
      <CambioContraseñaForzado
        onExit={() => {
          // Cerrar sesión: el usuario debe volver a login con la nueva contraseña.
          dispatch(cerrarSesion());
          operadoresApi.util.resetApiState();
          navigate("/login", { replace: true });
        }}
      />
    );
  }

  return <>{children}</>;
}

/**
 * Envuelve una ruta para exigir un rol específico.
 * Si el usuario no tiene el rol requerido, redirige a su home correspondiente.
 * Si el usuario tiene `must_change_password`, muestra la pantalla de cambio.
 */
function ProtegidaPorRol({ rol, children }: { rol: Rol; children: ReactNode }) {
  const { cargando, autenticado, usuario } = useSesion();
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

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

  const rolUsuario = (usuario?.rol as Rol) ?? null;
  if (rolUsuario !== rol) {
    // Redirige a la home del rol del usuario
    const home = rolUsuario === "admin" ? "/admin" : "/operador";
    return <Navigate to={home} replace />;
  }

  // Forzar cambio de contraseña si el flag está activo.
  if (usuario?.must_change_password) {
    return (
      <CambioContraseñaForzado
        onExit={() => {
          dispatch(cerrarSesion());
          operadoresApi.util.resetApiState();
          navigate("/login", { replace: true });
        }}
      />
    );
  }

  return <>{children}</>;
}

/**
 * Redirige al usuario a su home según rol.
 */
function RedirigirPorRol() {
  const { cargando, autenticado, rol } = useSesion();

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
    return <Navigate to="/login" replace />;
  }

  if (rol === "admin") {
    return <Navigate to="/admin" replace />;
  }
  if (rol === "operador") {
    return <Navigate to="/operador" replace />;
  }

  // Sin rol definido: redirige a admin (por defecto)
  return <Navigate to="/admin" replace />;
}

export function AppRoutes() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Registra el guard de auth: cualquier 401 en la API limpia la sesión,
  // resetea el cache de RTK Query y redirige a /login automáticamente.
  useEffect(() => {
    registerAuthGuard(navigate, () => {
      // 1. Limpiar el estado de auth (usuario).
      store.dispatch(cerrarSesion());
      // 2. Resetear el cache de RTK Query (padron, jerarquia, etc.).
      operadoresApi.util.resetApiState();
      // 3. Redirigir a /login.
      navigate("/login", { replace: true });
    });
  }, [navigate, dispatch]);

  return (
    <Routes>
      {/* Login (público) */}
      <Route path="/login" element={<PaginaLogin />} />

      {/* ==================== RUTAS ADMIN ==================== */}
      <Route path="/admin" element={<ProtegidaPorRol rol="admin"><PaginaPadron /></ProtegidaPorRol>} />
      <Route path="/admin/padron" element={<ProtegidaPorRol rol="admin"><PaginaPadron /></ProtegidaPorRol>} />
      <Route path="/admin/jerarquia" element={<ProtegidaPorRol rol="admin"><PaginaJerarquia /></ProtegidaPorRol>} />
      <Route path="/admin/inscripcion" element={<ProtegidaPorRol rol="admin"><PaginaRegistroOperadores /></ProtegidaPorRol>} />

      {/* Remitos REC y Tránsito */}
      <Route
        path="/admin/remitos"
        element={
          <ProtegidaPorRol rol="admin">
            <ModuloPage
              titulo="Remitos REC y Tránsito"
              descripcion="Gestión de remitos de la Red de Comercialización (REC) y tránsitos de ganado y carnes entre jurisdicciones."
            />
          </ProtegidaPorRol>
        }
      />

      {/* Fiscalización en Ruta */}
      <Route
        path="/admin/fiscalizacion"
        element={
          <ProtegidaPorRol rol="admin">
            <ModuloPage
              titulo="Fiscalización en Ruta"
              descripcion="Control y fiscalización de transporte de carnes y ganado en ruta, con geolocalización y verificación de remitos."
            />
          </ProtegidaPorRol>
        }
      />

      {/* Monitor Estratégico */}
      <Route
        path="/admin/monitor"
        element={
          <ProtegidaPorRol rol="admin">
            <ModuloPage
              titulo="Monitor Estratégico"
              descripcion="Panel de indicadores estratégicos, tableros de control y trazabilidad de la cadena cárnica provincial."
            />
          </ProtegidaPorRol>
        }
      />

      {/* Faena en Origen */}
      <Route
        path="/admin/faena"
        element={
          <ProtegidaPorRol rol="admin">
            <ModuloPage
              titulo="Faena en Origen"
              descripcion="Registro y control de faena en origen (establecimientos de cría y engorde) con trazabilidad de origen."
            />
          </ProtegidaPorRol>
        }
      />

      {/* ==================== RUTAS OPERADOR ==================== */}
      <Route path="/operador" element={<ProtegidaPorRol rol="operador"><PaginaOperadorInicio /></ProtegidaPorRol>} />
      <Route path="/operador/registro" element={<ProtegidaPorRol rol="operador"><PaginaOperadorRegistro /></ProtegidaPorRol>} />
      <Route path="/operador/:operadorId" element={<ProtegidaPorRol rol="operador"><PaginaOperadorDetalle /></ProtegidaPorRol>} />

      {/* ==================== RUTAS PÚBLICAS ==================== */}
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

      {/* ==================== REDIRECCIONES ==================== */}
      {/* Raíz: redirige según rol */}
      <Route path="/" element={<RedirigirPorRol />} />

      {/* Rutas legacy: redirigen a /admin/* */}
      <Route path="/operadores" element={<Navigate to="/admin/padron" replace />} />
      <Route path="/operadores/padron" element={<Navigate to="/admin/padron" replace />} />
      <Route path="/operadores/jerarquia" element={<Navigate to="/admin/jerarquia" replace />} />
      <Route path="/operadores/inscripcion" element={<Navigate to="/admin/inscripcion" replace />} />
      <Route path="/remitos" element={<Navigate to="/admin/remitos" replace />} />
      <Route path="/fiscalizacion" element={<Navigate to="/admin/fiscalizacion" replace />} />
      <Route path="/monitor" element={<Navigate to="/admin/monitor" replace />} />
      <Route path="/faena" element={<Navigate to="/admin/faena" replace />} />

      {/* Fallback: cualquier ruta desconocida redirige según rol */}
      <Route path="*" element={<RedirigirPorRol />} />
    </Routes>
  );
}
