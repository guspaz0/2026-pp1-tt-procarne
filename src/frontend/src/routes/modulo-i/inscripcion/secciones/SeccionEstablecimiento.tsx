/**
 * Sección 2 — Datos del Establecimiento / Sucursal
 *
 * El Departamento se acota a Santiago del Estero. La Localidad se muestra
 * solo cuando ya se seleccionó un departamento, y se filtra por ese departamento.
 *
 * El Domicilio usa un combobox con debounce que busca en el backend
 * (GET /api/domicilios) por calle + localidad. Si el usuario no selecciona
 * un resultado, se crea un domicilio nuevo al submit.
 */
import { useEffect, useRef, useState } from "react";
import {
  TextField,
  DepartamentoField,
  LocalidadField,
  SectionCard,
} from "../../../../components/shared/FormField";
import { useAppDispatch, useAppSelector } from "../../../../store/hooks";
import { setCampo, type FormF102 } from "../../../../store/formF102Slice";
import { useBuscarDomiciliosQuery } from "../../../../store/api";

/* ------------------------------------------------------------------ */
/* Combobox de Domicilio (búsqueda en backend con debounce)            */
/* ------------------------------------------------------------------ */

type DomicilioItem = {
  id: number;
  calle: string;
  numero: string | null;
  localidad: string;
  departamento: string;
  provincia: string;
  codigo_postal: string | null;
};

function DomicilioCombobox({
  value,
  localidad,
  departamento,
  onSeleccion,
  onTexto,
}: {
  value: string;
  localidad: string;
  departamento: string;
  onSeleccion: (d: DomicilioItem | null) => void;
  onTexto: (v: string) => void;
}) {
  const [texto, setTexto] = useState(value);
  const [abierto, setAbierto] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const contenedor = useRef<HTMLDivElement>(null);
  const esSeleccion = useRef(false);
  const [debounced, setDebounced] = useState("");

  // Debounce de 1.5 s (se resetea con cada keystroke).
  useEffect(() => {
    if (esSeleccion.current) return;
    const t = setTimeout(() => setDebounced(texto), 1500);
    return () => clearTimeout(t);
  }, [texto]);

  const hayConsulta = debounced.trim().length >= 2;
  const { data: resultados = [], isFetching } = useBuscarDomiciliosQuery(
    { calle: debounced.trim(), localidad: localidad || undefined, departamento: departamento || undefined },
    { skip: !hayConsulta },
  );

  // Cerrar al hacer click fuera.
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

  const seleccionar = (d: DomicilioItem) => {
    esSeleccion.current = true;
    onSeleccion(d);
    setTexto(`${d.calle}${d.numero ? ` N°${d.numero}` : ""}`);
    setAbierto(false);
    setTimeout(() => { esSeleccion.current = false; }, 0);
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
      seleccionar(resultados[highlight]);
    } else if (e.key === "Escape") {
      setAbierto(false);
    }
  };

  return (
    <div ref={contenedor} className="relative flex w-full flex-col gap-1.5">
      <span className="text-[12px] font-medium text-rocca-texto-medio">
        Calle * <span className="ml-0.5 text-rocca-error">*</span>
      </span>
      <input
        type="text"
        value={texto}
        placeholder="Ej: JOSE BENJAMIN ABALOS"
        onChange={(e) => {
          setTexto(e.target.value);
          onTexto(e.target.value);
          onSeleccion(null); // Si escribe, ya no es una selección
          setAbierto(true);
          setHighlight(0);
        }}
        onFocus={() => setAbierto(true)}
        onKeyDown={onKey}
        className="w-full rounded-lg border border-rocca-borde-input bg-white px-3 py-2.5 text-[13px] text-rocca-texto outline-none transition-colors focus:border-rocca-rojo focus:ring-1 focus:ring-rocca-rojo/30"
      />
      {isFetching && abierto && (
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] text-rocca-texto-suave">
          Buscando…
        </span>
      )}
      {abierto && hayConsulta && (
        <div className="absolute z-20 mt-1 max-h-48 w-full overflow-y-auto rounded-lg border border-rocca-borde bg-white shadow-lg">
          {resultados.length === 0 ? (
            <div className="px-3 py-2 text-[12px] text-rocca-texto-suave">
              Sin resultados. Se creará un domicilio nuevo al registrar.
            </div>
          ) : (
            resultados.map((d, i) => (
              <button
                key={d.id}
                type="button"
                onClick={() => seleccionar(d)}
                className={`block w-full px-3 py-2 text-left text-[13px] transition-colors ${
                  i === highlight ? "bg-rocca-rojo/10 text-rocca-rojo" : "text-rocca-texto hover:bg-rocca-fondo"
                }`}
              >
                <span className="font-medium">{d.calle}{d.numero ? ` N°${d.numero}` : ""}</span>
                <span className="ml-2 text-[11px] text-rocca-texto-suave">
                  {d.localidad} — {d.departamento}
                </span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Sección 2                                                           */
/* ------------------------------------------------------------------ */

export function SeccionEstablecimiento() {
  const dispatch = useAppDispatch();
  const form = useAppSelector((s) => s.formF102.form);

  const set = <K extends keyof FormF102>(key: K, value: FormF102[K]) =>
    dispatch(setCampo(key, value));

  // Al cambiar de provincia, limpiar departamento, localidad y domicilio.
  const onProvinciaChange = (v: string) => {
    set("provincia", v);
    if (form.departamento) set("departamento", "");
    if (form.localidad) set("localidad", "");
    if (form.domicilio) set("domicilio", "");
    if (form.domicilio_id) set("domicilio_id", null);
  };

  // Al cambiar de departamento, limpiar localidad y domicilio.
  const onDepartamentoChange = (v: string) => {
    set("departamento", v);
    if (form.localidad) set("localidad", "");
    if (form.domicilio) set("domicilio", "");
    if (form.domicilio_id) set("domicilio_id", null);
  };

  // Al cambiar de localidad, limpiar domicilio.
  const onLocalidadChange = (v: string) => {
    set("localidad", v);
    if (form.domicilio) set("domicilio", "");
    if (form.domicilio_id) set("domicilio_id", null);
  };

  const onDomicilioSeleccion = (d: DomicilioItem | null) => {
    if (d) {
      set("domicilio", d.calle);
      set("domicilio_id", d.id);
      set("numero_calle", d.numero ?? "");
    } else {
      set("domicilio_id", null);
    }
  };

  const onDomicilioTexto = (v: string) => {
    set("domicilio", v);
  };

  return (
    <SectionCard
      numero="2"
      titulo="Datos del Establecimiento / Sucursal (Boca de Expedido o Planta)"
      descripcion="Información física que figurará en el Cartón F 102 para esta sucursal."
    >
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <TextField
          label="Nombre del Establecimiento / Fantasia *"
          required
          placeholder="LA NORITA"
          value={form.nombreEstablecimiento}
          onChange={(v) => set("nombreEstablecimiento", v)}
        />
        <TextField
          label="Provincia *"
          required
          placeholder="Santiago del Estero"
          value={form.provincia}
          onChange={onProvinciaChange}
        />
        {form.provincia ? (
          <DepartamentoField
            label="Departamento Provincial *"
            required
            provincia={form.provincia}
            value={form.departamento}
            onChange={onDepartamentoChange}
          />
        ) : (
          <div className="flex flex-col justify-center rounded-lg border border-dashed border-rocca-borde bg-rocca-fondo px-3 py-2.5">
            <span className="text-[12px] text-rocca-texto-suave">
              Seleccione primero la provincia para buscar el departamento.
            </span>
          </div>
        )}
        {form.departamento ? (
          <LocalidadField
            label="Localidad *"
            required
            provincia={form.provincia}
            departamento={form.departamento}
            value={form.localidad}
            onChange={onLocalidadChange}
          />
        ) : (
          <div className="flex flex-col justify-center rounded-lg border border-dashed border-rocca-borde bg-rocca-fondo px-3 py-2.5">
            <span className="text-[12px] text-rocca-texto-suave">
              Seleccione primero el departamento para buscar la localidad.
            </span>
          </div>
        )}
        {form.localidad ? (
          <DomicilioCombobox
            value={form.domicilio}
            localidad={form.localidad}
            departamento={form.departamento}
            onSeleccion={onDomicilioSeleccion}
            onTexto={onDomicilioTexto}
          />
        ) : (
          <div className="flex flex-col justify-center rounded-lg border border-dashed border-rocca-borde bg-rocca-fondo px-3 py-2.5">
            <span className="text-[12px] text-rocca-texto-suave">
              Seleccione la localidad para buscar el domicilio.
            </span>
          </div>
        )}
        <TextField
          label="N° de Calle"
          placeholder="4582"
          value={form.numero_calle}
          onChange={(v) => set("numero_calle", v)}
        />

      </div>
    </SectionCard>
  );
}
