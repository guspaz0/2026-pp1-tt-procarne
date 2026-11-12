/**
 * Primitivas de formulario del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 * Campos de texto, select, checkbox, tarjeta de sección (cabecera + cuerpo)
 * y chip de tipo de carne.
 */
import { useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import {
  useBuscarLocalidadesQuery,
  useBuscarDepartamentosQuery,
  type Localidad,
  type Departamento,
} from "../../store/georefApi";

/** Devuelve `value` pero "atrasado" `delay` ms (debounce). */
function useDebounce<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

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
        autoComplete="off"
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
/* Combobox de georreferenciación (API pública datos.gob.ar)           */
/* ------------------------------------------------------------------ */

type GeorefComboboxProps<T> = {
  label: string;
  required?: boolean;
  /** Valor ya seleccionado (se muestra en el input). */
  value?: string;
  /** Se llama con el nombre completo al seleccionar. */
  onChange?: (v: string) => void;
  /** Nombre o ID de provincia para acotar la búsqueda (opcional). */
  provincia?: string;
  /** Extrae el nombre a mostrar/fijar de cada resultado. */
  getNombre: (item: T) => string;
  /** Extrae el subtexto (p. ej. "Departamento — Provincia"). */
  getSub?: (item: T) => string | undefined;
  /** Hook de RTK Query que devuelve la lista de resultados. */
  useQuery: (args: { nombre: string; provincia?: string }, opts: { skip: boolean }) => {
    data: { items: T[] } | undefined;
    isFetching: boolean;
    isError: boolean;
  };
  /** Mensaje de error (por defecto genérico). */
  errorLabel?: string;
};

/**
 * Combobox genérico alimentado por la API pública de georreferenciación
 * (https://apis.datos.gob.ar/georef/api/v2.0).
 *
 * El usuario escribe un texto, se busca con debounce (400 ms) y se muestra un
 * dropdown con los resultados. Al seleccionar uno se fija el nombre completo
 * en el campo. También permite escribir libremente si el usuario no elige del
 * dropdown (el valor queda como lo escribió).
 */
function GeorefCombobox<T>({
  label,
  required,
  value,
  onChange,
  provincia,
  getNombre,
  getSub,
  useQuery,
  errorLabel = "No se pudo consultar. Revisá la conexión.",
}: GeorefComboboxProps<T>) {
  // Texto que el usuario está escribiendo. Se sincroniza con `value` cuando
  // se selecciona una opción, pero no en cada keystroke (para no pelear con
  // el dropdown abierto).
  const [texto, setTexto] = useState(value ?? "");
  const [abierto, setAbierto] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const contenedor = useRef<HTMLDivElement>(null);

  // Si `value` cambia desde afuera (p. ej. reset del formulario), lo reflejamos.
  useEffect(() => {
    setTexto(value ?? "");
  }, [value]);

  // Cerrar el dropdown al hacer click fuera.
  useEffect(() => {
    if (!abierto) return;
    const handler = (e: MouseEvent) => {
      if (contenedor.current && !contenedor.current.contains(e.target as Node)) {
        setAbierto(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [abierto]);

  // Búsqueda con debounce: solo cuando hay al menos 2 caracteres. Se busca
  // contra el texto "debounced" (no el del input) para no disparar una query
  // por keystroke.
  const textoBusqueda = useDebounce(texto, 400);
  const hayConsulta = textoBusqueda.trim().length >= 2;
  const { data, isFetching, isError } = useQuery(
    { nombre: textoBusqueda.trim(), provincia },
    { skip: !hayConsulta },
  );
  const resultados = data?.items ?? [];

  const seleccionar = (nombre: string) => {
    onChange?.(nombre);
    setTexto(nombre);
    setAbierto(false);
  };

  const onKey = (e: React.KeyboardEvent) => {
    if (!abierto || resultados.length === 0) {
      if (e.key === "Enter") setAbierto(false);
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, resultados.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      seleccionar(getNombre(resultados[highlight]));
    } else if (e.key === "Escape") {
      setAbierto(false);
    }
  };

  return (
    <div ref={contenedor} className="relative flex w-full flex-col gap-1.5">
      <span className="text-[12px] font-medium text-rocca-texto-medio">
        {label}
        {required && <span className="ml-0.5 text-rocca-error">*</span>}
      </span>
      <input
        type="text"
        autoComplete="off"
        aria-label={label}
        value={texto}
        placeholder="Escribí para buscar…"
        onChange={(e) => {
          setTexto(e.target.value);
          setAbierto(true);
          setHighlight(0);
        }}
        onFocus={() => hayConsulta && setAbierto(true)}
        onKeyDown={onKey}
        className="h-[34px] w-full rounded-lg border border-rocca-borde-input bg-white px-3 text-[12px] font-semibold text-rocca-texto outline-none transition-colors placeholder:font-normal placeholder:text-rocca-placeholder focus:border-rocca-rojo"
      />

      {abierto && hayConsulta && (
        <ul
          role="listbox"
          className="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-rocca-borde-input bg-white py-1 shadow-[0_4px_12px_rgba(15,23,42,0.12)]"
        >
          {isFetching && (
            <li className="px-3 py-2 text-[12px] text-rocca-texto-apagado">Buscando…</li>
          )}
          {!isFetching && isError && (
            <li className="px-3 py-2 text-[12px] text-rocca-error">{errorLabel}</li>
          )}
          {!isFetching && !isError && resultados.length === 0 && (
            <li className="px-3 py-2 text-[12px] text-rocca-texto-apagado">
              Sin resultados para “{texto.trim()}”.
            </li>
          )}
          {!isFetching &&
            resultados.map((item, i) => {
              const nombre = getNombre(item);
              const sub = getSub?.(item);
              return (
                <li
                  key={`${nombre}-${i}`}
                  role="option"
                  aria-selected={i === highlight}
                  onMouseEnter={() => setHighlight(i)}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    seleccionar(nombre);
                  }}
                  className={`flex cursor-pointer flex-col px-3 py-2 ${
                    i === highlight ? "bg-rocca-rojo-claro" : "bg-white"
                  }`}
                >
                  <span className="text-[12px] font-semibold text-rocca-texto">
                    {nombre}
                  </span>
                  {sub && (
                    <span className="text-[11px] text-rocca-texto-apagado">{sub}</span>
                  )}
                </li>
              );
            })}
        </ul>
      )}
    </div>
  );
}

/** Hook adaptador: `useBuscarLocalidadesQuery` → forma esperada por el combobox. */
function useLocalidadesQuery(args: { nombre: string; provincia?: string }, opts: { skip: boolean }) {
  const { data, isFetching, isError } = useBuscarLocalidadesQuery(args, opts);
  return { data: data ? { items: data.localidades } : undefined, isFetching, isError };
}

/** Hook adaptador: `useBuscarDepartamentosQuery` → forma esperada por el combobox. */
function useDepartamentosQuery(args: { nombre: string; provincia?: string }, opts: { skip: boolean }) {
  const { data, isFetching, isError } = useBuscarDepartamentosQuery(args, opts);
  return { data: data ? { items: data.departamentos } : undefined, isFetching, isError };
}

type LocalidadFieldProps = {
  label: string;
  required?: boolean;
  value?: string;
  onChange?: (v: string) => void;
  provincia?: string;
};

/** Campo de localidad (API `GET /localidades`). */
export function LocalidadField(props: LocalidadFieldProps) {
  return (
    <GeorefCombobox<Localidad>
      {...props}
      getNombre={(l) => l.nombre}
      getSub={(l) =>
        [l.departamento?.nombre, l.provincia?.nombre].filter(Boolean).join(" — ")
      }
      useQuery={useLocalidadesQuery}
      errorLabel="No se pudo consultar las localidades. Revisá la conexión."
    />
  );
}

/** Campo de departamento (API `GET /departamentos`). */
export function DepartamentoField(props: LocalidadFieldProps) {
  return (
    <GeorefCombobox<Departamento>
      {...props}
      getNombre={(d) => d.nombre}
      getSub={(d) => d.provincia?.nombre ?? undefined}
      useQuery={useDepartamentosQuery}
      errorLabel="No se pudo consultar los departamentos. Revisá la conexión."
    />
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
