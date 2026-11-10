/**
 * Jerarquía: Personas y Sucursales — sub-ruta /modulo-i/jerarquia.
 * Agrupa los operadores (sucursales) según la persona titular, identificada
 * por el CUIT. Cada persona agrupa todas sus sucursales.
 */
import { IconBuildings, IconUser } from "../../../components/shared/Icons";
import {
  selectGruposPorPersona,
  selectItems,
} from "../../../store/operadoresSlice";
import { useListarQuery } from "../../../store/operadoresApi";
import { useAppSelector } from "../../../store/hooks";
import { ModuloILayout } from "../ModuloILayout";

export function PaginaJerarquia() {
  const { isLoading, error } = useListarQuery();
  const operadores = useAppSelector(selectItems);
  const grupos = useAppSelector(selectGruposPorPersona);

  const cargando = isLoading;

  return (
    <ModuloILayout>
      <div className="flex flex-col gap-5 p-6">
        <div className="flex flex-col gap-1">
          <h2 className="text-[16px] font-bold text-rocca-azul-oscuro">
            Jerarquía: Personas y Sucursales
          </h2>
          <p className="text-[12px] text-rocca-texto-suave">
            {grupos.length} persona{grupos.length !== 1 ? "s" : ""} titular
            {grupos.length !== 1 ? "es" : ""} con {operadores.length} sucursal
            {operadores.length !== 1 ? "es" : ""} en total.
          </p>
        </div>

        {cargando && (
          <div className="py-12 text-center text-[13px] text-rocca-texto-apagado">
            Cargando jerarquía…
          </div>
        )}

        {!cargando && error && (
          <div className="py-12 text-center text-[13px] text-rocca-error">
            Error al cargar: {JSON.stringify(error)}
          </div>
        )}

        {!cargando &&
          !error &&
          grupos.map((g) => (
            <div
              key={g.cuit}
              className="overflow-hidden rounded-lg border border-rocca-borde"
            >
              <div className="flex items-center gap-3 border-b border-rocca-borde bg-[#f8fafc] px-4 py-3">
                <span className="flex size-9 items-center justify-center rounded-full bg-rocca-rojo-claro text-rocca-rojo">
                  <IconUser size={18} />
                </span>
                <div className="flex flex-col">
                  <span className="text-[14px] font-bold text-rocca-azul-oscuro">
                    {g.nombre}
                  </span>
                  <span className="text-[11px] text-rocca-texto-apagado">
                    CUIT: {g.cuit}
                  </span>
                </div>
                <span className="ml-auto rounded-full bg-slate-200 px-2.5 py-0.5 text-[11px] font-semibold text-slate-600">
                  {g.sucursales.length} sucursal{g.sucursales.length !== 1 ? "es" : ""}
                </span>
              </div>

              <ul className="divide-y divide-rocca-borde">
                {g.sucursales.map((s) => (
                  <li
                    key={s.id}
                    className="flex items-center gap-3 px-4 py-3 transition-colors hover:bg-[#f8fafc]"
                  >
                    <span className="text-rocca-texto-apagado">
                      <IconBuildings size={16} />
                    </span>
                    <div className="flex min-w-0 flex-col">
                      <span className="truncate text-[13px] font-semibold text-[#0f172a]">
                        {s.razon_social}
                      </span>
                      <span className="truncate text-[11px] text-[#64748b]">
                        {s.domicilio_comercial ?? "—"}
                      </span>
                    </div>
                    <span className="ml-auto shrink-0 rounded-full bg-[#d1fae5] px-2.5 py-0.5 text-[11px] font-semibold text-[#065f46]">
                      {s.estado_registral}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
      </div>
    </ModuloILayout>
  );
}
