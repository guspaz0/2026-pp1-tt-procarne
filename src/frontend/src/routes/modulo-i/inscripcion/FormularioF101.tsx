/**
 * Formulario de Inscripción / Emisión de Cartón F 102
 * del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 *
 * Orquestador: compone las 4 secciones + banner + acciones.
 *
 * Secciones (una por archivo en ./secciones/):
 *  1. SeccionPersonaTitular
 *  2. SeccionEstablecimiento
 *  3. SeccionCategoria
 *  4. SeccionRequisitos
 */
import { useEffect } from "react";
import { IconCheck, IconForm, IconUpload } from "../../../components/shared/Icons";
import {
  resetearFormulario as resetearFormularioAction,
  type FormF102,
} from "../../../store/formF102Slice";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import {
  SeccionPersonaTitular,
} from "./secciones/SeccionPersonaTitular";
import {
  SeccionEstablecimiento,
} from "./secciones/SeccionEstablecimiento";
import { SeccionCategoria } from "./secciones/SeccionCategoria";
import { SeccionRequisitos } from "./secciones/SeccionRequisitos";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

type FormularioF101Props = {
  onRegistrar?: (data: FormF102) => void;
  onCancelar?: () => void;
};

export function FormularioF101({
  onRegistrar,
  onCancelar,
}: FormularioF101Props) {
  const dispatch = useAppDispatch();
  const form = useAppSelector((s) => s.formF102.form);

  // El formulario vive en el store; se inicializa una vez.
  useEffect(() => {
    dispatch(resetearFormularioAction(""));
  }, [dispatch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onRegistrar?.(form);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* ---------------------------------------------------------- */}
      {/* Banner oscuro de encabezado del formulario                 */}
      {/* ---------------------------------------------------------- */}
      <div
        className="flex flex-col gap-4 rounded-xl px-6 py-5 md:flex-row md:items-center md:justify-between"
        style={{
          background:
            "linear-gradient(90deg, #0f172a 0%, #540d17 50%, #0f172a 100%)",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.1)",
        }}
      >
        <div className="flex flex-col gap-1.5">
          <span className="flex items-center gap-1.5 text-[12px] font-bold text-[#fcd34d]">
            <IconForm size={14} />
            Simil Formulario Oficial F 101
          </span>
          <h2 className="text-[18px] font-bold text-white">
            Alta de Operador Cárnico
          </h2>
          <p className="max-w-[560px] text-[12px] text-[#cbd5e1]">
            Registra la Persona (Física/Jurídica), su establecimiento/sucursal,
            su categoría cárnica y sus requisitos de papeleo.
          </p>
        </div>
        <button
          type="button"
          className="flex shrink-0 items-center gap-2 rounded-lg bg-rocca-aviso px-4 py-2.5 text-[12px] font-bold text-[#020617] transition-opacity hover:opacity-90"
        >
          <IconUpload size={15} />
          Cargar Datos de un operador
        </button>
      </div>

      {/* ---------------------------------------------------------- */}
      {/* Secciones del formulario                                   */}
      {/* ---------------------------------------------------------- */}
      <SeccionPersonaTitular />
      <SeccionEstablecimiento />
      <SeccionCategoria />
      <SeccionRequisitos />

      {/* ---------------------------------------------------------- */}
      {/* Acciones finales                                            */}
      {/* ---------------------------------------------------------- */}
      <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={onCancelar}
          className="rounded-lg px-4 py-2.5 text-[13px] font-medium text-rocca-texto-medio transition-colors hover:bg-white"
        >
          Cancelar y Volver al Padrón
        </button>
        <button
          type="submit"
          className="flex items-center gap-2 rounded-lg bg-rocca-rojo px-5 py-2.5 text-[13px] font-bold text-white shadow-[0_2px_8px_rgba(139,20,37,0.3)] transition-opacity hover:opacity-90"
        >
          <IconCheck size={14} />
          Registrar Operador
        </button>
      </div>
    </form>
  );
}
