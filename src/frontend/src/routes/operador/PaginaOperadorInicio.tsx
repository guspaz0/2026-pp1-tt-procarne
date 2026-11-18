/**
 * Página de inicio para operadores.
 * Muestra la lista de operadores (sucursales) de la persona vinculada.
 */

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAppSelector } from "../../store/hooks";
import type { Operador } from "../../types";

interface OperadorResumen {
  id: number;
  establecimiento_fantasia: string | null;
  categoria: string | null;
  estado_registral: string;
  domicilio: string | null;
}

export function PaginaOperadorInicio() {
  const usuario = useAppSelector((s) => s.auth.usuario);
  const personaId = (usuario?.persona_id as number | undefined) ?? null;
  const [operadores, setOperadores] = useState<OperadorResumen[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!personaId) {
      setError("No se encontró una persona vinculada a su cuenta.");
      setCargando(false);
      return;
    }

    // Fetch operadores de la persona
    fetch(`/api/registro-operadores?persona_id=${personaId}`, {
      credentials: "include",
    })
      .then((r) => {
        if (!r.ok) throw new Error(`Error ${r.status}`);
        return r.json();
      })
      .then((data) => {
        const ops: Operador[] = Array.isArray(data) ? data : data.operadores ?? [];
        setOperadores(
          ops.map((op) => ({
            id: op.id,
            establecimiento_fantasia: op.establecimiento_fantasia,
            categoria: op.categoria,
            estado_registral: op.estado_registral,
            domicilio: op.domicilio
              ? `${op.domicilio.calle}${op.domicilio.numero ? ` N°${op.domicilio.numero}` : ""} - ${op.domicilio.localidad}, ${op.domicilio.provincia}`
              : null,
          }))
        );
        setCargando(false);
      })
      .catch((e) => {
        setError(e.message);
        setCargando(false);
      });
  }, [personaId]);

  if (cargando) {
    return (
      <div style={{ margin: "2rem", padding: "1rem", border: "1px solid #c9d2d8", borderRadius: "6px", background: "#fff" }}>
        Cargando sus establecimientos...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ margin: "2rem", padding: "1rem", border: "1px solid #e74c3c", borderRadius: "6px", background: "#fff" }}>
        <strong>Error:</strong> {error}
      </div>
    );
  }

  return (
    <div style={{ margin: "2rem", padding: "1.5rem", border: "1px solid #c9d2d8", borderRadius: "6px", background: "#fff" }}>
      <h1>Mis Establecimientos</h1>
      <p>Bienvenido, {usuario?.email}. Estos son sus operadores registrados:</p>

      {operadores.length === 0 ? (
        <div>
          <p>No tiene establecimientos registrados.</p>
          <Link
            to="/operador/registro"
            style={{ color: "#2563eb", textDecoration: "underline", fontWeight: 600 }}
          >
            Registrar nuevo establecimiento
          </Link>
        </div>
      ) : (
        <>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
            <thead>
              <tr style={{ borderBottom: "2px solid #334155" }}>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Razón Social</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Categoría</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Domicilio</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Estado</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}></th>
              </tr>
            </thead>
            <tbody>
              {operadores.map((op) => (
                <tr key={op.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                  <td style={{ padding: "0.5rem" }}>{op.establecimiento_fantasia || "—"}</td>
                  <td style={{ padding: "0.5rem" }}>{op.categoria || "—"}</td>
                  <td style={{ padding: "0.5rem", fontSize: "0.85rem" }}>{op.domicilio || "—"}</td>
                  <td style={{ padding: "0.5rem" }}>
                    <span
                      style={{
                        padding: "0.2rem 0.5rem",
                        borderRadius: "4px",
                        fontSize: "0.8rem",
                        background:
                          op.estado_registral === "ACTIVO" ? "#dcfce7" :
                          op.estado_registral === "PENDIENTE" ? "#fef3c7" :
                          "#fee2e2",
                        color:
                          op.estado_registral === "ACTIVO" ? "#166534" :
                          op.estado_registral === "PENDIENTE" ? "#92400e" :
                          "#991b1b",
                      }}
                    >
                      {op.estado_registral}
                    </span>
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    <Link
                      to={`/operador/${op.id}`}
                      style={{ color: "#2563eb", textDecoration: "underline", fontSize: "0.9rem" }}
                    >
                      Ver detalle
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: "1.5rem" }}>
            <Link
              to="/operador/registro"
              style={{
                display: "inline-block",
                padding: "0.5rem 1rem",
                background: "#2563eb",
                color: "#fff",
                borderRadius: "6px",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              + Registrar nuevo establecimiento
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
