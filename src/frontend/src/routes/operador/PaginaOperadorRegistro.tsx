/**
 * Página de registro de nuevo establecimiento (operador) para operadores.
 * Ruta: /operador/registro
 *
 * Usa las secciones 2, 3 y 4 del formulario F 102 (la sección 1 — Persona
 * Titular — se omite porque el operador ya tiene su persona vinculada).
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { IconCheck, IconForm } from "../../components/shared/Icons";
import {
  resetearFormulario as resetearFormularioAction,
  type FormF102,
} from "../../store/formF102Slice";
import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { useRegistrarMutation, useCrearDomicilioMutation } from "../../store/api";
import { useToast } from "../../store/toastSlice";
import { SeccionEstablecimiento } from "../modulo-i/inscripcion/secciones/SeccionEstablecimiento";
import { SeccionCategoria } from "../modulo-i/inscripcion/secciones/SeccionCategoria";
import { SeccionRequisitos } from "../modulo-i/inscripcion/secciones/SeccionRequisitos";

export function PaginaOperadorRegistro() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const usuario = useAppSelector((s) => s.auth.usuario);
  const form = useAppSelector((s) => s.formF102.form);
  const [registrar, { isLoading: enviando }] = useRegistrarMutation();
  const [crearDomicilio] = useCrearDomicilioMutation();
  const toast = useToast();

  // Resetear el formulario al entrar.
  useEffect(() => {
    dispatch(resetearFormularioAction(""));
  }, [dispatch]);

  const manejarRegistrar = async (data: FormF102) => {
    try {
      // Si el usuario no seleccionó un domicilio existente, se crea uno nuevo.
      let domicilioId = data.domicilio_id;
      if (!domicilioId && data.domicilio.trim()) {
        const nuevo = await crearDomicilio({
          calle: data.domicilio.replace(/\s*N°.*$/, "").trim(),
          numero: data.numero_calle || undefined,
          localidad: data.localidad,
          departamento: data.departamento,
          provincia: data.provincia,
        }).unwrap();
        domicilioId = nuevo.id;
      }

      // Recopilar los requisitos marcados como cumplidos (códigos).
      const requisitosCumplidos = Object.entries(data.requisitos)
        .filter(([, v]) => v)
        .map(([k]) => k.replace(/^req:/, ""));

      await registrar({
        persona_id: usuario?.persona_id ?? null,
        cuit: null,
        establecimiento_fantasia: data.nombreEstablecimiento,
        categoria: data.categorias[0] ?? null,
        domicilio: {
          calle: data.domicilio.replace(/\s*N°.*$/, "").trim(),
          numero: data.numero_calle || null,
          localidad: data.localidad,
          departamento: data.departamento,
          provincia: data.provincia,
          codigo_postal: null,
          id: domicilioId,
        },
        tipos_carne: data.tiposCarne.join(", ") || null,
        telefono: data.telefono || null,
        email: data.email || null,
        crear_cuenta: false,
        tipo_documento: "DNI",
        documento_requisitos: requisitosCumplidos.length > 0 ? requisitosCumplidos : null,
      }).unwrap();

      toast.exito(
        "Establecimiento registrado",
        `"${data.nombreEstablecimiento}" fue registrado correctamente. Estado: PENDIENTE.`,
      );
      navigate("/operador", { replace: true });
    } catch (err: unknown) {
      let detalle = "Ocurrió un error inesperado al registrar el establecimiento.";
      if (err && typeof err === "object" && "data" in err) {
        const data = (err as { data?: { detail?: string } }).data;
        if (data?.detail) {
          detalle = data.detail;
        }
      } else if (err instanceof Error) {
        detalle = err.message;
      }
      toast.error("No se pudo registrar", detalle, 10000);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    manejarRegistrar(form);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {/* Banner de encabezado */}
      <div
        className="flex flex-col gap-4 rounded-xl px-6 py-5 md:flex-row md:items-center md:justify-between"
        style={{
          background:
            "linear-gradient(90deg, #0f172a 0%, #540d17 50%, #0f172a 100%)",
          boxShadow: "0 2px 4px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.1)",
        }}
      >
        <div className="flex flex-col gap-1.5">
          <span className="flex items-center gap-1.5 text-[12px] font-bold text-[#fcd34d]">
            <IconForm size={14} />
            Registro de Establecimiento
          </span>
          <h2 className="text-[18px] font-bold text-white">
            Alta de Nuevo Establecimiento
          </h2>
          <p className="max-w-[560px] text-[12px] text-[#cbd5e1]">
            Titular: {usuario?.email}. Registre los datos del establecimiento,
            su categoría cárnica y los requisitos de papeleo.
          </p>
        </div>
      </div>

      {/* Secciones 2, 3, 4 (la 1 — Persona — se omite) */}
      <SeccionEstablecimiento />
      <SeccionCategoria />
      <SeccionRequisitos />

      {/* Acciones */}
      <div className="flex flex-wrap items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={() => navigate("/operador")}
          className="rounded-lg px-4 py-2.5 text-[13px] font-medium text-rocca-texto-medio transition-colors hover:bg-white"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={enviando}
          className="flex items-center gap-2 rounded-lg bg-rocca-rojo px-5 py-2.5 text-[13px] font-bold text-white shadow-[0_2px_8px_rgba(139,20,37,0.3)] transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          <IconCheck size={14} />
          {enviando ? "Registrando…" : "Registrar Establecimiento"}
        </button>
      </div>
    </form>
  );
}
