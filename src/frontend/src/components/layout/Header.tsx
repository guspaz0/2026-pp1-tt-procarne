/**
 * Header institucional del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Gradiente azul→granate. A la izquierda, pegado al logo: badges, título ROCCA
 * y subtítulo. A la derecha, el usuario logueado (email) con botón "Salir".
 */
import { useNavigate } from "react-router-dom";
import { useLogoutMutation } from "../../store/authApi";
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
    navigate("/", { replace: true });
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
      <div className="mx-auto flex max-w-[1280px] items-center justify-between gap-4 px-4 py-3">
        {/* Logo R + bloque de texto agrupados a la izquierda */}
        <div className="flex min-w-0 items-center gap-3">
          <div
            className="flex size-12 shrink-0 items-center justify-center rounded-lg text-[20px] font-bold tracking-[1px] text-white"
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
          <div className="flex min-w-0 flex-col gap-1.5">
          {/* Badges */}
          <div className="flex items-center gap-2">
            <span className="rounded bg-[#f59e0b/20] px-2 py-0.5 text-[11px] font-semibold tracking-[1.1px] text-[#fcd34d] border border-[#fbbf24/30]">
              GOBIERNO DE SANTIAGO DEL ESTERO
            </span>
          </div>

          {/* Título ROCCA + subtítulo en la misma línea */}
          <div className="flex items-center gap-2">
            <span className="text-[24px] font-black leading-none tracking-[-0.6px] text-white">
              ROCCA
            </span>
            <span className="text-[12px] tracking-[-0.6px] text-[#cbd5e1]">
              | Registro de Operadores y Control de la Cadena Cárnica
            </span>
          </div>

          <span className="text-[11px] text-[#cbd5e1]">
            Dirección General de Agricultura y Ganadería • ProCarne Fiscalización
          </span>
          </div>
        </div>

        {/* Usuario logueado + botón de salir */}
        {usuario && (
          <div className="flex shrink-0 items-center gap-3">
            <div className="flex flex-col items-end">
              <span className="text-[13px] font-semibold text-white">{usuario.email}</span>
              {typeof usuario.user_metadata?.nombre === "string" && (
                <span className="text-[10px] text-[#cbd5e1]">
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
