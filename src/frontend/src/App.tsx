import { useEffect, useState } from "react";

type Operador = {
  id: number;
  nombre: string;
  tipo: string;
  estado: string;
};

export default function App() {
  const [operadores, setOperadores] = useState<Operador[]>([]);

  useEffect(() => {
    fetch("/api/operadores")
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
