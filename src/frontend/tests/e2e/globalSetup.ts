/**
 * globalSetup / globalTeardown de la suite E2E.
 *
 * Crea una base de datos SQLite EFÍMERA y LIMPIA (sin datos: los tests de
 * inscripción son los que crean los operadores) y exporta su URL en
 * ``process.env.ROCCA_E2E_DB_URL`` para que el `webServer` de
 * `playwright.config.ts` la pase al backend.
 *
 * Así el keybinding de neotest (<leader>tr) levanta TODO (backend con BD
 * limpia + frontend) sin que nadie arranque nada a mano. InsForge sigue
 * siendo el IdP real (auth) — solo la base de datos es local y temporal.
 *
 * - El path usa un timestamp + pid para que cada corrida sea única.
 * - `crear_tablas()` se llama aquí (no depende del backend para el schema):
 *   el backend lo llama de nuevo al arrancar y es idempotente.
 * - El teardown borra el archivo al terminar (pasa o falle la suite).
 */
import { existsSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { e2eDbPath, e2eDbUrl } from "./e2eDb";
import { BACKEND_APP_DIR, pythonParaBackend } from "./backendPaths";

/**
 * Crea el SQLite temporal vacío (con schema). No seedeamos nada: los tests
 * de inscripción crean los operadores. El path viene de `e2eDb.ts` (mismo que
 * usa la config para el webServer).
 */
function crearDbE2E(): string {
  const url = e2eDbUrl();
  const dbPath = e2eDbPath();

  // Importamos los modelos del backend para que Base.metadata esté completo y
  // creamos el engine + tablas. Esto garantiza el schema aunque el backend
  // tarde en arrancar (el webServer espera a /api/health después).
  // pythonParaBackend() resuelve .venv/bin/python (unix) o
  // .venv/Scripts/python.exe (Windows).
  execFileSync(pythonParaBackend(), [
    "-c",
    [
      `import sys; sys.path.insert(0, ${JSON.stringify(BACKEND_APP_DIR)})`,
      `from configs.dao import crear_dao`,
      `dao = crear_dao(${JSON.stringify(url)})`,
      `dao.crear_tablas()`,
      `print("e2e db ready:", ${JSON.stringify(dbPath)})`,
    ].join("\n"),
  ], { stdio: "inherit" });

  // La exportamos también por si algún script externo la necesita.
  process.env.ROCCA_E2E_DB_URL = url;
  return url;
}

export default async function globalSetup(): Promise<void> {
  crearDbE2E();
  console.log(`[e2e] BD temporal: ${e2eDbUrl()}`);
}

export async function globalTeardown(): Promise<void> {
  const dbPath = e2eDbPath();
  try {
    if (existsSync(dbPath)) {
      rmSync(dbPath, { force: true });
      console.log(`[e2e] BD temporal eliminada: ${dbPath}`);
    }
  } catch (err) {
    console.warn(`[e2e] No se pudo borrar la BD temporal: ${err}`);
  }
}
