/**
 * Página de detalle de un operador (sucursal/establecimiento).
 * Ruta: /operador/:operadorId
 */

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useAppSelector } from "../../store/hooks";
import type { Operador } from "../../types";
import { useListarCategoriasQuery } from "../../store/api";
import type { CategoriaRequisito } from "../../store/api";

export function PaginaOperadorDetalle() {
  const { operadorId } = useParams<{ operadorId: string }>();
  const id = Number(operadorId);
  const usuario = useAppSelector((s) => s.auth.usuario);
  const personaId = (usuario?.persona_id as number | undefined) ?? null;

  const [operador, setOperador] = useState<Operador | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cargarOperador = () => {
    if (!id || isNaN(id)) {
      setError("ID de operador inválido.");
      setCargando(false);
      return;
    }
    fetch(`/api/registro-operadores/${id}`, {
      credentials: "include",
    })
      .then((r) => {
        if (r.status === 403) throw new Error("No tiene permiso para ver este establecimiento.");
        if (!r.ok) throw new Error(`Error ${r.status}`);
        return r.json();
      })
      .then((data) => {
        setOperador(data);
        setCargando(false);
      })
      .catch((e) => {
        setError(e.message);
        setCargando(false);
      });
  };

  useEffect(() => {
    cargarOperador();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (cargando) {
    return (
      <div style={{ margin: "2rem", padding: "1rem", border: "1px solid #c9d2d8", borderRadius: "6px", background: "#fff" }}>
        Cargando detalle…
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ margin: "2rem", padding: "1rem", border: "1px solid #e74c3c", borderRadius: "6px", background: "#fff" }}>
        <strong>Error:</strong> {error}
        <div style={{ marginTop: "1rem" }}>
          <Link to="/operador" style={{ color: "#2563eb", textDecoration: "underline" }}>
            ← Volver a mis establecimientos
          </Link>
        </div>
      </div>
    );
  }

  if (!operador) {
    return (
      <div style={{ margin: "2rem", padding: "1rem", border: "1px solid #c9d2d8", borderRadius: "6px", background: "#fff" }}>
        Operador no encontrado.
        <div style={{ marginTop: "1rem" }}>
          <Link to="/operador" style={{ color: "#2563eb", textDecoration: "underline" }}>
            ← Volver a mis establecimientos
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ margin: "2rem", padding: "1.5rem", border: "1px solid #c9d2d8", borderRadius: "6px", background: "#fff" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h1>Detalle del Establecimiento</h1>
        <Link to="/operador" style={{ color: "#2563eb", textDecoration: "underline" }}>
          ← Volver
        </Link>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
        <div>
          <h3 style={{ marginBottom: "0.5rem", color: "#334155" }}>Información General</h3>
          <dl style={{ margin: 0 }}>
            <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Establecimiento de Fantasía</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>{operador.establecimiento_fantasia || "—"}</dd>

            <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Categoría</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>{operador.categoria || "—"}</dd>

            <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Estado Registral</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>
              <span
                style={{
                  padding: "0.2rem 0.5rem",
                  borderRadius: "4px",
                  fontSize: "0.85rem",
                  background:
                    operador.estado_registral === "ACTIVO" ? "#dcfce7" :
                    operador.estado_registral === "PENDIENTE" ? "#fef3c7" :
                    "#fee2e2",
                  color:
                    operador.estado_registral === "ACTIVO" ? "#166534" :
                    operador.estado_registral === "PENDIENTE" ? "#92400e" :
                    "#991b1b",
                }}
              >
                {operador.estado_registral}
              </span>
            </dd>

            <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Teléfono</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>{operador.telefono || "—"}</dd>
          </dl>
        </div>

        <div>
          <h3 style={{ marginBottom: "0.5rem", color: "#334155" }}>Domicilio</h3>
          {operador.domicilio ? (
            <dl style={{ margin: 0 }}>
              <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Calle</dt>
              <dd style={{ margin: "0.25rem 0 0" }}>
                {operador.domicilio.calle}
                {operador.domicilio.numero ? ` N°${operador.domicilio.numero}` : ""}
              </dd>

              <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Localidad</dt>
              <dd style={{ margin: "0.25rem 0 0" }}>{operador.domicilio.localidad}</dd>

              <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Provincia</dt>
              <dd style={{ margin: "0.25rem 0 0" }}>{operador.domicilio.provincia}</dd>

              {operador.domicilio.codigo_postal && (
                <>
                  <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Código Postal</dt>
                  <dd style={{ margin: "0.25rem 0 0" }}>{operador.domicilio.codigo_postal}</dd>
                </>
              )}
            </dl>
          ) : (
            <p style={{ color: "#64748b" }}>Sin domicilio registrado.</p>
          )}

          <h3 style={{ marginBottom: "0.5rem", marginTop: "1.5rem", color: "#334155" }}>Titular</h3>
          <dl style={{ margin: 0 }}>
            <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>Nombre</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>{operador.titular || "—"}</dd>

            <dt style={{ fontWeight: 600, marginTop: "0.5rem" }}>CUIT</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>{operador.cuit || "—"}</dd>
          </dl>
        </div>
      </div>

      <RequisitosSection
        operadorId={operador.id}
        categoriaNombre={operador.categoria}
        requisitosCargados={operador.requisitos ?? []}
        onRequisitosCambiados={cargarOperador}
      />

      <div style={{ marginTop: "2rem", paddingTop: "1rem", borderTop: "1px solid #e2e8f0" }}>
        <h3 style={{ marginBottom: "0.5rem", color: "#334155" }}>Fechas</h3>
        <dl style={{ margin: 0, display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div>
            <dt style={{ fontWeight: 600 }}>Alta</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>
              {operador.alta_fecha ? new Date(operador.alta_fecha).toLocaleDateString("es-AR") : "—"}
            </dd>
          </div>
          <div>
            <dt style={{ fontWeight: 600 }}>Baja</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>
              {operador.baja_fecha ? new Date(operador.baja_fecha).toLocaleDateString("es-AR") : "—"}
            </dd>
          </div>
          <div>
            <dt style={{ fontWeight: 600 }}>Creado</dt>
            <dd style={{ margin: "0.25rem 0 0" }}>
              {new Date(operador.creado_en).toLocaleDateString("es-AR")}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Sección de Requisitos con botón de upload                           */
/* ------------------------------------------------------------------ */

/** Requisito ya cargado en el operador (viene de GET /{id}). */
type RequisitoCargado = {
  id: number;
  requisito_categoria_id: number;
  codigo: string | null;
  nombre: string | null;
  estado: string;
  documentos: Array<{
    id: number;
    nombre: string;
    url: string | null;
    mime_type: string;
    size_bytes: number;
  }>;
};

function RequisitosSection({
  operadorId,
  categoriaNombre,
  requisitosCargados,
  onRequisitosCambiados,
}: {
  operadorId: number;
  categoriaNombre: string | null;
  /** Requisitos que el operador ya tiene (con estado y documentos). */
  requisitosCargados: RequisitoCargado[];
  /** Callback para refrescar el operador tras un upload. */
  onRequisitosCambiados: () => void;
}) {
  const { data: categorias, isFetching } = useListarCategoriasQuery();
  const [subiendo, setSubiendo] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Encontrar la categoría del operador en el catálogo (para mostrar
  // solo los requisitos de ESA categoría, no todos).
  const categoria = categorias?.find((c) => c.nombre === categoriaNombre);
  const requisitosCatalogo: CategoriaRequisito[] = categoria?.requisitos ?? [];

  // Index de requisitos cargados por requisito_categoria_id
  const cargadoPorReqCat = new Map<number, RequisitoCargado>();
  for (const rc of requisitosCargados) {
    cargadoPorReqCat.set(rc.requisito_categoria_id, rc);
  }

  const handleUpload = async (requisitoId: number, file: File) => {
    setSubiendo(requisitoId);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `/api/registro-operadores/${operadorId}/requisitos/${requisitoId}/archivo`,
        {
          method: "POST",
          credentials: "include",
          body: formData,
        }
      );

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Error al subir archivo");
      }

      // Refrescar el operador para actualizar los requisitos.
      onRequisitosCambiados();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubiendo(null);
    }
  };

  if (isFetching) {
    return (
      <div style={{ marginTop: "2rem", padding: "1rem", color: "#64748b" }}>
        Cargando requisitos…
      </div>
    );
  }

  if (!categoriaNombre) {
    return (
      <div style={{ marginTop: "2rem", padding: "1rem", color: "#64748b" }}>
        Este establecimiento no tiene categoría asignada.
      </div>
    );
  }

  if (requisitosCatalogo.length === 0) {
    return (
      <div style={{ marginTop: "2rem", padding: "1rem", color: "#64748b" }}>
        Esta categoría no tiene requisitos registrados.
      </div>
    );
  }

  return (
    <div style={{ marginTop: "2rem", paddingTop: "1rem", borderTop: "1px solid #e2e8f0" }}>
      <h3 style={{ marginBottom: "1rem", color: "#334155" }}>
        Requisitos de Papeleo
      </h3>

      {error && (
        <div
          style={{
            marginBottom: "1rem",
            padding: "0.75rem 1rem",
            borderRadius: "6px",
            background: "#fef2f2",
            border: "1px solid #fecaca",
            color: "#dc2626",
            fontSize: "0.85rem",
          }}
        >
          {error}
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {requisitosCatalogo.map((r) => {
          // Cruzar: ¿el operador ya tiene este requisito cargado?
          const cargado = cargadoPorReqCat.get(r.id);
          const documentos = cargado?.documentos ?? [];
          const tieneArchivo = documentos.length > 0;
          const estado = cargado?.estado ?? "PENDIENTE";

          return (
            <div
              key={r.id}
              style={{
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "space-between",
                gap: "0.75rem",
                padding: "1rem",
                borderRadius: "8px",
                border: `1px solid ${tieneArchivo ? "#86efac" : "#e2e8f0"}`,
                background: tieneArchivo ? "#f0fdf4" : "#fff",
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ fontWeight: 600, fontSize: "0.85rem", color: "#1e293b" }}>
                    {r.nombre}
                  </span>
                  {r.obligatorio && (
                    <span
                      style={{
                        padding: "0.1rem 0.5rem",
                        borderRadius: "4px",
                        fontSize: "0.7rem",
                        fontWeight: 700,
                        background: "#fef2f2",
                        color: "#dc2626",
                      }}
                    >
                      OBLIGATORIO
                    </span>
                  )}
                  {tieneArchivo && (
                    <span style={{ color: "#16a34a", fontSize: "1rem" }}>✓</span>
                  )}
                  {!tieneArchivo && estado === "PENDIENTE" && (
                    <span
                      style={{
                        padding: "0.1rem 0.5rem",
                        borderRadius: "4px",
                        fontSize: "0.7rem",
                        fontWeight: 600,
                        background: "#fef3c7",
                        color: "#92400e",
                      }}
                    >
                      PENDIENTE
                    </span>
                  )}
                </div>
                {r.descripcion && (
                  <p style={{ margin: "0.25rem 0 0", fontSize: "0.75rem", color: "#64748b" }}>
                    {r.descripcion}
                  </p>
                )}
                {tieneArchivo && (
                  <div style={{ marginTop: "0.5rem", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                    {documentos.map((a) => (
                      <a
                        key={a.id}
                        href={a.url ?? "#"}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                          padding: "0.25rem 0.5rem",
                          borderRadius: "4px",
                          fontSize: "0.75rem",
                          background: "#fff",
                          color: "#2563eb",
                          textDecoration: "none",
                          border: "1px solid #e2e8f0",
                        }}
                      >
                        📎 {a.nombre}
                      </a>
                    ))}
                  </div>
                )}
              </div>

              <label
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.4rem",
                  padding: "0.5rem 1rem",
                  borderRadius: "6px",
                  fontSize: "0.8rem",
                  fontWeight: 500,
                  cursor: "pointer",
                  background: tieneArchivo ? "#dbeafe" : "#2563eb",
                  color: tieneArchivo ? "#1e40af" : "#fff",
                  opacity: subiendo === r.id ? 0.6 : 1,
                  pointerEvents: subiendo === r.id ? "none" : "auto",
                }}
              >
                {subiendo === r.id ? (
                  <>
                    <span
                      style={{
                        width: "0.75rem",
                        height: "0.75rem",
                        border: "2px solid currentColor",
                        borderTopColor: "transparent",
                        borderRadius: "50%",
                        animation: "spin 0.8s linear infinite",
                      }}
                    />
                    Subiendo…
                  </>
                ) : (
                  <>
                    📤 {tieneArchivo ? "Reemplazar" : "Subir imagen"}
                  </>
                )}
                <input
                  type="file"
                  accept="image/*,.pdf"
                  style={{ display: "none" }}
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleUpload(r.id, file);
                    e.target.value = "";
                  }}
                />
              </label>
            </div>
          );
        })}
      </div>
    </div>
  );
}
