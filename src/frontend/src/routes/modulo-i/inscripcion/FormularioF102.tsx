/**
 * Formulario de Inscripción / Emisión de Cartón F 102
 * del diseño Figma "ROCCA - Control Cadena Cárnica SDE - /".
 *
 * Secciones:
 *  1. Persona Titular (Clase Base: Persona Física / Jurídica)
 *  2. Datos del Establecimiento / Sucursal
 *  3. Categoría(s) de Actividad Cárnica y Especies
 *  4. Requisitos de Papeleo Exigidos por la Dirección de Agricultura y Ganadería
 */
import { useEffect } from "react";
import {
  Checkbox,
  Chip,
  SectionCard,
  DepartamentoField,
  LocalidadField,
  SelectField,
  TextField,
} from "../../../components/shared/FormField";
import { IconCheck, IconForm, IconUpload } from "../../../components/shared/Icons";
import {
  resetearFormulario as resetearFormularioAction,
  setCampo,
  toggleCarne as toggleCarneAction,
  toggleCategoria as toggleCategoriaAction,
  toggleRequisito as toggleRequisitoAction,
  type FormF102,
} from "../../../store/formF102Slice";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";

/* ------------------------------------------------------------------ */
/* Datos de dominio                                                    */
/* ------------------------------------------------------------------ */

export type CategoriaCarnica = {
  id: string;
  nombre: string;
  codigoAfip: string;
  descripcion: string;
};

export const CATEGORIAS_CARNICAS: CategoriaCarnica[] = [
  {
    id: "CARNICERIAS",
    nombre: "Carnicería Minorista",
    codigoAfip: "922210",
    descripcion: "Venta al por menor de carnes rojas, menudencias y chacinados frescos.",
  },
  {
    id: "SALA_DE_DESPOSTE",
    nombre: "Despostadero / Ciclo II",
    codigoAfip: "101120",
    descripcion: "Despostado, troceo y deshuese de reses vacunas y porcinos.",
  },
  {
    id: "FRIGORIFICO",
    nombre: "Frigorífico / Ciclo I",
    codigoAfip: "101111",
    descripcion: "Matanza y faena de ganado bovino, porcino y aviar en planta propia.",
  },
  {
    id: "MATARIFE",
    nombre: "Matarife Abastecedor",
    codigoAfip: "463120",
    descripcion: "Comercialización mayorista de ganado y carne con faena en plantas autorizadas.",
  },
  {
    id: "DISTRIBUIDOR",
    nombre: "Distribuidor Mayorista",
    codigoAfip: "463110",
    descripcion: "Distribución mayorista de medias reses, cortes y cortes envazados.",
  },
  {
    id: "TRANSPONEDOR",
    nombre: "Transportista de Carnes",
    codigoAfip: "492110",
    descripcion: "Transporte interjurisdiccional y local de carnes frescas en furgón térmico.",
  },
];

export const TIPOS_CARNE = [
  "Bovina",
  "Porcina",
  "Caprina (Cabrito SDE)",
  "Ovino",
  "Aviar",
  "Menudencias/Chacinados",
];

export type Requisito = {
  id: string;
  nombre: string;
  obligatorio: boolean;
  categoria?: string;
};

export const REQUISITOS: Requisito[] = [
  {
    id: "habilitacion_municipal",
    nombre: "Habilitación Municipal del Local Comercial",
    obligatorio: true,
    categoria: "CARNICERIAS",
  },
  {
    id: "libreta_sanitaria",
    nombre: "Libreta Sanitaria del personal expedido por autoridad competente",
    obligatorio: true,
    categoria: "CARNICERIAS",
  },
  {
    id: "desinfeccion",
    nombre: "Certificado de Desinfección y Control de Plagas vigente",
    obligatorio: true,
    categoria: "CARNICERIAS",
  },
  {
    id: "afip",
    nombre: "Constancia de Inscripción en AFIP / ARCA y DOR Santiago del Estero",
    obligatorio: true,
    categoria: "CARNICERIAS",
  },
  {
    id: "croquis",
    nombre: "Croquis o plano de instalaciones de frío y mesas de acero inoxidable",
    obligatorio: false,
    categoria: "CARNICERIAS",
  },
];



/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

type FormularioF102Props = {
  onRegistrar?: (data: FormF102) => void;
  onCancelar?: () => void;
};

export function FormularioF102({ onRegistrar, onCancelar }: FormularioF102Props) {
  const dispatch = useAppDispatch();
  const form = useAppSelector((s) => s.formF102.form);

  // El formulario vive en el store; se inicializa una vez con el departamento por defecto.
  useEffect(() => {
    dispatch(resetearFormularioAction(""));
  }, [dispatch]);

  const set = <K extends keyof FormF102>(key: K, value: FormF102[K]) =>
    dispatch(setCampo(key, value));

  const toggleCategoria = (id: string) => dispatch(toggleCategoriaAction(id));
  const toggleCarne = (t: string) => dispatch(toggleCarneAction(t));
  const toggleRequisito = (id: string) => dispatch(toggleRequisitoAction(id));

  // Los requisitos se muestran siempre (el diseño los lista de forma estática);
  // se marcan como "cumplidos" según el estado del formulario.
  const requisitosAplicables = REQUISITOS;

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
          boxShadow:
            "0 2px 4px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.1)",
        }}
      >
        <div className="flex flex-col gap-1.5">
          <span className="flex items-center gap-1.5 text-[12px] font-bold text-[#fcd34d]">
            <IconForm size={14} />
            Formulario Oficial F 102 • Módulo I ProCarne
          </span>
          <h2 className="text-[18px] font-bold text-white">
            Alta de Operador Cárnico y Emisión de Cartón Provincial
          </h2>
          <p className="max-w-[560px] text-[12px] text-[#cbd5e1]">
            Registra la Persona (Física/Jurídica), su establecimiento/sucursal,
            sus categorías cárnicas con requisitos de papeleo, y genera el
            cartón F102 con su N° Inscripto.
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
      {/* 1. Persona Titular                                         */}
      {/* ---------------------------------------------------------- */}
      <SectionCard
        numero="1"
        titulo="Persona Titular (Clase Base: Persona Física / Jurídica)"
        descripcion="Una persona puede poseer múltiples establecimientos (un cartón F 102 por cada sucursal)."
        accion={
          <div className="flex overflow-hidden rounded-md border border-rocca-borde-input">
            <button
              type="button"
              onClick={() => set("personaExistente", false)}
              className={`px-3 py-1.5 text-[12px] font-semibold transition-colors ${!form.personaExistente
                ? "bg-rocca-rojo text-white"
                : "bg-white text-rocca-texto-suave"
                }`}
            >
              Nueva Persona
            </button>
            <button
              type="button"
              onClick={() => set("personaExistente", true)}
              className={`border-l border-rocca-borde-input px-3 py-1.5 text-[12px] font-semibold transition-colors ${form.personaExistente
                ? "bg-rocca-rojo text-white"
                : "bg-white text-rocca-texto-suave"
                }`}
            >
              Persona Existente (+ Sucursal)
            </button>
          </div>
        }
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <SelectField
            label="Tipo de Persona *"
            required
            options={["Persona Física (Humana / Titular)", "Persona Jurídica (Empresa / Sociedad)"]}
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
            label="C.U.I.T. * (ej.: 23-30917912-9)"
            required
            placeholder="23-30917912-9"
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
              form.tipoPersona === "fisica" ? "OLIVEIRA DANIEL ALBERTO" : "LA NORITA S.R.L."
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
        </div>
      </SectionCard>

      {/* ---------------------------------------------------------- */}
      {/* 2. Datos del Establecimiento / Sucursal                    */}
      {/* ---------------------------------------------------------- */}
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
          <DepartamentoField
            label="Departamento Provincial *"
            required
            value={form.departamento}
            onChange={(v) => set("departamento", v)}
          />
          <LocalidadField
            label="Localidad *"
            required
            value={form.localidad}
            onChange={(v) => set("localidad", v)}
          />
          <TextField
            label="Domicilio Completo * (Calle, N° y Barrio)"
            required
            placeholder="JOSE BENJAMIN ABALOS N. 4582, B. ALMIRANTE BROWN"
            value={form.domicilio}
            onChange={(v) => set("domicilio", v)}
          />
          <TextField
            label="N° Habilitación Sanitaria Oficial"
            placeholder="Municipal N° 419/2026 • ProCarne F 102"
            value={form.habilitacionSanitaria}
            onChange={(v) => set("habilitacionSanitaria", v)}
          />
        </div>
      </SectionCard>

      {/* ---------------------------------------------------------- */}
      {/* 3. Categoría(s) de Actividad Cárnica y Especies             */}
      {/* ---------------------------------------------------------- */}
      <SectionCard
        numero="3"
        titulo="Categoría(s) de Actividad Cárnica y Especies"
        descripcion="Un operador puede poseer múltiples actividades simultáneas con sus respectivos códigos."
      >
        <p className="mb-3 text-[12px] font-semibold text-rocca-texto">
          Seleccione las categorías que desempeña este establecimiento:
        </p>
        <div className="mb-5 grid grid-cols-1 gap-3 md:grid-cols-3">
          {CATEGORIAS_CARNICAS.map((c) => {
            const activa = form.categorias.includes(c.id);
            return (
              <button
                key={c.id}
                type="button"
                onClick={() => toggleCategoria(c.id)}
                className={`flex flex-col gap-1.5 rounded-xl border p-3 text-left transition-colors ${activa
                  ? "border-rocca-rojo bg-rocca-rojo-claro"
                  : "border-rocca-borde bg-white"
                  }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span
                    className={`text-[13px] font-semibold ${activa ? "text-rocca-texto" : "text-rocca-texto-medio"
                      }`}
                  >
                    {c.nombre}
                  </span>
                  <Checkbox size="sm" checked={activa} onChange={() => toggleCategoria(c.id)} />
                </div>
                <span className="text-[11px] text-rocca-texto-apagado">
                  Código AFIP: {c.codigoAfip}
                </span>
                <span className="text-[11px] leading-snug text-rocca-texto-suave">
                  {c.descripcion}
                </span>
              </button>
            );
          })}
        </div>

        {/* Tipo de carne */}
        <p className="mb-2 text-[12px] font-semibold text-rocca-texto">
          Tipo de Carne Comercializada (Figurará en el Cartón):
        </p>
        <div className="flex flex-wrap gap-2">
          {TIPOS_CARNE.map((t) => (
            <Chip
              key={t}
              label={t}
              checked={form.tiposCarne.includes(t)}
              onChange={() => toggleCarne(t)}
            />
          ))}
        </div>
      </SectionCard>

      {/* ---------------------------------------------------------- */}
      {/* 4. Requisitos de Papeleo Exigidos                           */}
      {/* ---------------------------------------------------------- */}
      <SectionCard
        numero="4"
        titulo="Requisitos de Papeleo Exigidos por la Dirección de Agricultura y Ganadería"
        descripcion="Documentación y certificaciones requeridas para las categorías seleccionadas."
      >
        <div className="flex flex-col gap-2">
          {requisitosAplicables.map((r) => {
            const cumplido = !!form.requisitos[r.id];
            return (
              <div
                key={r.id}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 ${cumplido
                  ? "border border-rocca-exito-borde bg-rocca-exito-claro/80"
                  : "border border-rocca-borde bg-white"
                  }`}
              >
                <Checkbox checked={cumplido} onChange={() => toggleRequisito(r.id)} />
                <span
                  className={`flex-1 text-[12px] font-medium ${cumplido ? "text-rocca-exito-texto" : "text-rocca-texto-medio"
                    }`}
                >
                  {r.nombre}
                </span>
                {r.obligatorio && (
                  <span className="rounded bg-rocca-error-fondo px-2 py-0.5 text-[10px] font-bold text-rocca-error">
                    OBLIGATORIO
                  </span>
                )}
                {r.categoria && (
                  <span className="text-[11px] text-rocca-texto-muy-apagado">
                    {CATEGORIAS_CARNICAS.find((c) => c.id === r.categoria)?.nombre}
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {/* Sello AGROTRAZA — desactivado
        <div className="mt-4 flex items-center gap-3 rounded-xl border border-rocca-exito-borde bg-rocca-exito-claro p-3">
          <IconLeaf size={18} className="shrink-0 text-[#059669]" />
          <div className="flex-1">
            <span className="block text-[13px] font-semibold text-rocca-exito-texto">
              Adhesión al Sello AGROTRAZA Sustentable (Ley Nac. 27.279)
            </span>
            <span className="block text-[12px] text-[#065f46]">
              Certifica gestión de residuos cárnicos y trazabilidad ambiental.
            </span>
          </div>
          <Checkbox checked={form.selloAgrotraza} onChange={(v) => set("selloAgrotraza", v)} />
        </div>
        */}
      </SectionCard>

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
          Registrar Operador y Emitir Cartón F 102
        </button>
      </div>
    </form>
  );
}
