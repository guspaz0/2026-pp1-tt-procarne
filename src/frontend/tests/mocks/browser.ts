/**
 * Worker de MSW para el navegador (dev).
 *
 * Se genera con `npx msw init public/ --save`. El archivo resultante
 * (`public/mockServiceWorker.js`) queda servido por Vite en
 * `/mockServiceWorker.js` y es el que intercepta las peticiones del app.
 *
 * El worker se arranca de forma condicional en `main.tsx` solo cuando la
 * query string trae `?mocks=1` (o cuando `VITE_ENABLE_MSW === '1'`), para
 * no romper el flujo normal contra el backend real.
 *
 * NOTA: el archivo `mockServiceWorker.js` se genera una sola vez con:
 *   npx msw init public/ --save
 * y debe checkearse en git.
 */
import { setupWorker } from "msw/browser";
import { operadoresHandlers } from "./handlers";

export const browserWorker = setupWorker(...operadoresHandlers);
