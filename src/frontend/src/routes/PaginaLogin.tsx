/**
 * Página de login de ROCCA.
 * El usuario ingresa con su email y contraseña (`POST /api/auth/login`).
 *
 * El backend (FastAPI) orquesta InsForge: al éxito fija una **cookie
 * HttpOnly** con el token de InsForge. El frontend no la lee: el navegador
 * la envía automáticamente en cada petición y el middleware de FastAPI la
 * valida.
 *
 * On success: guarda los metadatos del usuario en el store (auth slice) y
 * redirige a la app principal (`/operadores`).
 *
 * Incluye un formulario de registro (`POST /api/auth/signup`) para crear
 * nuevos usuarios.
 */
import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useLoginMutation, useSignupMutation } from "../store/authApi";
import { setSesion } from "../store/authSlice";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import { TextField } from "../components/shared/FormField";

type Modo = "login" | "signup";

export function PaginaLogin() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const usuario = useAppSelector((s) => s.auth.usuario);

  const [modo, setModo] = useState<Modo>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [nombre, setNombre] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [login, { isLoading: cargandoLogin }] = useLoginMutation();
  const [signup, { isLoading: cargandoSignup }] = useSignupMutation();

  // Si ya hay usuario en el store (p. ej. recarga), redirige directo a la app.
  if (usuario && usuario.email) {
    const redirect = (location.state as { from?: string } | null)?.from ?? "/operadores";
    return <Navigate to={redirect} replace />;
  }

  const cargando = modo === "login" ? cargandoLogin : cargandoSignup;

  function cambiarModo(nuevo: Modo) {
    setModo(nuevo);
    setError(null);
    setPassword("");
    setPasswordConfirm("");
    setNombre("");
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    // Validaciones locales
    if (!email || !password) {
      setError("Complete todos los campos obligatorios.");
      return;
    }
    if (modo === "signup" && password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres.");
      return;
    }
    if (modo === "signup" && password !== passwordConfirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    try {
      let result;
      if (modo === "login") {
        result = await login({ email, password }).unwrap();
      } else {
        result = await signup({
          email,
          password,
          user_metadata: nombre.trim() ? { nombre: nombre.trim() } : {},
        }).unwrap();
      }
      // El backend ya fijó la cookie HttpOnly con el token de InsForge.
      // Guardamos solo los metadatos del usuario en el store local.
      if (result.user) {
        dispatch(setSesion({ usuario: result.user }));
      }
      const redirect = (location.state as { from?: string } | null)?.from ?? "/operadores";
      navigate(redirect, { replace: true });
    } catch (err: unknown) {
      const data = err as { data?: { detail?: string } };
      setError(
        data?.data?.detail ??
          (modo === "login"
            ? "Email o contraseña incorrectos"
            : "No se pudo crear el usuario. Verifique que el email no esté registrado."),
      );
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#f1f5f9]">
      {/* Header institucional */}
      <header
        className="w-full"
        style={{
          background: "linear-gradient(90deg, #0f1e36 0%, #0f172a 50%, #540d17 100%)",
        }}
      >
        <div className="mx-auto flex max-w-[1280px] items-center gap-3 px-4 py-4">
          <div
            className="flex size-12 shrink-0 items-center justify-center rounded-lg text-[20px] font-bold tracking-[1px] text-white"
            style={{ background: "var(--color-rocca-rojo)", border: "1px solid #c22338" }}
            aria-label="ROCCA"
          >
            R
          </div>
          <div className="flex flex-col">
            <span className="text-[22px] font-black leading-none text-white">ROCCA</span>
            <span className="text-[11px] text-[#cbd5e1]">
              Registro de Operadores y Control de la Cadena Cárnica
            </span>
          </div>
        </div>
      </header>

      {/* Tarjeta de login/registro */}
      <main className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-[420px] overflow-hidden rounded-xl border border-rocca-borde bg-white shadow-[0_1px_2px_rgba(15,23,42,0.08)]">
          {/* Tabs Login / Registro */}
          <div className="flex border-b border-rocca-borde">
            <button
              type="button"
              onClick={() => cambiarModo("login")}
              className={`flex-1 px-4 py-3 text-[13px] font-semibold transition-colors ${
                modo === "login"
                  ? "border-b-2 border-rocca-rojo text-rocca-azul-oscuro"
                  : "text-rocca-texto-apagado hover:text-rocca-texto"
              }`}
            >
              Iniciar sesión
            </button>
            <button
              type="button"
              onClick={() => cambiarModo("signup")}
              className={`flex-1 px-4 py-3 text-[13px] font-semibold transition-colors ${
                modo === "signup"
                  ? "border-b-2 border-rocca-rojo text-rocca-azul-oscuro"
                  : "text-rocca-texto-apagado hover:text-rocca-texto"
              }`}
            >
              Crear cuenta
            </button>
          </div>

          <div className="px-6 pt-4">
            <p className="text-[12px] text-rocca-texto-apagado">
              {modo === "login"
                ? "Ingrese con su email y contraseña."
                : "Complete sus datos para crear una nueva cuenta."}
            </p>
          </div>

          <form onSubmit={onSubmit} className="flex flex-col gap-4 p-6">
            {modo === "signup" && (
              <TextField
                label="Nombre completo"
                placeholder="Juan Pérez"
                value={nombre}
                onChange={setNombre}
              />
            )}
            <TextField
              label="Email"
              required
              type="email"
              placeholder="usuario@ejemplo.com"
              value={email}
              onChange={setEmail}
            />
            <TextField
              label="Contraseña"
              required
              type="password"
              placeholder={modo === "signup" ? "Mínimo 8 caracteres" : "••••••••"}
              value={password}
              onChange={setPassword}
            />
            {modo === "signup" && (
              <TextField
                label="Confirmar contraseña"
                required
                type="password"
                placeholder="••••••••"
                value={passwordConfirm}
                onChange={setPasswordConfirm}
              />
            )}

            {error && (
              <p className="rounded-lg border border-rocca-error/30 bg-rocca-error/5 px-3 py-2 text-[12px] font-medium text-rocca-error">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={
                cargando ||
                !email ||
                !password ||
                (modo === "signup" && !passwordConfirm)
              }
              className="mt-1 flex h-[38px] items-center justify-center gap-2 rounded-lg bg-rocca-rojo text-[13px] font-bold text-white transition-colors hover:bg-[#b91c1c] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {cargando
                ? modo === "login"
                  ? "Ingresando…"
                  : "Creando cuenta…"
                : modo === "login"
                  ? "Ingresar"
                  : "Crear cuenta"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
