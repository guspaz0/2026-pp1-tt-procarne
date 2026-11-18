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
import { useLoginMutation, useSignupMutation } from "../store/api";
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
  const [tipoDoc, setTipoDoc] = useState<"CUIT" | "DNI">("CUIT");
  const [documento, setDocumento] = useState("");
  const [aceptoPrivacidad, setAceptoPrivacidad] = useState(false);
  const [mostrarPolitica, setMostrarPolitica] = useState(false);
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
    setDocumento("");
    setTipoDoc("CUIT");
    setAceptoPrivacidad(false);
    setMostrarPolitica(false);
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
    if (modo === "signup" && !documento.trim()) {
      setError(tipoDoc === "CUIT" ? "Ingrese el CUIT del titular (11 dígitos)." : "Ingrese el DNI del titular (8 dígitos).");
      return;
    }
    if (modo === "signup") {
      const digitos = documento.replace(/\D/g, "");
      if (tipoDoc === "CUIT" && digitos.length !== 11) {
        setError("El CUIT debe tener 11 dígitos.");
        return;
      }
      if (tipoDoc === "DNI" && digitos.length !== 8) {
        setError("El DNI debe tener 8 dígitos.");
        return;
      }
    }
    if (modo === "signup" && !aceptoPrivacidad) {
      setError("Debe aceptar la Política de Privacidad y Tratamiento de Datos para crear la cuenta.");
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
          name: nombre.trim() || undefined,
          cuit: documento.trim(),
          tipo_documento: tipoDoc,
          user_metadata: { nombre: nombre.trim() || undefined },
        }).unwrap();
      }
      // El backend ya fijó la cookie HttpOnly con el token de InsForge.
      // Guardamos solo los metadatos del usuario en el store local.
      if (result.user) {
        dispatch(setSesion({ usuario: result.user }));
      }
      // Redirigir según rol del usuario
      const rol = (result.user?.rol as string) ?? "admin";
      const redirect = (location.state as { from?: string } | null)?.from ?? (rol === "operador" ? "/operador" : "/admin");
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
              <>
                <TextField
                  label="Nombre completo"
                  placeholder="Juan Pérez / RAZÓN SOCIAL S.A."
                  value={nombre}
                  onChange={setNombre}
                />
                <div className="flex flex-col gap-1">
                  <label className="text-[12px] font-semibold text-rocca-texto">Tipo de documento *</label>
                  <div className="flex gap-2">
                    {(["CUIT", "DNI"] as const).map((tipo) => (
                      <button
                        key={tipo}
                        type="button"
                        onClick={() => setTipoDoc(tipo)}
                        className={`flex-1 rounded-lg border px-3 py-2 text-[13px] font-semibold transition-colors ${
                          tipoDoc === tipo
                            ? "border-rocca-rojo bg-rocca-rojo/5 text-rocca-rojo"
                            : "border-rocca-borde text-rocca-texto-apagado hover:border-rocca-texto-apagado"
                        }`}
                      >
                        {tipo}
                      </button>
                    ))}
                  </div>
                </div>
                <TextField
                  label={tipoDoc === "CUIT" ? "C.U.I.T. del titular * (ej.: 30-11111111-4)" : "D.N.I. del titular * (ej.: 11111111)"}
                  required
                  placeholder={tipoDoc === "CUIT" ? "30-11111111-4" : "11111111"}
                  value={documento}
                  onChange={setDocumento}
                />
              </>
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

            {modo === "signup" && (
              <div className="flex flex-col gap-1.5">
                <label className="flex cursor-pointer select-none items-start gap-2">
                  <input
                    type="checkbox"
                    checked={aceptoPrivacidad}
                    onChange={(e) => setAceptoPrivacidad(e.target.checked)}
                    className="mt-0.5 size-4 shrink-0 accent-[var(--color-rocca-rojo)]"
                  />
                  <span className="text-[12px] leading-snug text-rocca-texto-medio">
                    Acepto la{" "}
                    <button
                      type="button"
                      onClick={() => setMostrarPolitica(true)}
                      className="font-semibold text-rocca-azul-oscuro underline underline-offset-2 hover:text-rocca-rojo"
                    >
                      Política de Privacidad y Tratamiento de Datos
                    </button>{" "}
                    y consiento el tratamiento de mis datos personales para la
                    gestión del Registro de Operadores de la Cadena Cárnica. *
                  </span>
                </label>
              </div>
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
                (modo === "signup" && (!passwordConfirm || !documento.trim() || !aceptoPrivacidad))
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

      {/* Modal: Política de Privacidad y Tratamiento de Datos */}
      {mostrarPolitica && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Política de Privacidad y Tratamiento de Datos"
          onClick={(e) => {
            if (e.target === e.currentTarget) setMostrarPolitica(false);
          }}
        >
          <div className="flex max-h-[80vh] w-full max-w-[560px] flex-col overflow-hidden rounded-xl bg-white shadow-xl">
            <div className="flex items-center justify-between border-b border-rocca-borde px-5 py-3">
              <h2 className="text-[14px] font-bold text-rocca-azul-oscuro">
                Política de Privacidad y Tratamiento de Datos
              </h2>
              <button
                type="button"
                onClick={() => setMostrarPolitica(false)}
                aria-label="Cerrar"
                className="text-[18px] leading-none text-rocca-texto-apagado hover:text-rocca-texto"
              >
                ×
              </button>
            </div>
            <div className="flex-1 space-y-3 overflow-y-auto px-5 py-4 text-[12px] leading-relaxed text-rocca-texto-medio">
              <p>
                <strong className="text-rocca-texto">Responsable del tratamiento.</strong> El
                Registro de Operadores y Control de la Cadena Cárnica (ROCCA) actúa como
                responsable del tratamiento de los datos personales que usted proporciona al
                registrarse.
              </p>
              <p>
                <strong className="text-rocca-texto">Finalidad.</strong> Sus datos se utilizan
                exclusivamente para la gestión del registro de operadores, la emisión de los
                cartones F 102, el seguimiento de la documentación exigida por la Dirección de
                Agricultura y Ganadería y la comunicación de novedades relacionadas con su
                inscripción.
              </p>
              <p>
                <strong className="text-rocca-texto">Datos que se recogen.</strong> Datos de
                identificación del titular (nombre o razón social, CUIT o DNI), datos de contacto
                (email, teléfono) y datos del establecimiento (domicilio, categoría de actividad).
              </p>
              <p>
                <strong className="text-rocca-texto">Conservación y acceso.</strong> Los datos se
                conservan mientras la inscripción se encuentre vigente y solo son accesibles al
                personal autorizado de la Dirección de Agricultura y Ganadería. No se ceden a
                terceros ajenos a la gestión del registro, salvo obligación legal.
              </p>
              <p>
                <strong className="text-rocca-texto">Sus derechos.</strong> Puede ejercer los
                derechos de acceso, rectificación, supresión y oposición sobre sus datos
                personales dirigiéndose al área de atención al usuario del Registro.
              </p>
              <p>
                <strong className="text-rocca-texto">Seguridad.</strong> Se aplican medidas
                técnicas y organizativas razonables para proteger sus datos contra el acceso
                no autorizado, la pérdida o la alteración.
              </p>
              <p>
                La aceptación de esta política es obligatoria para crear la cuenta y es revocable
                en cualquier momento mediante el ejercicio de sus derechos.
              </p>
            </div>
            <div className="flex justify-end gap-2 border-t border-rocca-borde px-5 py-3">
              <button
                type="button"
                onClick={() => {
                  setAceptoPrivacidad(true);
                  setMostrarPolitica(false);
                }}
                className="rounded-lg bg-rocca-rojo px-4 py-2 text-[13px] font-bold text-white transition-colors hover:bg-[#b91c1c]"
              >
                Aceptar y continuar
              </button>
              <button
                type="button"
                onClick={() => setMostrarPolitica(false)}
                className="rounded-lg px-4 py-2 text-[13px] font-medium text-rocca-texto-medio hover:bg-rocca-fondo"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
