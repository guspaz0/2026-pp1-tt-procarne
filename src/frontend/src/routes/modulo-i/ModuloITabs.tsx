/**
 * Tabs del Módulo I: Padrón de Operadores | Jerarquía | Formulario de Inscripción.
 * Usa NavLink de react-router para la navegación entre sub-rutas.
 *
 * Cada tab muestra un contador reactivo con la cantidad de items de esa sección.
 * Los datos se precargan solo cuando el usuario entra a la sección (cada página
 * dispara su `useListarQuery`); RTK Query los cachea, así que al volver el
 * contador se pinta de inmediato.
 */
import { NavLink, useLocation } from "react-router-dom";
import { IconBuildings, IconHierarchy, IconForm } from "../../components/shared/Icons";
import { useListarQuery } from "../../store/operadoresApi";
import {
  selectItems,
  selectGruposPorPersona,
} from "../../store/operadoresSlice";
import { useAppSelector } from "../../store/hooks";

type TabDef = {
  to: string;
  label: string;
  icon: typeof IconBuildings;
  /** Contador a mostrar (null = sin contador, p. ej. el formulario de inscripción). */
  count: number | null;
};

export function ModuloITabs() {
  const { data, isLoading } = useListarQuery();
  const items = useAppSelector(selectItems);
  const grupos = useAppSelector(selectGruposPorPersona);

  // `data` solo existe una vez que alguna sección precargó la lista.
  const cargada = data !== undefined;
  const totalOperadores = items.length;
  const totalPersonas = grupos.length;

  const TABS: TabDef[] = [
    { to: "/operadores/padron", label: "Padrón de Operadores", icon: IconBuildings, count: totalOperadores },
    { to: "/operadores/jerarquia", label: "Jerarquía: Personas y Sucursales", icon: IconHierarchy, count: totalPersonas },
    {
      to: "/operadores/inscripcion",
      label: "Formulario de Inscripción / Emitir Cartón F 102",
      icon: IconForm,
      count: null,
    },
  ];

  const location = useLocation();

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-rocca-borde bg-white px-6 py-3">
      {TABS.map((t) => {
        const Icon = t.icon;
        const isActive = location.pathname === t.to;
        return (
          <NavLink
            key={t.to}
            to={t.to}
            className={`flex items-center gap-2 rounded-lg px-3 py-2 text-[12px] font-semibold transition-colors ${
              isActive
                ? "bg-rocca-rojo text-white"
                : "text-rocca-texto-suave hover:bg-rocca-fondo"
            }`}
          >
            <Icon size={15} />
            <span>{t.label}</span>
            {t.count !== null && (
              <span
                className={`rounded-full px-2 py-0.5 text-[11px] font-bold tabular-nums ${
                  isActive ? "bg-white/20 text-white" : "bg-slate-200 text-slate-600"
                }`}
              >
                {cargada ? t.count : isLoading ? "…" : "—"}
              </span>
            )}
          </NavLink>
        );
      })}
    </div>
  );
}
