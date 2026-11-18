/**
 * Header institucional del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Gradiente azul→granate. A la izquierda, pegado al logo: badges, título ROCCA
 * y subtítulo. A la derecha, el usuario logueado (email) con botón "Salir".
 */
import { useNavigate } from "react-router-dom";
import { useLogoutMutation } from "../../store/api";
import { cerrarSesion } from "../../store/authSlice";
import { useAppDispatch, useAppSelector } from "../../store/hooks";

export function Header() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { usuario } = useAppSelector((s) => s.auth);
  const [logout, { isLoading: cerrando }] = useLogoutMutation();

  async function onLogout() {
    // Cierra la sesión en InsForge y limpia las cookies (el backend hace el
    // sign-out y borra las cookies HttpOnly).
    try {
      await logout().unwrap();
    } catch {
      // Mejor esfuerzo: aunque el sign-out remoto falle, limpiamos local.
    }
    dispatch(cerrarSesion());
    // Refrescar la página para limpiar todo el estado (cache de RTK Query,
    // slices, etc.) y evitar que persistan datos tras el logout.
    window.location.href = "/";
  }

  return (
    <header
      className="w-full"
      style={{
        background:
          "linear-gradient(90deg, #0f1e36 0%, #0f172a 50%, #540d17 100%)",
        boxShadow: "0 2px 4px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.1)",
      }}
    >
      <div className="mx-auto flex max-w-[1280px] flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
        {/* Logo R + bloque de texto agrupados a la izquierda */}
        <div className="flex min-w-0 items-center gap-3">
          <div
            className="flex size-10 shrink-0 items-center justify-center rounded-lg text-[18px] font-bold tracking-[1px] text-white sm:size-12 sm:text-[20px]"
            style={{
              background: "var(--color-rocca-rojo)",
              border: "1px solid #c22338",
              boxShadow: "inset 0 2px 4px rgba(0,0,0,0.05)",
            }}
            aria-label="ROCCA"
          >
            R
          </div>

          {/* Bloque de texto pegado al logo */}
          <div className="flex min-w-0 flex-col gap-1">
            {/* Badges */}
            <div className="flex items-center gap-2">
              <span className="rounded bg-[#f59e0b/20] px-2 py-0.5 text-[10px] font-semibold tracking-[1.1px] text-[#fcd34d] border border-[#fbbf24/30] sm:text-[11px]">
                GOBIERNO DE SANTIAGO DEL ESTERO
              </span>
            </div>

            {/* Título ROCCA + subtítulo */}
            <div className="flex flex-col gap-0.5 sm:flex-row sm:items-center sm:gap-2">
              <span className="text-[20px] font-black leading-none tracking-[-0.6px] text-white sm:text-[24px]">
                ROCCA
              </span>
              <span className="text-[11px] leading-tight tracking-[-0.3px] text-[#cbd5e1] sm:text-[12px]">
                | Registro de Operadores y Control de la Cadena Cárnica
              </span>
            </div>

            <span className="hidden text-[11px] text-[#cbd5e1] sm:block">
              Dirección General de Agricultura y Ganadería • ProCarne Fiscalización
            </span>
          </div>
        </div>

        {/* Usuario logueado + botón de salir */}
        {usuario && (
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <div className="flex min-w-0 flex-col items-start sm:items-end">
              <span className="max-w-[160px] truncate text-[12px] font-semibold text-white sm:max-w-none sm:text-[13px]">
                {usuario.email}
              </span>
              {typeof usuario.user_metadata?.nombre === "string" && (
                <span className="hidden text-[10px] text-[#cbd5e1] sm:block">
                  {usuario.user_metadata.nombre as string}
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={onLogout}
              disabled={cerrando}
              className="rounded-lg border border-white/20 bg-white/10 px-3 py-1.5 text-[12px] font-semibold text-white transition-colors hover:bg-white/20 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {cerrando ? "Cerrando…" : "Salir"}
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
