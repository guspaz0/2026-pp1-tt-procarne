/**
 * Rutas del backend, cross-platform (Linux / macOS / Windows).
 *
 * El venv de Python tiene layouts distintos:
 *   - Linux/macOS: .venv/bin/python
 *   - Windows:     .venv/Scripts/python.exe
 *
 * `pythonParaBackend()` devuelve el path del interpretador del venv, y
 * `uvicornCmd()` la orden para arrancar uvicorn con ese intérpretera. Se usa
 * tanto en `playwright.config.ts` (webServer) como en `globalSetup.ts`
 * (para crear las tablas antes de arrancar el backend).
 */
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
// src/frontend/tests/e2e → src/backend
export const BACKEND_DIR = join(__dirname, "..", "..", "..", "backend");
// `configs` vive en app/configs, así que el paquete raíz es `app/`.
export const BACKEND_APP_DIR = join(BACKEND_DIR, "app");

/** Path al Python del venv, según el SO. */
export function pythonParaBackend(): string {
  if (process.platform === "win32") {
    return join(BACKEND_DIR, ".venv", "Scripts", "python.exe");
  }
  return join(BACKEND_DIR, ".venv", "bin", "python");
}

/**
 * Orden (string) para arrancar uvicorn con el Python del venv. Playwright
 * la ejecuta con `shell: true`, así que en Windows se usa `cmd` y en
 * unix `/bin/sh`. El path del intérpretera va entre comillas para que
 * funcione aunque contenga espacios (p. ej. `C:\\Users\\John Doe\\...`).
 */
export function uvicornCmd(): string {
  const py = pythonParaBackend();
  return `"${py}" -m uvicorn app.main:app --host 127.0.0.1 --port 8000`;
}
