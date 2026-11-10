/**
 * Padrón de Operadores — Módulo I.
 * Lista de operadores (sucursal por sucursal) con los estilos de la capa
 * Figma "ROCCA - Control Cadena Cárnica SDE" (node 39:916 "Table").
 *
 * Columnas: Certificado F 102 | Establecimiento & Razón Social |
 * Persona Titular / CUIT | Actividades / Especies | Domicilio | Estado | Cartón F 102
 */
import { useEffect, useMemo, useState } from "react";
import { IconCheck, IconCamera, IconDownload } from "../../../components/shared/Icons";
import { CartonF102Modal } from "./CartonF102Modal";
import type { Operador } from "../../../types";
import {
  setBusqueda as setBusquedaAction,
  selectItems,
  selectOperadoresFiltrados,
} from "../../../store/operadoresSlice";
import { useListarQuery } from "../../../store/operadoresApi";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";

// ---------------------------------------------------------------------------
// Mapeo de dominios → textos de la UI (para las columnas Actividades/Estado)
// ---------------------------------------------------------------------------
const CATEGORIA_LABEL: Record<string, string> = {
  CARNICERIAS: "Carnicería Minorista",
  CAMARAS_FRIGORIFICAS: "Frigorífico / Ciclo I",
  SALA_DE_DESPOSTE: "Despostadero / Ciclo II",
  FABRICA_DE_CHACINADOS: "Matarife Abastecedor",
  DISTRIBUIDOR: "Distribuidor Mayorista",
  TRANSPONEDOR: "Transportista de Carnes",
  SUPERMERCADO: "Carnicería Minorista",
};

const ESPECIES: Record<string, string> = {
  CARNICERIAS: "Bovina, Porcina",
  CAMARAS_FRIGORIFICAS: "Bovina",
  SALA_DE_DESPOSTE: "Bovina, Porcina, Caprina",
  FABRICA_DE_CHACINADOS: "Bovina, Porcina",
  DISTRIBUIDOR: "Bovina, Porcina",
  TRANSPONEDOR: "Bovina, Caprina",
  SUPERMERCADO: "Bovina, Porcina, Caprina",
};

function estadoLabel(estado: string): { texto: string; tono: "ok" | "warn" | "off" } {
  const e = (estado || "").toUpperCase();
  if (e.includes("ACTIVO") || e.includes("HABILITADO") || e.includes("ALTA"))
    return { texto: "Habilitado", tono: "ok" };
  if (e.includes("RENOV") || e.includes("VENC"))
    return { texto: "Renovación", tono: "warn" };
  if (e.includes("BAJA") || e.includes("INACTIVO") || e.includes("SUSP"))
    return { texto: "Inhabilitado", tono: "off" };
  return { texto: e || "—", tono: "ok" };
}

// ---------------------------------------------------------------------------
// Componentes de celda
// ---------------------------------------------------------------------------
function SelloVerde() {
  return (
    <span className="inline-flex items-center gap-1 rounded bg-[#d1fae5] px-1.5 py-0.5 text-[9px] font-medium text-[#065f46]">
      <IconCheck size={10} />
      Sello Verde
    </span>
  );
}

function BadgeEstado({ tono, texto }: { tono: "ok" | "warn" | "off"; texto: string }) {
  const estilos =
    tono === "ok"
      ? "bg-[#d1fae5] text-[#065f46]"
      : tono === "warn"
        ? "bg-[#fef3c7] text-[#92400e]"
        : "bg-[#fee2e2] text-[#991b1b]";
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold ${estilos}`}>
      <IconCheck size={12} />
      {texto}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Componente principal
// ---------------------------------------------------------------------------
export function PadronSucursales() {
  const dispatch = useAppDispatch();
  const { data, isLoading, error } = useListarQuery();
  const operadores = useAppSelector(selectItems);
  const { busqueda } = useAppSelector((s) => s.operadores);
  const filtrados = useAppSelector(selectOperadoresFiltrados);
  const [cartonAbierto, setCartonAbierto] = useState<Operador | null>(null);

  const cargando = isLoading;

  const exportarCSV = () => {
    const encabezados = [
      "N° Certificado",
      "Razón Social",
      "CUIT",
      "Categoría",
      "Domicilio",
      "Domicilio Fiscal",
      "Teléfono",
      "Email",
      "Estado",
    ];
    const filas = filtrados.map((o) => [
      String(100000 + o.id),
      o.razon_social,
      o.cuit,
      o.categoria ?? "",
      o.domicilio_comercial ?? "",
      o.telefono ?? "",
      o.email ?? "",
      o.estado_registral,
    ]);
    const csv = [encabezados, ...filas]
      .map((f) => f.map((c) => `"${c.replace(/"/g, '""')}`)).join(",");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `padron_rocca_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Escucha el evento custom de Ver Cartón (llevado desde PageHeader).
  useEffect(() => {
    const onVerCarton = () => {
      if (filtrados.length > 0) setCartonAbierto(filtrados[0]);
    };
    window.addEventListener("rocca:ver-carton", onVerCarton);
    return () => {
      window.removeEventListener("rocca:ver-carton", onVerCarton);
    };
  }, [filtrados]);

  return (
    <div className="flex flex-col gap-4 p-6">
      {/* Encabezado de sección + búsqueda */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-1">
          <h2 className="text-[16px] font-bold text-rocca-azul-oscuro">
            Padrón de Operadores
          </h2>
          <p className="text-[12px] text-rocca-texto-suave">
            {operadores.length} establecimientos registrados • listado por sucursal
          </p>
        </div>
        <div className="flex w-full items-center gap-2 lg:w-auto">
          <button
            type="button"
            onClick={exportarCSV}
            className="flex items-center gap-1.5 rounded-lg border border-rocca-borde-input bg-white px-3 py-2 text-[12px] text-rocca-texto-medio transition-colors hover:bg-rocca-fondo"
          >
            <IconDownload size={15} className="text-rocca-texto-apagado" />
            Exportar CSV
          </button>
          <div className="relative w-full lg:w-[360px]">
            <input
              type="text"
              value={busqueda}
              onChange={(e) => dispatch(setBusquedaAction(e.target.value))}
              placeholder="Buscar por N° Cartón, CUIT, Establecimiento, Titular…"
              className="w-full rounded-lg border border-rocca-borde-input bg-white px-3 py-2 text-[13px] text-rocca-azul-oscuro placeholder:text-rocca-texto-apagado focus:border-rocca-rojo focus:outline-none focus:ring-2 focus:ring-rocca-rojo/20"
            />
          </div>
        </div>
      </div>

      {/* Tabla */}
      <div className="overflow-hidden rounded-lg border border-rocca-borde">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="h-[56px] border-b border-rocca-borde bg-[#f1f5f9]">
                <th className="w-[120px] px-3 py-3 text-[12px] font-bold text-[#334155]">
                  Certificado F 102
                </th>
                <th className="px-3 py-3 text-[12px] font-bold text-[#334155]">
                  Establecimiento &amp; Razón Social
                </th>
                <th className="w-[170px] px-3 py-3 text-[12px] font-bold text-[#334155]">
                  Persona Titular / CUIT
                </th>
                <th className="w-[180px] px-3 py-3 text-[12px] font-bold text-[#334155]">
                  Actividades / Especies
                </th>
                <th className="w-[200px] px-3 py-3 text-[12px] font-bold text-[#334155]">
                  Domicilio
                </th>
                <th className="w-[120px] px-3 py-3 text-[12px] font-bold text-[#334155]">
                  Estado
                </th>
                <th className="w-[150px] px-3 py-3 text-[12px] font-bold text-[#334155]">
                  Cartón F 102
                </th>
              </tr>
            </thead>
            <tbody>
              {cargando && (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-[13px] text-rocca-texto-apagado">
                    Cargando padrón…
                  </td>
                </tr>
              )}

              {!cargando && (error as object) && (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-[13px] text-rocca-error">
                    Error al cargar el padrón: {error instanceof Error ? error.message : JSON.stringify(error)}
                  </td>
                </tr>
              )}

              {!cargando && !error && filtrados.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center text-[13px] text-rocca-texto-apagado">
                    No se encontraron operadores.
                  </td>
                </tr>
              )}

              {!cargando &&
                filtrados.map((o) => {
                  const cat = o.categoria ?? "";
                  const estado = estadoLabel(o.estado_registral);
                  return (
                    <tr
                      key={o.id}
                      className="border-b border-[#f1f5f9] transition-colors last:border-b-0 hover:bg-[#f8fafc]"
                    >
                      {/* Certificado F 102 */}
                      <td className="px-3 py-4 align-top">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[10px] font-medium text-rocca-texto-apagado">N°</span>
                          <span className="text-[14px] font-black leading-tight text-[#0f172a]">
                            {String(100000 + o.id)}
                          </span>
                          <span className="text-[10px] font-bold text-rocca-rojo">
                            FORMULARIO F 102
                          </span>
                        </div>
                      </td>

                      {/* Establecimiento & Razón Social */}
                      <td className="px-3 py-4 align-top">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <span className="text-[12px] font-semibold text-[#0f172a]">
                              {o.razon_social}
                            </span>
                            {estado.tono === "ok" && <SelloVerde />}
                          </div>
                          <span className="text-[10px] text-[#64748b]">
                            {o.domicilio_comercial ?? "—"}
                          </span>
                        </div>
                      </td>

                      {/* Persona Titular / CUIT */}
                      <td className="px-3 py-4 align-top">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[12px] font-semibold text-[#0f172a]">
                            {o.razon_social.split(" - ")[0]}
                          </span>
                          <span className="text-[10px] font-medium text-[#64748b]">
                            CUIT: {o.cuit}
                          </span>
                        </div>
                      </td>

                      {/* Actividades / Especies */}
                      <td className="px-3 py-4 align-top">
                        <div className="flex flex-col gap-0.5">
                          <span className="text-[12px] text-[#0f172a]">
                            {CATEGORIA_LABEL[cat] ?? cat ?? "—"}
                          </span>
                          <span className="text-[11px] text-[#64748b]">
                            Carnes: {ESPECIES[cat] ?? "Bovina"}
                          </span>
                        </div>
                      </td>

                      {/* Domicilio */}
                      <td className="px-3 py-4 align-top">
                        <span className="text-[12px] text-[#0f172a]">
                          {o.domicilio_comercial ?? "—"}
                        </span>
                      </td>

                      {/* Estado */}
                      <td className="px-3 py-4 align-top">
                        <BadgeEstado tono={estado.tono} texto={estado.texto} />
                      </td>

                      {/* Cartón F 102 */}
                      <td className="px-3 py-4 align-top">
                        <button
                          type="button"
                          onClick={() => setCartonAbierto(o)}
                          className="inline-flex items-center gap-1.5 rounded-md bg-rocca-rojo px-3 py-1.5 text-[11px] font-bold text-white transition-opacity hover:opacity-90"
                        >
                          <IconCamera size={13} />
                          Ver Cartón F 102
                        </button>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal Cartón F 102 */}
      {cartonAbierto && (
        <CartonF102Modal
          operador={cartonAbierto}
          onClose={() => setCartonAbierto(null)}
        />
      )}
    </div>
  );
}
