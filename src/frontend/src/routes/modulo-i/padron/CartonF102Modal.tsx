/**
 * Modal de detalle del Cartón F 102 — muestra el PDF del formulario
 * oficial de inscripción provincial (mockeado desde el backend).
 */
import { useEffect, useState } from "react";
import { IconCamera, IconDownload } from "../../../components/shared/Icons";
import { useObtenerCartonF102Query } from "../../../store/api";
import type { Operador } from "../../../types";

export function CartonF102Modal({
  operador,
  onClose,
}: {
  operador: Operador;
  onClose: () => void;
}) {
  const [urlPdf, setUrlPdf] = useState<string | null>(null);

  const { data, isLoading, isError } = useObtenerCartonF102Query(operador.id, {
    skip: false,
  });

  // Cuando llega el PDF base64, lo convierte a una URL de objeto para el <iframe>.
  useEffect(() => {
    if (data?.fileContents) {
      const byteCharacters = atob(data.fileContents);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: data.contentType || "application/pdf" });
      const url = URL.createObjectURL(blob);
      setUrlPdf(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [data?.fileContents, data?.contentType]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const numero = String(100000 + operador.id);

  const descargar = () => {
    if (!urlPdf) return;
    const a = document.createElement("a");
    a.href = urlPdf;
    a.download = data?.fileDownloadName || `F102-${numero}.pdf`;
    a.click();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`Cartón F 102 ${numero}`}
    >
      <div
        className="flex h-[90vh] w-full max-w-[800px] flex-col overflow-hidden rounded-xl bg-white shadow-2xl"
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

        {/* Cuerpo: PDF */}
        <div className="flex-1 overflow-hidden bg-[#e2e8f0]">
          {isLoading && (
            <div className="flex h-full items-center justify-center">
              <div className="flex flex-col items-center gap-3">
                <div className="size-8 animate-spin rounded-full border-4 border-rocca-rojo border-t-transparent" />
                <span className="text-[13px] font-medium text-rocca-texto-suave">
                  Generando Cartón F 102…
                </span>
              </div>
            </div>
          )}

          {isError && (
            <div className="flex h-full items-center justify-center">
              <div className="flex flex-col items-center gap-2 text-center">
                <span className="text-[14px] font-bold text-rocca-error">
                  Error al generar el Cartón F 102
                </span>
                <span className="text-[12px] text-rocca-texto-apagado">
                  Verificá la conexión con el servidor.
                </span>
              </div>
            </div>
          )}

          {urlPdf && (
            <iframe
              src={urlPdf}
              title={`Cartón F 102 ${numero}`}
              className="h-full w-full border-0"
            />
          )}
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
            onClick={descargar}
            disabled={!urlPdf}
            className="inline-flex items-center gap-1.5 rounded-lg bg-rocca-rojo px-4 py-2 text-[12px] font-bold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            <IconDownload size={14} />
            Descargar PDF
          </button>
        </div>
      </div>
    </div>
  );
}
