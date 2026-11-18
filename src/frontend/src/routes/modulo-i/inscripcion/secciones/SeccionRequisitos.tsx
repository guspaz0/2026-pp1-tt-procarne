/**
 * Sección 4 — Requisitos de Papeleo Exigidos (dinámicos según categoría)
 *
 * Cada requisito muestra un checkbox de cumplimiento + botón para adjuntar
 * la imagen/documento correspondiente.
 */
import { useRef, useState } from "react";
import { Checkbox, SectionCard } from "../../../../components/shared/FormField";
import {
  IconUpload,
  IconCamera,
  IconCheck,
} from "../../../../components/shared/Icons";
import { useAppDispatch, useAppSelector } from "../../../../store/hooks";
import {
  toggleRequisito as toggleRequisitoAction,
  setAdjunto as setAdjuntoAction,
} from "../../../../store/formF102Slice";
import {
  useListarCategoriasQuery,
  type CategoriaRequisito,
} from "../../../../store/api";

export type RequisitoAplicable = Omit<CategoriaRequisito, "id"> & {
  id: string;
};

/** Clave estable del checklist (sin acentos, sin espacios). */
export const reqId = (c: { nombre: string }) =>
  "req:" +
  c.nombre
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "_");

export function SeccionRequisitos() {
  const dispatch = useAppDispatch();
  const form = useAppSelector((s) => s.formF102.form);

  const { data: categoriasApi, isFetching: cargando } =
    useListarCategoriasQuery();

  const toggleRequisito = (id: string) => dispatch(toggleRequisitoAction(id));

  const setAdjunto = (id: string, nombre: string | null) =>
    dispatch(setAdjuntoAction({ id, nombre }));

  const categoriaSeleccionada = (categoriasApi ?? []).find((c) =>
    form.categorias.includes(c.nombre),
  );

  const requisitosAplicables: RequisitoAplicable[] =
    categoriaSeleccionada?.requisitos.map((r) => ({
      codigo: r.codigo,
      nombre: r.nombre,
      descripcion: r.descripcion,
      obligatorio: r.obligatorio,
      id: reqId(r),
    })) ?? [];

  return (
    <SectionCard
      numero="4"
      titulo="Requisitos de Papeleo Exigidos por la Dirección de Agricultura y Ganadería"
      descripcion={`Documentación requerida para la categoría seleccionada (${categoriaSeleccionada?.nombre ?? "—"}).`}
    >
      {cargando ? (
        <p className="text-[12px] text-rocca-texto-suave">
          Cargando requisitos de la categoría…
        </p>
      ) : !categoriaSeleccionada ? (
        <p className="text-[12px] text-rocca-texto-suave">
          Seleccione una categoría en la sección 3 para ver sus requisitos de
          papeleo.
        </p>
      ) : requisitosAplicables.length === 0 ? (
        <p className="text-[12px] text-rocca-texto-suave">
          Esta categoría no tiene requisitos de papeleo registrados.
        </p>
      ) : (
        <div className="flex flex-col gap-3">
          {requisitosAplicables.map((r) => {
            const cumplido = !!form.requisitos[r.id];
            const adjunto = form.adjuntos[r.id];
            return (
              <div
                key={r.id}
                className={`rounded-lg border p-3 transition-colors ${
                  cumplido
                    ? "border-rocca-exito-borde bg-rocca-exito-claro/80"
                    : "border-rocca-borde bg-white"
                }`}
              >
                {/* Fila principal: checkbox + nombre + badge */}
                <div className="flex items-center gap-3">
                  <Checkbox
                    checked={cumplido}
                    onChange={() => toggleRequisito(r.id)}
                  />
                  <div className="flex-1">
                    <span
                      className={`block text-[12px] font-medium ${
                        cumplido
                          ? "text-rocca-exito-texto"
                          : "text-rocca-texto-medio"
                      }`}
                    >
                      {r.nombre}
                    </span>
                    {r.descripcion && (
                      <span className="block text-[11px] leading-snug text-rocca-texto-apagado">
                        {r.descripcion}
                      </span>
                    )}
                  </div>
                  {/* Fila de adjunto: botón de upload + preview */}
                  <div className="mt-2 flex items-center gap-2 pl-8">
                    <AdjuntoBoton
                      requisitoId={r.id}
                      nombreArchivo={adjunto}
                      onAdjuntar={(nombre) => setAdjunto(r.id, nombre)}
                      onQuitar={() => setAdjunto(r.id, null)}
                    />
                  </div>
                  {r.obligatorio && (
                    <span className="rounded bg-rocca-error-fondo px-2 py-0.5 text-[10px] font-bold text-rocca-error">
                      OBLIGATORIO
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </SectionCard>
  );
}

/* ------------------------------------------------------------------ */
/* Botón de adjunto (upload de imagen) por requisito                   */
/* ------------------------------------------------------------------ */

type AdjuntoBotonProps = {
  requisitoId: string;
  nombreArchivo: string | undefined;
  onAdjuntar: (nombre: string) => void;
  onQuitar: () => void;
};

function AdjuntoBoton({
  nombreArchivo,
  onAdjuntar,
  onQuitar,
}: AdjuntoBotonProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  /** Abre el dialog de archivos del SO. */
  const abrirPicker = () => inputRef.current?.click();

  /** Maneja el archivo elegido desde el <input type="file">. */
  const manejarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onAdjuntar(file.name);
    e.target.value = ""; // reset para poder re-seleccionar el mismo archivo
  };

  /** Drag & drop: soltar una imagen sobre la zona. */
  const manejarDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      onAdjuntar(file.name);
    }
  };

  const manejarDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const manejarDragLeave = () => setDragOver(false);

  // Input de archivo siempre presente (oculto) para que el click funcione.
  const inputOculto = (
    <input
      ref={inputRef}
      type="file"
      accept="image/*,.pdf"
      className="hidden"
      onChange={manejarChange}
    />
  );

  if (nombreArchivo) {
    return (
      <div className="flex items-center gap-2">
        {inputOculto}
        <IconCamera size={14} className="text-rocca-exito" />
        <span className="max-w-[200px] truncate text-[11px] font-medium text-rocca-texto-medio">
          {nombreArchivo}
        </span>
        <button
          type="button"
          onClick={abrirPicker}
          className="text-[11px] font-semibold text-rocca-texto-suave underline hover:text-rocca-texto"
        >
          Reemplazar
        </button>
        <button
          type="button"
          onClick={onQuitar}
          className="text-[11px] font-semibold text-rocca-error underline hover:no-underline"
        >
          Quitar
        </button>
      </div>
    );
  }

  return (
    <div
      onDrop={manejarDrop}
      onDragOver={manejarDragOver}
      onDragLeave={manejarDragLeave}
      className={`flex items-center gap-1.5 rounded-md border border-dashed px-3 py-1.5 text-[11px] font-semibold transition-colors cursor-pointer ${
        dragOver
          ? "border-rocca-rojo bg-rocca-rojo-claro text-rocca-rojo"
          : "border-rocca-borde-input text-rocca-texto-suave hover:border-rocca-rojo hover:text-rocca-texto"
      }`}
      onClick={abrirPicker}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && abrirPicker()}
    >
      {inputOculto}
      <IconUpload size={13} />
      Adjuntar imagen
    </div>
  );
}
