/**
 * Página genérica de módulo (placeholder) con la estructura institucional
 * (AppLayout) y un mensaje de "No implementado".
 */
import type { ReactNode } from "react";
import { AppLayout } from "../components/layout/AppLayout";

type ModuloPageProps = {
  titulo: string;
  descripcion?: string;
  children?: ReactNode;
};

export function ModuloPage({ titulo, descripcion, children }: ModuloPageProps) {
  return (
    <AppLayout>
      {children ?? (
        <div className="flex flex-col items-center justify-center gap-3 px-6 py-24 text-center">
          <span className="flex size-14 items-center justify-center rounded-2xl bg-rocca-rojo-claro text-[28px] font-black text-rocca-rojo">
            {titulo.charAt(0)}
          </span>
          <h1 className="text-[22px] font-bold text-rocca-azul-oscuro">{titulo}</h1>
          <p className="max-w-[560px] text-[13px] text-rocca-texto-suave">
            {descripcion ??
              "Módulo en desarrollo. Esta sección formará parte del sistema ROCCA de Control de la Cadena Cárnica."}
          </p>
          <span className="mt-2 rounded-full bg-rocca-aviso-fondo px-3 py-1 text-[12px] font-semibold text-[#78350f] border border-rocca-aviso-borde">
            No implementado
          </span>
        </div>
      )}
    </AppLayout>
  );
}
