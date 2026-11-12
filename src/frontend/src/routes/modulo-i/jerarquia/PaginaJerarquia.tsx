/**
 * Jerarquía: Personas y Sucursales — sub-ruta /modulo-i/jerarquia.
 *
 * No hay endpoint propio para esta vista: se reutiliza el padrón completo
 * (`GET /registro-operadores`, `useListarQuery`) y la agrupación por
 * persona titular se hace en el frontend con `Object.groupBy` sobre el
 * CUIT de cada operador (un CUIT = una persona titular; sus sucursales
 * son los operadores que lo comparten).
 */
import { IconBuildings, IconUser } from "../../../components/shared/Icons";
import { useListarQuery } from "../../../store/api";
import type { Operador } from "../../../types";
import { ModuloILayout } from "../ModuloILayout";

/**
 * Agrupa los operadores por CUIT de la persona titular.
 * Devuelve un mapa ordenado (CUIT → sucursales, por nombre de sucursal)
 * listo para renderizar.
 */
function agruparPorCuit(operadores: Operador[]): [string, Operador[]][] {
  // Object.groupBy (ES2024) devuelve un objeto plano Record<K, T[]>.
  const porCuit = Object.groupBy(
    operadores,
    (o: Operador) => (o.cuit ?? `op-${o.id}`).toUpperCase(),
  ) as Record<string, Operador[]>;

  return Object.entries(porCuit)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([cuit, ops]) => [
      cuit,
      [...ops].sort((a, b) => a.razon_social.localeCompare(b.razon_social)),
    ]);
}

export function PaginaJerarquia() {
  const { data: operadores, isLoading, error } = useListarQuery();

  const grupos = agruparPorCuit(operadores ?? []);
  const totalSucursales = operadores?.length ?? 0;

  return (
    <ModuloILayout>
      <div className="flex flex-col gap-5 p-6">
        <div className="flex flex-col gap-1">
          <h2 className="text-[16px] font-bold text-rocca-azul-oscuro">
            Jerarquía: Personas y Sucursales
          </h2>
          <p className="text-[12px] text-rocca-texto-suave">
            {grupos.length} persona{grupos.length !== 1 ? "s" : ""} titular
            {grupos.length !== 1 ? "es" : ""} con {totalSucursales} sucursal
            {totalSucursales !== 1 ? "es" : ""} en total.
          </p>
        </div>

        {isLoading && (
          <div className="py-12 text-center text-[13px] text-rocca-texto-apagado">
            Cargando jerarquía…
          </div>
        )}

        {!isLoading && (error as object) && (
          <div className="py-12 text-center text-[13px] text-rocca-error">
            Error al cargar: {error instanceof Error ? error.message : JSON.stringify(error)}
          </div>
        )}

        {!isLoading && !error && grupos.length === 0 && (
          <div className="py-12 text-center text-[13px] text-rocca-texto-apagado">
            No hay operadores registrados.
          </div>
        )}

        {!isLoading &&
          !error &&
          grupos.map(([cuit, sucursales]) => (
            <div
              key={cuit}
              className="overflow-hidden rounded-lg border border-rocca-borde"
            >
              <div className="flex items-center gap-3 border-b border-rocca-borde bg-[#f8fafc] px-4 py-3">
                <span className="flex size-9 items-center justify-center rounded-full bg-rocca-rojo-claro text-rocca-rojo">
                  <IconUser size={18} />
                </span>
                <div className="flex flex-col">
                  <span className="text-[14px] font-bold text-rocca-azul-oscuro">
                    {sucursales[0].razon_social}
                  </span>
                  <span className="text-[11px] text-rocca-texto-apagado">
                    CUIT: {cuit}
                  </span>
                </div>
                <span className="ml-auto rounded-full bg-slate-200 px-2.5 py-0.5 text-[11px] font-semibold text-slate-600">
                  {sucursales.length} sucursal{sucursales.length !== 1 ? "es" : ""}
                </span>
              </div>

              <ul className="divide-y divide-rocca-borde">
                {sucursales.map((s) => (
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
