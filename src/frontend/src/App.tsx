import { useEffect, useState } from "react";

/// <reference types="vite/client" />

type Operador = {
  id: number;
  nombre: string;
  tipo: string;
  estado: string;
};

// En dev (Vite) el proxy lleva /api al backend; en prod la API vive en Render.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export default function App() {
  const [operadores, setOperadores] = useState<Operador[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/api/operadores`)
      .then((res) => res.json())
      .then(setOperadores);
  }, []);

  return (
    <main style={{ fontFamily: "system-ui", margin: "2rem auto", maxWidth: 640 }}>
      <h1>ROCCA</h1>
      <p>Registro de Operadores y Control de la Cadena Cárnica</p>
      <ul>
        {operadores.map((op) => (
          <li key={op.id}>
            {op.nombre} — {op.tipo} ({op.estado})
          </li>
        ))}
      </ul>
    </main>
  );
}
