/**
 * Modal de detalle del Cartón F 102 — muestra los datos del operador
 * en formato de cartón provincial.
 */
import { useEffect } from "react";
import { IconCamera, IconCheck, IconDownload } from "../../../components/shared/Icons";
import type { Operador } from "../../../types";

const CATEGORIA_LABEL: Record<string, string> = {
  CARNICERIAS: "Carnicería Minorista",
  CAMARAS_FRIGORIFICAS: "Frigorífico / Ciclo I",
  SALA_DE_DESPOSTE: "Despostadero / Ciclo II",
  FABRICA_DE_CHACINADOS: "Matarife Abastecedor",
  DISTRIBUIDOR: "Distribuidor Mayorista",
  TRANSPONEDOR: "Transportista de Carnes",
  SUPERMERCADO: "Carnicería Minorista",
};

function Campo({ label, valor }: { label: string; valor: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[10px] font-bold uppercase tracking-wide text-rocca-texto-apagado">
        {label}
      </span>
      <span className="text-[13px] font-semibold text-[#0f172a]">{valor}</span>
    </div>
  );
}

export function CartonF102Modal({
  operador,
  onClose,
}: {
  operador: Operador;
  onClose: () => void;
}) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const numero = String(100000 + operador.id);
  const estadoOk = (operador.estado_registral || "").toUpperCase().includes("ACTIVO");

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`Cartón F 102 ${numero}`}
    >
      <div
        className="w-full max-w-[640px] overflow-hidden rounded-xl bg-white shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-rocca-borde bg-[#f8fafc] px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-lg bg-rocca-rojo text-white">
              <IconCamera size={20} />
            </span>
            <div>
              <h3 className="text-[15px] font-bold text-rocca-azul-oscuro">
                Cartón F 102 — N° {numero}
              </h3>
              <p className="text-[11px] text-rocca-texto-apagado">
                Formulario Oficial de Inscripción Provincial
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex size-8 items-center justify-center rounded-lg text-rocca-texto-apagado transition-colors hover:bg-rocca-fondo hover:text-rocca-azul-oscuro"
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        {/* Cuerpo */}
        <div className="flex flex-col gap-5 p-5">
          {/* Estado */}
          <div
            className={`flex items-center gap-2 rounded-lg px-4 py-3 ${
              estadoOk
                ? "bg-[#d1fae5] text-[#065f46]"
                : "bg-[#fee2e2] text-[#991b1b]"
            }`}
          >
            <IconCheck size={16} />
            <span className="text-[13px] font-bold">
              {estadoOk ? "Habilitado" : operador.estado_registral}
            </span>
            {estadoOk && (
              <span className="ml-auto rounded bg-white/60 px-2 py-0.5 text-[10px] font-medium">
                Sello Verde
              </span>
            )}
          </div>

          {/* Datos en grid */}
          <div className="grid grid-cols-2 gap-4">
            <Campo label="Razón Social" valor={operador.razon_social} />
            <Campo label="CUIT" valor={operador.cuit} />
            <Campo label="Categoría" valor={CATEGORIA_LABEL[operador.categoria ?? ""] ?? operador.categoria ?? "—"} />
            <Campo label="Tipo" valor={operador.tipo} />
            <Campo label="Domicilio Comercial" valor={operador.domicilio_comercial ?? "—"} />
            <Campo label="Teléfono" valor={operador.telefono ?? "—"} />
            <Campo label="Email" valor={operador.email ?? "—"} />
          </div>

          {/* Fechas */}
          <div className="flex items-center gap-6 border-t border-rocca-borde pt-4 text-[11px] text-rocca-texto-apagado">
            <span>
              Alta:{" "}
              <strong className="text-rocca-azul-oscuro">
                {operador.alta_fecha
                  ? new Date(operador.alta_fecha).toLocaleDateString("es-AR")
                  : "—"}
              </strong>
            </span>
            <span>
              Creado:{" "}
              <strong className="text-rocca-azul-oscuro">
                {new Date(operador.creado_en).toLocaleDateString("es-AR")}
              </strong>
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 border-t border-rocca-borde bg-[#f8fafc] px-5 py-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-rocca-borde px-4 py-2 text-[12px] font-semibold text-rocca-texto-suave transition-colors hover:bg-white"
          >
            Cerrar
          </button>
          <button
            type="button"
            className="inline-flex items-center gap-1.5 rounded-lg bg-rocca-rojo px-4 py-2 text-[12px] font-bold text-white transition-opacity hover:opacity-90"
          >
            <IconDownload size={14} />
            Descargar PDF
          </button>
        </div>
      </div>
    </div>
  );
}
