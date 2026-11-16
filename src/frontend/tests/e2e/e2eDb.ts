/**
 * Path de la BD temporal E2E — compartido por `globalSetup` (lo crea) y
 * `playwright.config.ts` (se lo pasa al backend).
 *
 * El truco: el path se deriva de un valor que ambas partes pueden calcular
 * INDEPENDIENTEMENTE sin comunicación entre ellas. Playwright evalúa
 * `playwright.config.ts` ANTES de correr `globalSetup`, así que la config no
 * puede leer `process.env.ROCCA_E2E_DB_URL` (aún no existe). En cambio, si
 * ambas usan la MISMA fórmula (timestamp de arranque del proceso de Playwright
 * + pid), coinciden sin pasarse nada.
 *
 * En la práctica, el proceso de `playwright test` es único por corrida, así
 * que `process.pid` + un stamp compartido da un path estable para toda la
 * corrida: globalSetup lo crea, el webServer lo usa, globalTeardown lo borra.
 *
 * Cross-platform:
 *   - Linux/macOS: /tmp/rocca-e2e-<stamp>.db
 *   - Windows:     %TEMP%\rocca-e2e-<stamp>.db
 * SQLAlchemy SQLite URL: usa siempre barras invertidas en el path para que
 * funcione en los tres SO (los backslash de Windows rompan el esquema si se
 * usan tal cual, `sqlite:///C:\Users\...` → SQLAlchemy lee `\U` como escape).
 */
import { tmpdir } from "node:os";
import { join } from "node:path";

// Se calcula UNA vez al importar el módulo (mismo resultado en config y en
// globalSetup porque es el mismo proceso). El pid del proceso de Playwright
// es estable durante toda la corrida.
const STAMP = `${process.pid}-${Date.now()}`;

export function e2eDbPath(): string {
  return join(tmpdir(), `rocca-e2e-${STAMP}.db`);
}

/**
 * URL de SQLAlchemy para el SQLite temporal. Convierte los separadores del
 * path a `/` para que la URL sea válida en los tres SO (los backslash de
 * Windows se interpretan como secuencias de escape dentro del esquema).
 */
export function e2eDbUrl(): string {
  const path = e2eDbPath().split("\\").join("/");
  return `sqlite:///${path}`;
}
