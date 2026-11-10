/**
 * Primitivas de formulario del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Campos de texto, select, checkbox, tarjeta de sección (cabecera + cuerpo)
 * y chip de tipo de carne.
 */
import type { ReactNode } from "react";

/* ------------------------------------------------------------------ */
/* Campo de texto                                                      */
/* ------------------------------------------------------------------ */

type TextFieldProps = {
  label: string;
  required?: boolean;
  placeholder?: string;
  value?: string;
  onChange?: (v: string) => void;
  type?: string;
};

export function TextField({
  label,
  required,
  placeholder,
  value,
  onChange,
  type = "text",
}: TextFieldProps) {
  return (
    <label className="flex w-full flex-col gap-1.5">
      <span className="text-[12px] font-medium text-rocca-texto-medio">
        {label}
        {required && <span className="ml-0.5 text-rocca-error">*</span>}
      </span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className="h-[34px] w-full rounded-lg border border-rocca-borde-input bg-white px-3 text-[12px] font-semibold text-rocca-texto outline-none transition-colors placeholder:font-normal placeholder:text-rocca-placeholder focus:border-rocca-rojo"
      />
    </label>
  );
}

/* ------------------------------------------------------------------ */
/* Select                                                              */
/* ------------------------------------------------------------------ */

type SelectFieldProps = {
  label: string;
  required?: boolean;
  options: string[];
  value?: string;
  onChange?: (v: string) => void;
};

export function SelectField({
  label,
  required,
  options,
  value,
  onChange,
}: SelectFieldProps) {
  return (
    <label className="flex w-full flex-col gap-1.5">
      <span className="text-[12px] font-medium text-rocca-texto-medio">
        {label}
        {required && <span className="ml-0.5 text-rocca-error">*</span>}
      </span>
      <select
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        className="h-[35px] w-full appearance-none rounded-lg border border-rocca-borde-input bg-white px-3 pr-8 text-[12px] font-semibold text-rocca-texto outline-none transition-colors focus:border-rocca-rojo bg-[url('data:image/svg+xml,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20width=%2210%22%20height=%226%22%20viewBox=%220%200%2010%206%22%3E%3Cpath%20d=%22M1%201l4%204%204-4%22%20fill=%22none%22%20stroke=%22%2364748b%22%20stroke-width=%221.5%22%20stroke-linecap=%22round%22%20stroke-linejoin=%22round%22/%3E%3C/svg%3E')] bg-[position:right_12px_center] bg-no-repeat"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  );
}

/* ------------------------------------------------------------------ */
/* Checkbox                                                            */
/* ------------------------------------------------------------------ */

type CheckboxProps = {
  checked: boolean;
  onChange: (v: boolean) => void;
  children?: ReactNode;
  size?: "sm" | "md";
};

export function Checkbox({ checked, onChange, children, size = "md" }: CheckboxProps) {
  const dim = size === "sm" ? "size-3.5" : "size-4";
  return (
    <label className="flex cursor-pointer select-none items-center gap-2">
      <span
        className={`${dim} flex shrink-0 items-center justify-center rounded-[3px] border transition-colors ${
          checked ? "border-rocca-checkbox bg-rocca-checkbox" : "border-rocca-borde-input bg-white"
        }`}
        onClick={() => onChange(!checked)}
      >
        {checked && (
          <svg
            viewBox="0 0 14 14"
            width={size === "sm" ? 10 : 12}
            height={size === "sm" ? 10 : 12}
            fill="none"
          >
            <path
              d="M3 7.5 6 10.5 11 4"
              stroke="#ffffff"
              strokeWidth={1.75}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </span>
      {children && <span onClick={() => onChange(!checked)}>{children}</span>}
    </label>
  );
}

/* ------------------------------------------------------------------ */
/* Tarjeta de sección (cabecera + cuerpo)                              */
/* ------------------------------------------------------------------ */

type SectionCardProps = {
  numero: string;
  titulo: string;
  descripcion: string;
  accion?: ReactNode;
  children: ReactNode;
};

export function SectionCard({ numero, titulo, descripcion, accion, children }: SectionCardProps) {
  return (
    <section className="overflow-hidden rounded-xl border border-rocca-borde bg-white shadow-[0_1px_2px_rgba(15,23,42,0.04)]">
      {/* Cabecera */}
      <div className="flex items-center justify-between gap-3 border-b border-rocca-borde bg-rocca-tarjeta px-5 py-3.5">
        <div className="flex items-start gap-3">
          <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-rocca-rojo text-[12px] font-black text-white">
            {numero}
          </span>
          <div className="flex flex-col gap-0.5">
            <h2 className="text-[14px] font-bold leading-tight text-rocca-azul-oscuro">
              {titulo}
            </h2>
            <p className="text-[11px] text-rocca-texto-apagado">{descripcion}</p>
          </div>
        </div>
        {accion && <div className="shrink-0">{accion}</div>}
      </div>
      {/* Cuerpo */}
      <div className="p-5">{children}</div>
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Chip / etiqueta de tipo de carne                                    */
/* ------------------------------------------------------------------ */

type ChipProps = {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
};

export function Chip({ label, checked, onChange }: ChipProps) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[12px] font-medium transition-colors ${
        checked
          ? "bg-[#fef3c7] text-[#451a03]"
          : "border border-rocca-borde-input bg-white text-rocca-texto-suave"
      }`}
    >
      <Checkbox size="sm" checked={checked} onChange={onChange} />
      {label}
    </button>
  );
}
