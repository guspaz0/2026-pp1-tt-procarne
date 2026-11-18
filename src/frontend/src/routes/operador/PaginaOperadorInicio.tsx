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
    // El backend filtra automáticamente por la persona del usuario autenticado.
    fetch(`/api/registro-operadores`, {
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
              ? `${op.domicilio.calle}${op.domicilio.numero ? ` N°${op.domicilio.numero}` : ""} - ${op.domicilio.localidad}, ${op.domicilio.departamento}`
              : null,
          }))
        );
        setCargando(false);
      })
      .catch((e) => {
        setError(e.message);
        setCargando(false);
      });
  }, []);

  if (cargando) {
    return (
      <div style={{ padding: "1.5rem" }}>
        Cargando sus establecimientos...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "1.5rem", color: "#e74c3c" }}>
        <strong>Error:</strong> {error}
      </div>
    );
  }

  return (
    <div style={{ padding: "1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.4rem", fontWeight: 700 }}>Mis Establecimientos</h1>
          <p style={{ margin: "0.25rem 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            Bienvenido, {usuario?.email}
          </p>
        </div>
        <Link
          to="/operador/registro"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.4rem",
            padding: "0.55rem 1.1rem",
            background: "var(--color-rocca-rojo, #c22338)",
            color: "#fff",
            borderRadius: "8px",
            textDecoration: "none",
            fontWeight: 600,
            fontSize: "0.9rem",
            boxShadow: "0 1px 3px rgba(0,0,0,0.12)",
            transition: "background 0.15s",
          }}
        >
          <span style={{ fontSize: "1.1rem", lineHeight: 1 }}>+</span>
          Agregar establecimiento
        </Link>
      </div>

      {operadores.length === 0 ? (
        <div style={{ padding: "2rem", textAlign: "center", color: "#64748b", border: "1px dashed #cbd5e1", borderRadius: "8px" }}>
          <p style={{ margin: 0, fontSize: "1rem" }}>No tiene establecimientos registrados.</p>
          <p style={{ margin: "0.5rem 0 0", fontSize: "0.85rem" }}>Use el botón "Agregar establecimiento" para registrar su primer operador.</p>
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #334155" }}>
              <th style={{ textAlign: "left", padding: "0.6rem 0.5rem", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.03em", color: "#475569" }}>Razón Social</th>
              <th style={{ textAlign: "left", padding: "0.6rem 0.5rem", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.03em", color: "#475569" }}>Categoría</th>
              <th style={{ textAlign: "left", padding: "0.6rem 0.5rem", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.03em", color: "#475569" }}>Domicilio</th>
              <th style={{ textAlign: "left", padding: "0.6rem 0.5rem", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.03em", color: "#475569" }}>Estado</th>
              <th style={{ textAlign: "left", padding: "0.6rem 0.5rem" }}></th>
            </tr>
          </thead>
          <tbody>
            {operadores.map((op) => (
              <tr key={op.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.6rem 0.5rem", fontWeight: 500 }}>{op.establecimiento_fantasia || "—"}</td>
                <td style={{ padding: "0.6rem 0.5rem" }}>{op.categoria || "—"}</td>
                <td style={{ padding: "0.6rem 0.5rem", fontSize: "0.85rem", color: "#475569" }}>{op.domicilio || "—"}</td>
                <td style={{ padding: "0.6rem 0.5rem" }}>
                  <span
                    style={{
                      padding: "0.2rem 0.55rem",
                      borderRadius: "4px",
                      fontSize: "0.78rem",
                      fontWeight: 600,
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
                <td style={{ padding: "0.6rem 0.5rem" }}>
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
      )}
    </div>
  );
}
