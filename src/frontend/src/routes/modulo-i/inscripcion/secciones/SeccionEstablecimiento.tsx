/**
 * Sección 2 — Datos del Establecimiento / Sucursal
 */
import {
  TextField,
  DepartamentoField,
  LocalidadField,
  SectionCard,
} from "../../../../components/shared/FormField";
import { useAppDispatch, useAppSelector } from "../../../../store/hooks";
import { setCampo, type FormF102 } from "../../../../store/formF102Slice";

export function SeccionEstablecimiento() {
  const dispatch = useAppDispatch();
  const form = useAppSelector((s) => s.formF102.form);

  const set = <K extends keyof FormF102>(key: K, value: FormF102[K]) =>
    dispatch(setCampo(key, value));

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
  );
}
