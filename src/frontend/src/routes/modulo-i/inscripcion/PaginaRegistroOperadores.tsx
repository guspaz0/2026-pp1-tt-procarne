/**
 * Página del Módulo I: Registro Provincial de Operadores de la Cadena Cárnica.
 * Sub-ruta /modulo-i/inscripcion — Formulario F 102.
 *
 * El alta se gestiona con la mutación RTK Query `registrar`, que invalida la
 * lista del padrón y expone el mensaje de resultado en el store.
 */
import { FormularioF102, CATEGORIAS_CARNICAS } from "./FormularioF102";
import type { FormF102 } from "../../../store/formF102Slice";
import { setAltaMensaje } from "../../../store/operadoresSlice";
import { useListarQuery, useRegistrarMutation } from "../../../store/api";
import { parsearDomicilio } from "../../../types";
import { useAppDispatch, useAppSelector } from "../../../store/hooks";
import { ModuloILayout } from "../ModuloILayout";

export function PaginaRegistroOperadores() {
  const dispatch = useAppDispatch();
  const mensaje = useAppSelector((s) => s.operadores.altaMensaje);
  // Precarga la lista al entrar a la sección: alimenta los contadores de las tabs.
  useListarQuery();
  const [registrar] = useRegistrarMutation();

  const manejarRegistrar = async (data: FormF102) => {
    try {
      // Códigos AFIP de las actividades económicas seleccionadas (N:M).
      const codigoAfip = data.categorias
        .map((id) => CATEGORIAS_CARNICAS.find((c) => c.id === id)?.codigoAfip)
        .filter((c): c is string => Boolean(c));
      const op = await registrar({
        // El titular (persona) viene de la sesión; el CUIT es opcional.
        cuit: data.cuit.trim() || null,
        razon_social: data.titular || data.nombreEstablecimiento,
        // Tipo de establecimiento según la primera categoría elegida.
        tipo: data.categorias[0] ?? "CARNICERIA",
        categoria: data.categorias[0] ?? null,
        codigo_afip: codigoAfip,
        domicilio: parsearDomicilio(data.domicilio),
        telefono: data.telefono,
        email: data.email,
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
