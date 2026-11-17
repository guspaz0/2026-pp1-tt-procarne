/**
 * Helpers del usuario autenticado.
 *
 * Todos los usuarios son titulares comunes: no existe rol de administrador.
 * La persona titular vinculada al usuario se guarda en `user_metadata.persona_id`
 * (InsForge lo expone en el JWT).
 */
import type { Usuario } from "../types";

/** Id de la persona titular vinculada al usuario (o null si no está). */
export function personaIdDe(usuario: Usuario | null | undefined): number | null {
  const pid = usuario?.user_metadata?.persona_id;
  if (typeof pid === "number") return pid;
  if (typeof pid === "string" && pid.trim() !== "") {
    const n = Number(pid);
    if (!Number.isNaN(n)) return n;
  }
  return null;
}

/** CUIT de la persona titular (si está en los metadatos). */
export function cuitDe(usuario: Usuario | null | undefined): string | null {
  const cuit = usuario?.user_metadata?.cuit;
  return typeof cuit === "string" && cuit ? cuit : null;
}
