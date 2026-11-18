/**
 * ToastContainer — Renderiza los toasts activos en la esquina superior derecha.
 *
 * Se monta una sola vez en la raíz de la app (dentro del Provider).
 * Cada toast se auto-cierra según su `duracion`; también se puede cerrar
 * manualmente con la "X".
 */

import { useEffect, useRef } from "react";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { quitarToast, type Toast, type ToastTipo } from "../../store/toastSlice";

/* Iconos por tipo */
function IconoToast({ tipo }: { tipo: ToastTipo }) {
  switch (tipo) {
    case "exito":
      return (
        <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case "error":
      return (
        <svg className="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
      );
    case "warning":
      return (
        <svg className="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
      );
    case "info":
    default:
      return (
        <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12v-.008z" />
        </svg>
      );
  }
}

/* Estilos por tipo */
const ESTILOS: Record<ToastTipo, { borde: string; bg: string }> = {
  exito: { borde: "border-l-green-500", bg: "bg-white" },
  error: { borde: "border-l-red-500", bg: "bg-white" },
  warning: { borde: "border-l-amber-500", bg: "bg-white" },
  info: { borde: "border-l-blue-500", bg: "bg-white" },
};

function ToastItem({ toast }: { toast: Toast }) {
  const dispatch = useAppDispatch();
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (toast.duracion !== null) {
      timerRef.current = setTimeout(() => {
        dispatch(quitarToast(toast.id));
      }, toast.duracion);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [toast.id, toast.duracion, dispatch]);

  const estilo = ESTILOS[toast.tipo];

  return (
    <div
      className={`${estilo.bg} ${estilo.borde} flex w-full items-start gap-3 rounded-lg border border-gray-200 border-l-4 p-4 shadow-lg`}
      role="alert"
    >
      <IconoToast tipo={toast.tipo} />
      <div className="flex-1 min-w-0">
        <p className="text-[13px] font-semibold text-gray-900">{toast.titulo}</p>
        {toast.mensaje && (
          <p className="mt-0.5 text-[12px] leading-relaxed text-gray-600">{toast.mensaje}</p>
        )}
      </div>
      <button
        type="button"
        onClick={() => dispatch(quitarToast(toast.id))}
        className="shrink-0 rounded p-0.5 text-gray-400 transition-colors hover:text-gray-600"
        aria-label="Cerrar"
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

export function ToastContainer() {
  const toasts = useAppSelector((s) => s.toasts.items);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-[100] flex w-full max-w-sm flex-col gap-2">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  );
}
