/**
 * Página de inicio: iframe con el portal público de ProCarne + botón flotante
 * para acceder al dashboard autenticado.
 */
import { Link } from "react-router-dom";
import { IconUser } from "../components/shared/Icons";

const PORTAL_URL = "https://procarnesgo.netlify.app/";

export function PaginaInicio() {
  return (
    <div className="relative flex h-screen w-full flex-col overflow-hidden bg-rocca-fondo">
      {/* Iframe con el portal público */}
      <iframe
        src={PORTAL_URL}
        title="Portal Público ProCarne"
        className="h-full w-full flex-1 border-0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />

      {/* Botón flotante para acceso al dashboard */}
      <Link
        to="/operadores"
        className="absolute bottom-6 right-6 flex items-center gap-2 rounded-full bg-rocca-rojo px-5 py-3 text-[14px] font-bold text-white shadow-[0_4px_12px_rgba(139,20,37,0.3)] transition-all hover:bg-rocca-rojo-oscuro hover:shadow-[0_6px_16px_rgba(139,20,37,0.4)] focus:outline-none focus:ring-2 focus:ring-rocca-rojo focus:ring-offset-2"
      >
        <IconUser size={18} className="text-white" />
        <span>Acceso Usuarios</span>
      </Link>
    </div>
  );
}
