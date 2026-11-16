import { defineConfig, devices } from "@playwright/test";
import { e2eDbUrl } from "./tests/e2e/e2eDb";
import { BACKEND_DIR, uvicornCmd } from "./tests/e2e/backendPaths";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

/**
 * Lee el .env del repo (raíz) para INSFORGE_URL / INSFORGE_API_KEY y las
 * credenciales de E2E. Así el keybinding de neotest levanta TODO sin exportar
 * nada: el fixture inyecta estas vars en el backend que arranca solo.
 */
function leerEnvDeRepo(): Record<string, string> {
  const out: Record<string, string> = {};
  const rutas = [join(__dirname, "..", "..", ".env"), join(__dirname, ".env")];
  for (const p of rutas) {
    let contenido = "";
    try {
      contenido = readFileSync(p, "utf8");
    } catch {
      continue;
    }
    for (const linea of contenido.split("\n")) {
      const m = linea.match(
        /^\s*(INSFORGE_URL|INSFORGE_API_KEY|INSFORGE_BUCKET|ROCCA_E2E_EMAIL|ROCCA_E2E_PASSWORD)\s*=\s*(.*)\s*$/,
      );
      if (m) out[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  }
  return out;
}

const envRepo = leerEnvDeRepo();

/**
 * Playwright E2E — ROCCA (Control Cadena Cárnica SDE).
 *
 * Se corre contra el Vite dev server (puerto 5173), que proxy-kea `/api`
 * al backend FastAPI (uvicorn :8000). El `webServer` arranca AMBOS:
 *   1. Backend: uvicorn con un SQLite EFÍMERO y LIMPIO (lo crea
 *      `globalSetup`, `ROCCA_E2E_DB_URL`). InsForge sigue siendo el IdP real.
 *   2. Frontend: `pnpm dev` (Vite, proxy /api → :8000).
 * Así el keybinding de neotest (<leader>tr) levanta todo solo: no hay que
 * arrancar backend ni frontend a mano, ni exportar variables.
 *
 * Uso:
 *   npx playwright install chromium   # primera vez (browsers)
 *   npx playwright test               # suite completa (levanta todo solo)
 *   npx playwright test --ui          # modo interactivo
 *   npx playwright show-report        # reporte HTML tras correr
 *
 * Pre-requisito: cuenta de prueba en InsForge (ROCCA_E2E_EMAIL/PASSWORD en
 * .env del repo o del frontend). Sin ellas, auth.setup.ts deja el
 * storageState vacío y los tests protegidos fallan con 401.
 */
export default defineConfig({
  globalSetup: "./tests/e2e/globalSetup.ts",
  globalTeardown: "./tests/e2e/globalSetup.ts",
  testDir: "./tests/e2e",
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  testMatch: /.*\.spec\.ts/,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "retain-on-failure",
    // Pantalla al FINAL de cada test (pasa y falla).
    screenshot: "on",
    // Sesión compartida: auth.setup.ts loguea y guarda la cookie HttpOnly
    // en este storageState; todos los tests la reutilizan (la API exige
    // autenticación vía middleware de InsForge).
    storageState: "tests/e2e/.auth/user.json",
  },
  // auth.setup.ts (project `setup`) se corre PRIMERO: loguea con
  // ROCCA_E2E_EMAIL / ROCCA_E2E_PASSWORD y escribe el storageState que usa el
  // resto de la suite. El archivo debe existir ({} si no hay credenciales),
  // por eso tests/e2e/.auth/user.json está commitado.
  projects: [
    {
      // Login de prueba: corre solo una vez, antes del resto de la suite.
      name: "setup",
      testMatch: /auth\.setup\.ts$/,
    },
    {
      name: "chromium",
      // Espera a que `setup` termine (y escriba el storageState) antes de
      // correr cualquier test. Sin esto, los tests arrancan en paralelo con
      // el login y leen un storageState vacío → redirección a /login.
      dependencies: ["setup"],
      testIgnore: /auth\.setup\.ts$/,
      use: {
        ...devices["Desktop Chrome"],
        // El headless shell del sandbox está incompleto (sin ICU: icudtl.dat
        // no found) y la cache de browsers (~/Library/Caches/ms-playwright)
        // no es legible desde el sandbox. Se usa el Edge instalado vía
        // `channel` (resuelve la app por nombre, sin leer la cache).
        // IMPORTANTE: cerrá Edge antes de correr (el profile queda bloqueado
        // por ProcessSingleton si hay una instancia abierta).
        channel: "msedge",
      },
    },
  ],
  // Dos webServers: el backend (SQLite efímero) y el frontend (Vite).
  // `globalSetup` crea la BD temporal y fija ROCCA_E2E_DB_URL; acá la
  // pasamos al backend. `reuseExistingServer: false` en el backend para
  // garantizar que cada corrida use la BD limpia de esta ejecución (no una
  // instancia vieja con datos residuales). El frontend sí reusa el que
  // ya esté corriendo para no matar un `pnpm dev` del desarrollo.
  webServer: [
    {
      // uvicornCmd() resuelve el Python del venv según el SO
      // (.venv/bin/python en unix, .venv/Scripts/python.exe en Windows).
      command: uvicornCmd(),
      cwd: BACKEND_DIR,
      env: {
        ...process.env,
        // BD temporal limpia (mismo path que crea `globalSetup` vía e2eDb.ts).
        ROCCA_DATABASE_URL: e2eDbUrl(),
        // InsForge real (IdP): URL + clave desde el .env del repo.
        INSFORGE_URL: envRepo.INSFORGE_URL,
        INSFORGE_API_KEY: envRepo.INSFORGE_API_KEY,
        INSFORGE_BUCKET: envRepo.INSFORGE_BUCKET,
      },
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: "pnpm dev",
      url: "http://localhost:5173",
      reuseExistingServer: true,
      timeout: 60_000,
    },
  ],
});

// El project `setup` (auth.setup.ts) loguea contra InsForge real y persiste
// el storageState que el project `chromium` reutiliza. `globalSetup` (arriba)
// es solo para la BD temporal; el auth lo maneja el project `setup`.
