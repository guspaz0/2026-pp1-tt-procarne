/**
 * Sección 3 — Categoría de Actividad Cárnica y Especies
 *
 * Las categorías (y sus requisitos) NO están hardcodeadas:
 * se cargan desde el backend vía `useListarCategoriasQuery()`.
 */
import {
  Chip,
  SectionCard,
  SelectField,
} from "../../../../components/shared/FormField";
import { useAppDispatch, useAppSelector } from "../../../../store/hooks";
import {
  setCampo,
  toggleCarne as toggleCarneAction,
  type FormF102,
} from "../../../../store/formF102Slice";
import {
  useListarCategoriasQuery,
  type CategoriaCarnicaApi,
} from "../../../../store/api";

export const TIPOS_CARNE = [
  "Bovina",
  "Porcina",
  "Caprina (Cabrito SDE)",
  "Ovino",
  "Aviar",
  "Menudencias/Chacinados",
];

export function SeccionCategoria() {
  const dispatch = useAppDispatch();
  const form = useAppSelector((s) => s.formF102.form);

  const { data: categoriasApi, isFetching: cargando } =
    useListarCategoriasQuery();

  const set = <K extends keyof FormF102>(key: K, value: FormF102[K]) =>
    dispatch(setCampo(key, value));

  const toggleCarne = (t: string) => dispatch(toggleCarneAction(t));

  const categoriaSeleccionada = (categoriasApi ?? []).find((c) =>
    form.categorias.includes(c.nombre),
  );

  const seleccionarCategoria = (nombre: string) => {
    set("categorias", nombre ? [nombre] : []);
  };

  return (
    <SectionCard
      numero="3"
      titulo="Categoría de Actividad Cárnica y Especies"
      descripcion="Categoría declarada ante el Registro Provincial (con código AFIP/DGR asociado)."
    >
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <SelectField
          label="Categoría del Establecimiento *"
          required
          disabled={cargando}
          placeholder={
            cargando ? "Cargando categorías…" : "Seleccione una categoría"
          }
          options={(categoriasApi ?? []).map((c: CategoriaCarnicaApi) => ({
            value: c.nombre,
            label: `${c.nombre}${c.descripcion ? ` — ${c.descripcion}` : ""}`,
          }))}
          value={categoriaSeleccionada?.nombre ?? ""}
          onChange={seleccionarCategoria}
        />
        <div className="flex flex-col justify-center gap-1 rounded-lg border border-rocca-borde bg-white px-3 py-2.5">
          {categoriaSeleccionada ? (
            <>
              <span className="text-[11px] font-bold uppercase tracking-wide text-rocca-texto-apagado">
                Categoría seleccionada
              </span>
              <span className="text-[13px] font-semibold text-rocca-texto">
                {categoriaSeleccionada.nombre}
              </span>
              {categoriaSeleccionada.descripcion && (
                <span className="text-[11px] leading-snug text-rocca-texto-suave">
                  {categoriaSeleccionada.descripcion}
                </span>
              )}
            </>
          ) : (
            <span className="text-[12px] text-rocca-texto-suave">
              Elija la categoría de actividad de este establecimiento; los
              requisitos de papeleo se mostrarán en la sección 4.
            </span>
          )}
        </div>
      </div>

      {/* Tipo de carne */}
      <p className="mb-2 mt-4 text-[12px] font-semibold text-rocca-texto">
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
  );
}
