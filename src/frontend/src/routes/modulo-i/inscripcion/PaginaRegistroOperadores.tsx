/**
 * Página del Módulo I: Registro Provincial de Operadores de la Cadena Cárnica.
 * Sub-ruta /modulo-i/inscripcion — Formulario F 102.
 *
 * El alta se gestiona con la mutación RTK Query `registrar`, que invalida la
 * lista del padrón y expone el mensaje de resultado en el store.
 */
import { FormularioF101 as FormularioF102 } from "./FormularioF101";
import type { FormF102 } from "../../../store/formF102Slice";
import { setAltaMensaje } from "../../../store/operadoresSlice";
import {
  useListarCategoriasQuery,
  useListarQuery,
  useRegistrarMutation,
} from "../../../store/api";
import { parsearDomicilio } from "../../../types";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import { ModuloILayout } from "../ModuloILayout";

export function PaginaRegistroOperadores() {
  const dispatch = useAppDispatch();
  const mensaje = useAppSelector((s) => s.operadores.altaMensaje);
  // Precarga la lista al entrar a la sección: alimenta los contadores de las tabs.
  useListarQuery();
  const [registrar] = useRegistrarMutation();

  // Categorías desde el backend (compartido con el formulario).
  const { data: categorias } = useListarCategoriasQuery();

  const manejarRegistrar = async (data: FormF102) => {
    try {
      const op = await registrar({
        // El titular (persona) viene de la sesión; el CUIT es opcional.
        cuit: data.cuit.trim() || null,
        establecimiento_fantasia: data.titular || data.nombreEstablecimiento,
        // Categoría declarada (nombre de la fila en ``categorias``).
        categoria: data.categorias[0] ?? null,
        domicilio: parsearDomicilio(data.domicilio),
        tipos_carne: data.tiposCarne.join(", ") || null,
        telefono: data.telefono,
        email: data.email,
        // Crear cuenta de login (solo admin + nueva persona).
        crear_cuenta: data.crearCuenta,
        tipo_documento: data.tipoPersona === "fisica" ? "DNI" : "CUIT",
      }).unwrap();
      dispatch(
        setAltaMensaje(
          `Operador registrado (CUIT ${op.cuit ?? "de la sesión"}). Estado registral: ${op.estado_registral}.`,
        ),
      );
    } catch (err) {
      dispatch(
        setAltaMensaje(
          `Error al registrar: ${err instanceof Error ? err.message : JSON.stringify(err)}`,
        ),
      );
    }
  };

  return (
    <ModuloILayout>
      <div className="p-5">
        <FormularioF102
          onRegistrar={manejarRegistrar}
          onCancelar={() => dispatch(setAltaMensaje(null))}
        />
      </div>

      {mensaje && (
        <div
          className={`mx-5 mb-5 rounded-lg border px-4 py-3 text-[13px] ${
            mensaje.startsWith("Error")
              ? "border-[#fecaca] bg-rocca-error-fondo text-rocca-error"
              : "border-rocca-exito-borde bg-rocca-exito-claro text-rocca-exito-texto"
          }`}
          role="status"
        >
          {mensaje}
        </div>
      )}
    </ModuloILayout>
  );
}
