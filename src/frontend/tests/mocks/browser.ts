/**
 * MSW (Mock Service Worker) — configuración del worker para Component Testing.
 *
 * El service worker se sirve desde `public/mockServiceWorker.js` (generado con
 * `npx msw init public/`). Los handlers viven en `tests/mocks/handlers.ts`
 * para poder importarlos desde los specs.
 */
import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

/** Worker MSW para el browser (Component Testing). */
export const browserWorker = setupWorker(...handlers);
