/**
 * Página Padrón de Operadores — sub-ruta /modulo-i/padron.
 * Lista de operadores (sucursal por sucursal) con los estilos de la capa
 * Figma "ROCCA - Control Cadena Cárnica SDE".
 */
import { useCallback } from "react";
import { ModuloILayout } from "../ModuloILayout";
import { PadronSucursales } from "./PadronSucursales";

export function PaginaPadron() {
  const manejarVerCarton = useCallback(() => {
    window.dispatchEvent(new CustomEvent("rocca:ver-carton"));
  }, []);

  return (
    <ModuloILayout onVerCarton={manejarVerCarton}>
      <PadronSucursales />
    </ModuloILayout>
  );
}
