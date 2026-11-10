/**
 * Definición de rutas del sistema ROCCA.
 * Cada módulo del NavBar tiene su propia ruta.
 */
import { Navigate, Route, Routes } from "react-router-dom";
import { PaginaInicio } from "./routes/PaginaInicio";
import { PaginaRegistroOperadores } from "./routes/modulo-i/inscripcion/PaginaRegistroOperadores";
import { PaginaPadron } from "./routes/modulo-i/padron/PaginaPadron";
import { PaginaJerarquia } from "./routes/modulo-i/jerarquia/PaginaJerarquia";
import { ModuloPage } from "./routes/ModuloPage";

export function AppRoutes() {
  return (
    <Routes>
      {/* Operadores — sub-rutas por tab */}
      <Route path="/operadores" element={<Navigate to="/operadores/padron" replace />} />
      <Route path="/operadores/padron" element={<PaginaPadron />} />
      <Route path="/operadores/jerarquia" element={<PaginaJerarquia />} />
      <Route path="/operadores/inscripcion" element={<PaginaRegistroOperadores />} />

      {/* Remitos REC y Tránsito */}
      <Route
        path="/remitos"
        element={
          <ModuloPage
            titulo="Remitos REC y Tránsito"
            descripcion="Gestión de remitos de la Red de Comercialización (REC) y tránsitos de ganado y carnes entre jurisdicciones."
          />
        }
      />

      {/* Fiscalización en Ruta */}
      <Route
        path="/fiscalizacion"
        element={
          <ModuloPage
            titulo="Fiscalización en Ruta"
            descripcion="Control y fiscalización de transporte de carnes y ganado en ruta, con geolocalización y verificación de remitos."
          />
        }
      />

      {/* Monitor Estratégico */}
      <Route
        path="/monitor"
        element={
          <ModuloPage
            titulo="Monitor Estratégico"
            descripcion="Panel de indicadores estratégicos, tableros de control y trazabilidad de la cadena cárnica provincial."
          />
        }
      />

      {/* Portal Público */}
      <Route
        path="/portal"
        element={
          <ModuloPage
            titulo="Portal Público"
            descripcion="Consulta pública de operadores habilitados, cartones F 102 vigentes y datos abiertos de la cadena cárnica."
          />
        }
      />

      {/* Faena en Origen */}
      <Route
        path="/faena"
        element={
          <ModuloPage
            titulo="Faena en Origen"
            descripcion="Registro y control de faena en origen (establecimientos de cría y engorde) con trazabilidad de origen."
          />
        }
      />

      {/* Raíz: página de inicio con iframe del portal público */}
      <Route path="/" element={<PaginaInicio />} />

      {/* Fallback: cualquier ruta desconocida vuelve a Operadores */}
      <Route path="*" element={<Navigate to="/operadores" replace />} />
    </Routes>
  );
}
