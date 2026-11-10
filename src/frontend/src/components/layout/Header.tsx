/**
 * Header institucional del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Gradiente azul→granate. A la izquierda, pegado al logo: badges, título ROCCA
 * y subtítulo. A la derecha, el panel de interconexión federal (glass card).
 */
// import { IconWifi } from "../shared/Icons"; // [INTERCONEXIÓN FEDERAL] desactivado

export function Header() {
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
            {/* [AGROTRAZA] desactivado
            <span className="flex items-center gap-1.5 rounded bg-[#10b981/20] px-2 py-0.5 text-[11px] text-[#6ee7b7] border border-[#34d399/30]">
              <span
                className="size-1.5 rounded-full"
                style={{ background: "#34d399", boxShadow: "0 0 6px #34d399" }}
              />
              AGROTRAZA Integrado
            </span>
            */}
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

        {/* Panel interconexión federal (glass) — desactivado
        <div
          className="flex shrink-0 items-center gap-3 rounded-lg px-4 py-3"
          style={{
            background: "rgba(0,0,0,0.35)",
            border: "1px solid rgba(255,255,255,0.1)",
            backdropFilter: "blur(24px)",
          }}
        >
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-1.5">
              <IconWifi size={14} className="text-[#34d399]" />
              <span className="text-[12px] font-semibold text-[#f1f5f9]">
                Interconexión Federal Activa
              </span>
            </div>
            <span className="text-[10px] text-[#94a3b8]">
              ARCA (REC) • SENASA (SIGSA)
            </span>
          </div>
          <span
            className="size-3 rounded-full"
            style={{ background: "#34d399", boxShadow: "0 0 10px #34d399" }}
          />
        </div>
        */}
      </div>
    </header>
  );
}
