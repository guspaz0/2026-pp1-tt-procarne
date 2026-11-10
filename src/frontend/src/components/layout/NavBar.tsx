/**
 * Barra de navegación de módulos del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Fondo BLANCO con borde inferior; el módulo activo se resalta en rojo claro
 * (#fdf2f3) con borde rojo y texto rojo oscuro.
 */
import type { ComponentType } from "react";
import { NavLink } from "react-router-dom";
import {
  IconChart,
  IconDoc,
  IconFactory,
  IconGlobe,
  IconTruck,
  IconUser,
} from "../shared/Icons";
import { selectItems } from "../../store/operadoresSlice";
import { useAppSelector } from "../../store/hooks";

export type ModuloNav = {
  id: string;
  label: string;
  ruta: string;
  icon: ComponentType<{ size?: number; className?: string }>;
  /** Contador estático (módulos sin datos propios). El de Operadores es reactivo. */
  badge?: string;
};

export const MODULOS: ModuloNav[] = [
  { id: "monitor", label: "Monitor Estratégico", ruta: "/monitor", icon: IconChart },
  { id: "operadores", label: "Operadores", ruta: "/operadores", icon: IconUser },
  { id: "remitos", label: "Remitos REC y Tránsito", ruta: "/remitos", icon: IconDoc },
  { id: "fiscalizacion", label: "Fiscalización en Ruta", ruta: "/fiscalizacion", icon: IconTruck },
  { id: "faena", label: "Faena en Origen", ruta: "/faena", icon: IconFactory },
  { id: "portal", label: "Portal Público", ruta: "/portal", icon: IconGlobe },
];

export function NavBar() {
  // Contador reactivo de operadores (se pinta una vez precargada la lista).
  const totalOperadores = useAppSelector(selectItems).length;
  return (
    <nav className="w-full border-b border-rocca-borde bg-white shadow-[0_1px_2px_rgba(0,0,0,0.05)]">
      <div className="mx-auto flex max-w-[1280px] items-center gap-1 overflow-x-auto px-4 py-2">
        {MODULOS.map((m) => {
          const Icon = m.icon;
          return (
            <NavLink
              key={m.id}
              to={m.ruta}
              className={({ isActive }) =>
                `flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-[14px] transition-colors ${
                  isActive
                    ? "border border-rocca-rojo bg-rocca-rojo-claro font-bold text-rocca-rojo-oscuro"
                    : "font-medium text-rocca-texto-medio hover:bg-rocca-fondo"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon size={16} className={isActive ? "text-rocca-rojo" : "text-rocca-texto-apagado"} />
                  <span>{m.label}</span>
                  {m.badge && (
                    <span
                      className={`ml-1 flex h-4 min-w-4 items-center justify-center rounded-full px-1.5 text-[10px] font-bold ${
                        isActive ? "bg-rocca-rojo text-white" : "bg-slate-200 text-slate-600"
                      }`}
                    >
                      {m.badge}
                    </span>
                  )}
                  {m.id === "operadores" && totalOperadores > 0 && (
                    <span
                      className={`ml-1 flex h-4 min-w-4 items-center justify-center rounded-full px-1.5 text-[10px] font-bold tabular-nums ${
                        isActive ? "bg-rocca-rojo text-white" : "bg-slate-200 text-slate-600"
                      }`}
                    >
                      {totalOperadores}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
