/**
 * Componente para subir archivos de imagen para requisitos de operador.
 * Muestra una lista de requisitos con un botón de upload para cada uno.
 */
import { useRef, useState } from "react";
import { IconUpload, IconCheck } from "../../../components/shared/Icons";

type RequisitoItem = {
  id: number;
  nombre: string;
  descripcion?: string;
  obligatorio: boolean;
};

type ArchivoSubido = {
  documento_id: number;
  archivo_id: number;
  nombre: string;
  url: string;
  fecha_carga: string | null;
};

type Props = {
  operadorId: number;
  requisitos: RequisitoItem[];
};

export function FormularioRequisitos({ operadorId, requisitos }: Props) {
  const [subiendo, setSubiendo] = useState<number | null>(null);
  const [archivosPorRequisito, setArchivosPorRequisito] = useState<
    Record<number, ArchivoSubido[]>
  >({});
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (requisitoId: number, file: File) => {
    setSubiendo(requisitoId);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const token = localStorage.getItem("procarne_token");
      const response = await fetch(
        `/api/registro-operadores/${operadorId}/requisitos/${requisitoId}/archivo`,
        {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Error al subir archivo");
      }

      // Recargar archivos del requisito
      await cargarArchivos(requisitoId);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubiendo(null);
    }
  };

  const cargarArchivos = async (requisitoId: number) => {
    try {
      const token = localStorage.getItem("procarne_token");
      const response = await fetch(
        `/api/registro-operadores/${operadorId}/requisitos/${requisitoId}/archivos`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );

      if (response.ok) {
        const data: ArchivoSubido[] = await response.json();
        setArchivosPorRequisito((prev) => ({
          ...prev,
          [requisitoId]: data,
        }));
      }
    } catch {
      // Silencioso: si no hay archivos, no pasa nada
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {error && (
        <div className="rounded-lg border border-rocca-error-borde bg-rocca-error-fondo px-4 py-3 text-[12px] text-rocca-error">
          {error}
        </div>
      )}
      {requisitos.map((r) => {
        const archivos = archivosPorRequisito[r.id] || [];
        const tieneArchivo = archivos.length > 0;
        const fileInputRef = useRef<HTMLInputElement>(null);

        return (
          <div
            key={r.id}
            className={`rounded-lg border p-4 ${
              tieneArchivo
                ? "border-rocca-exito-borde bg-rocca-exito-claro/50"
                : "border-rocca-borde bg-white"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-[13px] font-semibold text-rocca-azul-oscuro">
                    {r.nombre}
                  </h4>
                  {r.obligatorio && (
                    <span className="rounded bg-rocca-error-fondo px-2 py-0.5 text-[10px] font-bold text-rocca-error">
                      OBLIGATORIO
                    </span>
                  )}
                  {tieneArchivo && (
                    <IconCheck className="h-4 w-4 text-rocca-exito" />
                  )}
                </div>
                {r.descripcion && (
                  <p className="mt-1 text-[11px] text-rocca-texto-suave">
                    {r.descripcion}
                  </p>
                )}
                {tieneArchivo && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {archivos.map((a) => (
                      <a
                        key={a.documento_id}
                        href={a.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 rounded bg-white px-2 py-1 text-[11px] text-rocca-azul-oscuro shadow-sm hover:bg-rocca-azul-claro"
                      >
                        <IconUpload className="h-3 w-3" />
                        {a.nombre}
                      </a>
                    ))}
                  </div>
                )}
              </div>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={subiendo === r.id}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-[12px] font-medium transition-colors ${
                  tieneArchivo
                    ? "bg-rocca-azul-claro text-rocca-azul-oscuro hover:bg-rocca-azul-medio"
                    : "bg-rocca-azul-oscuro text-white hover:bg-rocca-azul-medio"
                } disabled:opacity-50`}
              >
                {subiendo === r.id ? (
                  <>
                    <span className="h-3 w-3 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Subiendo...
                  </>
                ) : (
                  <>
                    <IconUpload className="h-3.5 w-3.5" />
                    {tieneArchivo ? "Reemplazar" : "Subir"}
                  </>
                )}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*,.pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    handleUpload(r.id, file);
                  }
                  e.target.value = "";
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
