/**
 * Footer institucional del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Fondo azul oscuro (#0f1e36) con datos de la Dirección General de Agricultura
 * y Ganadería y los marcos legales de referencia.
 */
import { IconShield } from "../shared/Icons";

const LEYES = [
  "Ley Federal 22.375",
  "Ley Provincial 5.893/92",
  // "AGROTRAZA Ley 27.279", // [AGROTRAZA] desactivado
];

export function Footer() {
  return (
    <footer className="bg-[#0f1e36]">
      <div className="mx-auto flex max-w-[1280px] flex-col gap-4 px-6 py-7 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-col gap-1">
          <span className="text-[14px] font-bold text-white">
            Dirección General de Agricultura y Ganadería • Programa ProCarne Fiscalización
          </span>
          <span className="text-[11px] text-rocca-texto-muy-apagado">
            Ministerio de Producción, Recursos Naturales, Forestería, Tierras y Medio Ambiente
          </span>
          <span className="text-[10px] text-rocca-texto-apagado">
            Andes N° 30, Torre Andes 8° Piso • Santiago del Estero • Tel. (0385) 423-0000 Int. 102
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          {LEYES.map((ley) => (
            <span key={ley} className="flex items-center gap-1.5 text-[11px] text-[#cbd5e1]">
              <IconShield size={14} className="text-[#34d399]" />
              {ley}
            </span>
          ))}
        </div>
      </div>
    </footer>
  );
}
