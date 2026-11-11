/**
 * Encabezado de página del Módulo I (breadcrumb, título y acciones)
 * del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 */
import { IconBuildings, IconCamera, IconForm, IconHierarchy } from "../../components/shared/Icons";

type PageHeaderProps = {
  onVerCarton?: () => void;
  onVerPadron?: () => void;
  onVerJerarquia?: () => void;
  onVerFormulario?: () => void;
};

export function PageHeader({
  onVerCarton,
  onVerPadron,
  onVerJerarquia,
  onVerFormulario,
}: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 border-b border-rocca-borde bg-white px-6 py-4 lg:flex-row lg:items-start lg:justify-between">
      {/* Breadcrumb + título */}
      <div className="flex flex-col gap-1.5">
        <div className="flex items-center gap-2">
          {/*<span className="rounded bg-rocca-rojo-pastel px-2 py-0.5 text-[10px] font-bold tracking-wide text-rocca-rojo-oscuro">
            MÓDULO I • PROCARNE OFICIAL
          </span>*/}
          <span className="text-[12px] text-rocca-texto-apagado">
            Dirección General de Agricultura y Ganadería de Santiago del Estero
          </span>
        </div>
        <h1 className="text-[20px] font-bold leading-tight text-rocca-azul-oscuro">
          Registro Provincial de Operadores de Carne (ROCCA)
        </h1>
        <p className="max-w-[640px] text-[12px] text-rocca-texto-suave">
          Sistema de alta, matriculación y emisión del Certificado de Operador F 102.
          Modelo de clases: Persona (Física / Jurídica) Titular de múltiples
          Operadores / Sucursales con requisitos de papeleo según categoría.
        </p>
      </div>

      {/* Acciones — fila superior */}
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={onVerCarton}
          className="flex items-center gap-1.5 rounded-lg border border-rocca-aviso-borde bg-rocca-aviso-fondo px-3 py-2 text-[12px] font-bold text-[#78350f] transition-colors hover:bg-[#fef3c7]"
        >
          <IconCamera size={15} className="text-[#b45309]" />
          Ver Cartón F 102 Original
        </button>
      </div>
    </div>
  );
}

/**
 * Fila secundaria de acciones del encabezado de página:
 * Padrón, Jerarquía y el botón primario "Formulario de Inscripción".
 */
export function PageHeaderActions({
  onVerPadron,
  onVerJerarquia,
  onVerFormulario,
}: {
  onVerPadron?: () => void;
  onVerJerarquia?: () => void;
  onVerFormulario?: () => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-rocca-borde bg-white px-6 py-3">
      <button
        type="button"
        onClick={onVerPadron}
        className="flex items-center gap-2 rounded-lg px-3 py-2 text-[12px] font-semibold text-rocca-texto-suave transition-colors hover:bg-rocca-fondo"
      >
        <IconBuildings size={15} className="text-rocca-texto-apagado" />
        Padrón de Operadores
      </button>
      <button
        type="button"
        onClick={onVerJerarquia}
        className="flex items-center gap-2 rounded-lg px-3 py-2 text-[12px] font-semibold text-rocca-texto-suave transition-colors hover:bg-rocca-fondo"
      >
        <IconHierarchy size={15} className="text-rocca-texto-apagado" />
        Jerarquía: Personas y Sucursales
      </button>
      <button
        type="button"
        onClick={onVerFormulario}
        className="flex items-center gap-2 rounded-lg bg-rocca-rojo px-3 py-2 text-[12px] font-bold text-white transition-opacity hover:opacity-90"
      >
        <IconForm size={15} />
        Formulario de Inscripción / Emitir Cartón F 102
      </button>
    </div>
  );
}
