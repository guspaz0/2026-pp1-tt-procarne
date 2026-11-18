/**
 * Página de registro de nuevo establecimiento (operador) para operadores.
 * Ruta: /operador/registro
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppSelector } from "../../store/hooks";
import type { OperadorIn } from "../../types";

const CATEGORIAS = [
  { valor: "SALA_DE_DESPOSTE", label: "Sala de Desposte" },
  { valor: "CAMARAS_FRIGORIFICAS", label: "Cámaras Frigoríficas" },
  { valor: "FABRICA_DE_CHACINADOS", label: "Fábrica de Chacinados" },
  { valor: "CARNICERIAS", label: "Carnicerías" },
  { valor: "CARNICERIA_CON_CAMARA", label: "Carnicería con Cámara" },
  { valor: "TRANSPONEDOR", label: "Transportador" },
  { valor: "SUPERMERCADO", label: "Supermercado" },
  { valor: "DISTRIBUIDOR", label: "Distribuidor" },
];

export function PaginaOperadorRegistro() {
  const navigate = useNavigate();
  const usuario = useAppSelector((s) => s.auth.usuario);
  const personaId = (usuario?.persona_id as number | undefined) ?? null;

  const [razonSocial, setRazonSocial] = useState("");
  const [categoria, setCategoria] = useState("");
  const [telefono, setTelefono] = useState("");
  const [calle, setCalle] = useState("");
  const [numero, setNumero] = useState("");
  const [localidad, setLocalidad] = useState("");
  const [provincia, setProvincia] = useState("");
  const [codigoPostal, setCodigoPostal] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setExito(null);

    if (!razonSocial.trim()) {
      setError("La razón social es obligatoria.");
      return;
    }
    if (!categoria) {
      setError("Seleccione una categoría.");
      return;
    }
    if (!calle.trim() || !localidad.trim() || !provincia.trim()) {
      setError("Complete el domicilio (calle, localidad y provincia).");
      return;
    }

    const payload: OperadorIn = {
      tipo: categoria,
      establecimiento_fantasia: razonSocial.trim(),
      cuit: null, // Se toma de la sesión
      domicilio: {
        calle: calle.trim(),
        numero: numero.trim() || null,
        localidad: localidad.trim(),
        provincia: provincia.trim(),
        codigo_postal: codigoPostal.trim() || null,
      },
      telefono: telefono.trim() || null,
      email: usuario?.email ?? null,
      categoria,
    };

    setEnviando(true);
    try {
      const resp = await fetch("/api/registro-operadores", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        throw new Error(data.detail || `Error ${resp.status}`);
      }

      const nuevo = await resp.json();
      setExito(`Establecimiento "${nuevo.establecimiento_fantasia}" registrado correctamente.`);
      // Reset form
      setRazonSocial("");
      setCategoria("");
      setTelefono("");
      setCalle("");
      setNumero("");
      setLocalidad("");
      setProvincia("");
      setCodigoPostal("");

      // Navegar al detalle
      setTimeout(() => {
        navigate(`/operador/${nuevo.id}`);
      }, 1500);
    } catch (e: any) {
      setError(e.message || "Error al registrar el establecimiento.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div style={{ margin: "2rem", padding: "1.5rem", border: "1px solid #c9d2d8", borderRadius: "6px", background: "#fff", maxWidth: "700px" }}>
      <h1>Registrar Nuevo Establecimiento</h1>
      <p>Complete los datos para dar de alta un nuevo operador/sucursal.</p>

      {exito && (
        <div style={{ padding: "1rem", background: "#dcfce7", border: "1px solid #16a34a", borderRadius: "6px", marginBottom: "1rem" }}>
          {exito}
        </div>
      )}

      {error && (
        <div style={{ padding: "1rem", background: "#fee2e2", border: "1px solid #dc2626", borderRadius: "6px", marginBottom: "1rem" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "grid", gap: "1rem" }}>
        <div>
          <label style={{ display: "block", fontWeight: 600, marginBottom: "0.25rem" }}>
            Razón Social *
          </label>
          <input
            type="text"
            value={razonSocial}
            onChange={(e) => setRazonSocial(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
            placeholder="Ej: Carnicería El Gallo"
          />
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 600, marginBottom: "0.25rem" }}>
            Categoría *
          </label>
          <select
            value={categoria}
            onChange={(e) => setCategoria(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
          >
            <option value="">Seleccione una categoría…</option>
            {CATEGORIAS.map((cat) => (
              <option key={cat.valor} value={cat.valor}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ display: "block", fontWeight: 600, marginBottom: "0.25rem" }}>
            Teléfono
          </label>
          <input
            type="tel"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
            placeholder="Ej: 351-4567890"
          />
        </div>

        <fieldset style={{ border: "1px solid #cbd5e1", borderRadius: "6px", padding: "1rem" }}>
          <legend style={{ fontWeight: 600, padding: "0 0.5rem" }}>Domicilio</legend>
          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "0.5rem" }}>
            <div>
              <label style={{ display: "block", fontWeight: 500, marginBottom: "0.25rem" }}>Calle *</label>
              <input
                type="text"
                value={calle}
                onChange={(e) => setCalle(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontWeight: 500, marginBottom: "0.25rem" }}>Número</label>
              <input
                type="text"
                value={numero}
                onChange={(e) => setNumero(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
              />
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.5rem", marginTop: "0.5rem" }}>
            <div>
              <label style={{ display: "block", fontWeight: 500, marginBottom: "0.25rem" }}>Localidad *</label>
              <input
                type="text"
                value={localidad}
                onChange={(e) => setLocalidad(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontWeight: 500, marginBottom: "0.25rem" }}>Provincia *</label>
              <input
                type="text"
                value={provincia}
                onChange={(e) => setProvincia(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontWeight: 500, marginBottom: "0.25rem" }}>Código Postal</label>
              <input
                type="text"
                value={codigoPostal}
                onChange={(e) => setCodigoPostal(e.target.value)}
                style={{ width: "100%", padding: "0.5rem", border: "1px solid #cbd5e1", borderRadius: "4px" }}
              />
            </div>
          </div>
        </fieldset>

        <button
          type="submit"
          disabled={enviando}
          style={{
            padding: "0.75rem 1.5rem",
            background: enviando ? "#94a3b8" : "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            fontWeight: 600,
            cursor: enviando ? "not-allowed" : "pointer",
            fontSize: "1rem",
          }}
        >
          {enviando ? "Registrando…" : "Registrar Establecimiento"}
        </button>
      </form>
    </div>
  );
}
