/**
 * Pantalla de cambio de contraseña forzado.
 *
 * Se muestra cuando el usuario tiene `must_change_password: true` en su
 * `user_metadata` (p. ej. cuando un admin creó su cuenta con la contraseña
 * por defecto = CUIT/DNI).
 *
 * El usuario debe ingresar la contraseña actual y una nueva.
 */
import { useState, type FormEvent } from "react";
import { useChangePasswordMutation } from "../store/api";
import { useAppSelector } from "../store/hooks";

export function CambioContraseñaForzado({ onExit }: { onExit: () => void }) {
  const usuario = useAppSelector((s) => s.auth.usuario);
  const [cambiar] = useChangePasswordMutation();
  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);
  const [cargando, setCargando] = useState(false);

  const manejarSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (nueva.length < 8) {
      setError("La nueva contraseña debe tener al menos 8 caracteres.");
      return;
    }
    if (nueva !== confirmar) {
      setError("La confirmación no coincide con la nueva contraseña.");
      return;
    }

    setCargando(true);
    try {
      // Verificar la contraseña actual haciendo login.
      const loginResult = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email: usuario?.email || "", password: actual }),
      }).then((r) => r.json());

      if (loginResult?.detail) {
        setError("Contraseña actual incorrecta.");
        setCargando(false);
        return;
      }

      // Cambiar la contraseña.
      await cambiar({ new_password: nueva }).unwrap();
      setExito(true);
      // Cerrar sesión y volver a login con la nueva contraseña.
      setTimeout(onExit, 1500);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo cambiar la contraseña."
      );
    } finally {
      setCargando(false);
    }
  };

  if (exito) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-rocca-fondo p-5">
        <div className="w-full max-w-md rounded-xl border border-rocca-exito-borde bg-white p-8 text-center shadow-lg">
          <div className="mb-3 text-4xl">✓</div>
          <h2 className="mb-2 text-lg font-bold text-rocca-texto-oscuro">
            Contraseña actualizada
          </h2>
          <p className="text-[13px] text-rocca-texto-medio">
            Su contraseña fue cambiada correctamente. Se le redirigirá…
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-rocca-fondo p-5">
      <div className="w-full max-w-md rounded-xl border border-rocca-borde bg-white p-8 shadow-lg">
        <h2 className="mb-1 text-lg font-bold text-rocca-texto-oscuro">
          Cambiar contraseña
        </h2>
        <p className="mb-5 text-[13px] text-rocca-texto-suave">
          Por seguridad, debe cambiar su contraseña antes de continuar. La
          contraseña actual es su número de documento (CUIT/DNI).
        </p>

        <form onSubmit={manejarSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-[12px] font-semibold text-rocca-texto-medio">
              Contraseña actual
            </label>
            <input
              type="password"
              value={actual}
              onChange={(e) => setActual(e.target.value)}
              className="w-full rounded-md border border-rocca-borde-input px-3 py-2 text-[13px] outline-none focus:border-rocca-azul"
              placeholder="CUIT o DNI"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-[12px] font-semibold text-rocca-texto-medio">
              Nueva contraseña
            </label>
            <input
              type="password"
              value={nueva}
              onChange={(e) => setNueva(e.target.value)}
              className="w-full rounded-md border border-rocca-borde-input px-3 py-2 text-[13px] outline-none focus:border-rocca-azul"
              placeholder="Mínimo 8 caracteres"
              required
              minLength={8}
            />
          </div>
          <div>
            <label className="mb-1 block text-[12px] font-semibold text-rocca-texto-medio">
              Confirmar nueva contraseña
            </label>
            <input
              type="password"
              value={confirmar}
              onChange={(e) => setConfirmar(e.target.value)}
              className="w-full rounded-md border border-rocca-borde-input px-3 py-2 text-[13px] outline-none focus:border-rocca-azul"
              placeholder="Repita la nueva contraseña"
              required
              minLength={8}
            />
          </div>

          {error && (
            <div className="rounded-md border border-rocca-error-fondo bg-rocca-error-fondo px-3 py-2 text-[12px] text-rocca-error">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={cargando}
            className="w-full rounded-md bg-rocca-rojo px-4 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-rocca-rojo-oscuro disabled:opacity-50"
          >
            {cargando ? "Procesando…" : "Cambiar contraseña"}
          </button>
        </form>
      </div>
    </div>
  );
}
