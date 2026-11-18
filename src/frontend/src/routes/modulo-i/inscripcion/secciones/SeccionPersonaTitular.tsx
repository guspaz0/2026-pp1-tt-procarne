/**
 * Sección 1 — Persona Titular (Clase Base: Persona Física / Jurídica)
 *
 * Comportamiento según rol:
 * - **admin**: puede buscar una persona existente en el padrón (por CUIT o
 *   nombre) y asignarla, o registrar una persona nueva.
 * - **operador / común**: la sección se autocompleta con los datos de la
 *   persona vinculada a su sesión (user_metadata.persona_id). No se puede
 *   cambiar: es siempre la misma persona.
 */
import { useEffect, useState } from "react";
import {
  SelectField,
  TextField,
  SectionCard,
} from "../../../../components/shared/FormField";
import { useAppDispatch, useAppSelector } from "../../../../store/hooks";
import { setCampo, type FormF102 } from "../../../../store/formF102Slice";
import { personaIdDe, cuitDe } from "../../../../store/auth";

/* ------------------------------------------------------------------ */
/* Tipos de persona del padrón (GET /api/personas)                     */
/* ------------------------------------------------------------------ */

type PersonaPadron = {
  id: number;
  tipo: string;
  tipo_documento: string;
  identificador: string;
  nombre: string;
  email: string | null;
};

export function SeccionPersonaTitular() {
  const dispatch = useAppDispatch();
  const form = useAppSelector((s) => s.formF102.form);
  const usuario = useAppSelector((s) => s.auth.usuario);

  const esAdmin = usuario?.rol === "admin";
  const personaId = personaIdDe(usuario);
  const cuitUsuario = cuitDe(usuario);

  const set = <K extends keyof FormF102>(key: K, value: FormF102[K]) =>
    dispatch(setCampo(key, value));

  /* ---------------------------------------------------------------- */
  /* Rol operador: autocompletar con datos de la sesión                */
  /* ---------------------------------------------------------------- */

  useEffect(() => {
    if (!esAdmin && cuitUsuario) {
      set("cuit", cuitUsuario);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [esAdmin, cuitUsuario]);

  /* ---------------------------------------------------------------- */
  /* Rol admin: buscar persona en el padrón                            */
  /* ---------------------------------------------------------------- */

  const [personas, setPersonas] = useState<PersonaPadron[]>([]);
  const [buscando, setBuscando] = useState(false);
  const [personaSeleccionada, setPersonaSeleccionada] = useState<
    PersonaPadron | null
  >(null);

  useEffect(() => {
    if (!esAdmin) return;
    setBuscando(true);
    fetch("/api/personas", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : []))
      .then((data: PersonaPadron[]) => setPersonas(data))
      .catch(() => setPersonas([]))
      .finally(() => setBuscando(false));
  }, [esAdmin]);

  const filtrarPersonas = (q: string): PersonaPadron[] => {
    if (!q.trim()) return personas;
    const lower = q.toLowerCase();
    return personas.filter(
      (p) =>
        p.nombre.toLowerCase().includes(lower) ||
        p.identificador.toLowerCase().includes(lower)
    );
  };

  const [busqueda, setBusqueda] = useState("");
  const resultados = filtrarPersonas(busqueda);

  const seleccionarPersona = (p: PersonaPadron) => {
    setPersonaSeleccionada(p);
    set("titular", p.nombre);
    set("cuit", p.identificador);
    if (p.email) set("email", p.email);
    set(
      "tipoPersona",
      p.tipo === "FISICA" ? "fisica" : "juridica"
    );
  };

  /* ---------------------------------------------------------------- */
  /* Render: rol operador (autocompletado, no editable)                */
  /* ---------------------------------------------------------------- */

  if (!esAdmin) {
    return (
      <SectionCard
        numero="1"
        titulo="Persona Titular"
        descripcion="Datos autocompletados desde su cuenta. No se pueden modificar."
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-rocca-texto-suave">
              Tipo de Persona
            </label>
            <div className="rounded-md border border-rocca-borde-input bg-rocca-fondo px-3 py-2 text-[13px] text-rocca-texto-medio">
              {form.tipoPersona === "fisica"
                ? "Persona Física"
                : "Persona Jurídica"}
            </div>
          </div>
          <div>
            <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-rocca-texto-suave">
              C.U.I.T. / D.N.I.
            </label>
            <div className="rounded-md border border-rocca-borde-input bg-rocca-fondo px-3 py-2 text-[13px] text-rocca-texto-medio">
              {form.cuit || cuitUsuario || "—"}
            </div>
          </div>
          <div>
            <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-rocca-texto-suave">
              {form.tipoPersona === "fisica"
                ? "Apellido y Nombre"
                : "Razón Social"}
            </label>
            <div className="rounded-md border border-rocca-borde-input bg-rocca-fondo px-3 py-2 text-[13px] text-rocca-texto-medio">
              {form.titular || usuario?.email || "—"}
            </div>
          </div>
        </div>
      </SectionCard>
    );
  }

  /* ---------------------------------------------------------------- */
  /* Render: rol admin (búsqueda en padrón + nueva persona)            */
  /* ---------------------------------------------------------------- */

  return (
    <SectionCard
      numero="1"
      titulo="Persona Titular (Clase Base: Persona Física / Jurídica)"
      descripcion="Una persona puede poseer múltiples establecimientos (un cartón F 102 por cada sucursal)."
      accion={
        <div className="flex overflow-hidden rounded-md border border-rocca-borde-input">
          <button
            type="button"
            onClick={() => {
              set("personaExistente", false);
              setPersonaSeleccionada(null);
            }}
            className={`px-3 py-1.5 text-[12px] font-semibold transition-colors ${
              !form.personaExistente
                ? "bg-rocca-rojo text-white"
                : "bg-white text-rocca-texto-suave"
            }`}
          >
            Nueva Persona
          </button>
          <button
            type="button"
            onClick={() => set("personaExistente", true)}
            className={`border-l border-rocca-borde-input px-3 py-1.5 text-[12px] font-semibold transition-colors ${
              form.personaExistente
                ? "bg-rocca-rojo text-white"
                : "bg-white text-rocca-texto-suave"
            }`}
          >
            Persona Existente (+ Sucursal)
          </button>
        </div>
      }
    >
      {/* --- Búsqueda en padrón (solo admin + persona existente) --- */}
      {form.personaExistente && (
        <div className="mb-4 rounded-lg border border-rocca-borde bg-rocca-fondo p-3">
          <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-rocca-texto-suave">
            Buscar persona en el padrón
          </label>
          <div className="relative">
            <input
              type="text"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por nombre o CUIT…"
              className="w-full rounded-md border border-rocca-borde-input bg-white px-3 py-2 text-[13px] text-rocca-texto-oscuro outline-none focus:border-rocca-azul"
            />
            {buscando && (
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] text-rocca-texto-suave">
                Cargando…
              </span>
            )}
          </div>

          {/* Resultados */}
          {!buscando && resultados.length > 0 && (
            <div className="mt-2 max-h-48 overflow-y-auto rounded-md border border-rocca-borde bg-white">
              {resultados.slice(0, 20).map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => seleccionarPersona(p)}
                  className={`flex w-full items-center justify-between border-b border-rocca-borde px-3 py-2 text-left text-[12px] transition-colors last:border-b-0 hover:bg-rocca-azul-claro ${
                    personaSeleccionada?.id === p.id
                      ? "bg-rocca-azul-claro font-semibold"
                      : ""
                  }`}
                >
                  <span className="text-rocca-texto-oscuro">{p.nombre}</span>
                  <span className="text-rocca-texto-suave">
                    {p.tipo_documento} {p.identificador}
                  </span>
                </button>
              ))}
            </div>
          )}
          {!buscando && resultados.length === 0 && busqueda.trim() && (
            <p className="mt-2 text-[12px] text-rocca-texto-suave">
              No se encontraron personas para «{busqueda}».
            </p>
          )}

          {/* Persona seleccionada */}
          {personaSeleccionada && (
            <div className="mt-2 flex items-center gap-2 rounded-md bg-rocca-exito-claro px-3 py-2 text-[12px] text-rocca-exito-texto">
              <span>✓</span>
              <span>
                Persona asignada: <strong>{personaSeleccionada.nombre}</strong>{" "}
                ({personaSeleccionada.tipo_documento}{" "}
                {personaSeleccionada.identificador})
              </span>
            </div>
          )}
        </div>
      )}

      {/* --- Formulario de datos --- */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <SelectField
          label="Tipo de Persona *"
          required
          options={[
            "Persona Física (Humana / Titular)",
            "Persona Jurídica (Empresa / Sociedad)",
          ]}
          value={
            form.tipoPersona === "fisica"
              ? "Persona Física (Humana / Titular)"
              : "Persona Jurídica (Empresa / Sociedad)"
          }
          onChange={(v) =>
            set(
              "tipoPersona",
              v.startsWith("Persona Física") ? "fisica" : "juridica",
            )
          }
        />
        <TextField
          label={
            form.personaExistente
              ? "C.U.I.T. (opcional — se usa la persona del padrón)"
              : "C.U.I.T. * (ej.: 23-30917912-5)"
          }
          required={!form.personaExistente}
          placeholder="23-30917912-5"
          value={form.cuit}
          onChange={(v) => set("cuit", v)}
        />
        <TextField
          label={
            form.tipoPersona === "fisica"
              ? "Apellido y Nombre del Titular *"
              : "Razón Social *"
          }
          required
          placeholder={
            form.tipoPersona === "fisica"
              ? "OLIVEIRA DANIEL ALBERTO"
              : "LA NORITA S.R.L."
          }
          value={form.titular}
          onChange={(v) => set("titular", v)}
        />
        {form.tipoPersona === "fisica" && (
          <TextField
            label="D.N.I."
            placeholder="30.917.912"
            value={form.dni}
            onChange={(v) => set("dni", v)}
          />
        )}
        <TextField
          label="Teléfono"
          placeholder="(0385) 431-8910"
          value={form.telefono}
          onChange={(v) => set("telefono", v)}
        />
        <TextField
          label="Correo Electrónico"
          type="email"
          placeholder="contacto@procarne.gob.ar"
          value={form.email}
          onChange={(v) => set("email", v)}
        />
        {/* Crear cuenta de login (solo admin + nueva persona) */}
        {!form.personaExistente && (
          <label className="flex cursor-pointer items-start gap-2 md:col-span-3">
            <input
              type="checkbox"
              checked={form.crearCuenta}
              onChange={(e) => set("crearCuenta", e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-rocca-borde-input text-rocca-rojo"
            />
            <span className="text-[12px] text-rocca-texto-medio">
              <strong>Crear cuenta de login</strong> para la persona con el email
              indicado. La contraseña inicial será el número de documento (CUIT/DNI).
              La persona deberá cambiarla en su primer acceso.
            </span>
          </label>
        )}
      </div>
    </SectionCard>
  );
}
