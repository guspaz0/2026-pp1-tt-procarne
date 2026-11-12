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
        cuit: data.cuit,
        razon_social: data.titular || data.nombreEstablecimiento,
        tipo: data.tipoPersona === "fisica" ? "PRODUCTOR" : "COMERCIALIZADOR",
        categoria: data.categorias[0] ?? null,
        codigo_afip: codigoAfip,
        domicilio_comercial: data.domicilio,
        telefono: data.telefono,
        email: data.email,
      }).unwrap();
      dispatch(
        setAltaMensaje(
          `Operador registrado con CUIT ${op.cuit}. Estado registral: ${op.estado_registral}.`,
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
