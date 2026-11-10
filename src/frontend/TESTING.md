# Testing frontend — Playwright + MSW + React + RTK Query

Guía de cómo testear el frontend ROCCA (Vite + React 18 + Redux Toolkit + RTK Query)
con dos capas de Playwright, ambas compartiendo un mismo set de handlers de MSW.

> Stack: **Vite** · **RTK Query** (no plain thunks) · MSW 3.x.

Hay **dos capas** que usan MSW de forma distinta:

| Capa | Paquete | Qué monta | MSW responde vía |
|---|---|---|---|
| **Component tests (CT)** | `@playwright/experimental-ct-react` | Un componente React + un store Redux real, en un browser real | Service worker (in-app) |
| **E2E** | `@playwright/test` | La app completa | Service worker (`?mocks=1`) **o** `@msw/playwright` (nivel Playwright) |

Ambas comparten `src/mocks/handlers.ts`.

---

## 1. Instalación (en tu máquina — el sandbox bloquea el npm registry)

```bash
cd src/frontend
npm i -D @playwright/test @playwright/experimental-ct-react msw @msw/playwright
npx playwright install chromium
npx msw init public/ --save     # genera public/mockServiceWorker.js (ya existe en el repo)
```

`msw` ya está en `devDependencies`; el resto hay que instalarlo.

---

## 2. Handlers compartidos (ya existen)

```
src/mocks/
  data.ts        → OPERADORES_MOCK (7 establecimientos, 4 personas por CUIT)
  handlers.ts    → createHandlers(db?)  ·  GET/POST /api/registro-operadores
  browser.ts     → setupWorker(...)  (browser worker)
  server.ts      → setupServer(...)  (Node)
```

`createHandlers()` es una factory: cada llamada devuelve un array fresco,
así el estado del mock no se filtra entre tests. El POST muta el `db` pasado
y devuelve **409** si CUIT+razón ya existen (imita al backend real).

---

## 3. Store inyectable (ya existe)

`src/store/store.ts` exporta `setupStore(preloadedState?)` además del
singleton `store`. En tests usamos `setupStore()` para obtener una
**instancia fresca por test**, evitando que el cache de RTK Query de un test
se filtre al siguiente.

```ts
import { setupStore } from "../store/store";

const store = setupStore({
  // preloadedState opcional para sembrar slices (p. ej. formF102)
});
```

> **No mockear Redux.** El valor está en usar el reducer + el cache RTK Query
> reales contra respuestas mockeadas.

---

## 4. E2E — dos opciones

### Opción A: worker in-app (`?mocks=1`) — ya funciona

El worker se arranca en `src/main.tsx` cuando la query trae `mocks=1`
(o `VITE_ENABLE_MSW=1`). MSW hace *bypass* de lo que no tiene handler.

```bash
# Manual
npx vite            # abrir http://localhost:5173/?mocks=1

# Tests (tests/e2e/mocks.spec.ts)
npx playwright test tests/e2e/mocks.spec.ts
```

- Pros: reutiliza los mismos mocks para desarrollo manual.
- Contras: el código de MSW va en el bundle de dev; los overrides por test
  son más engorrosos.

### Opción B: `@msw/playwright` (nivel Playwright) — overrides por test

Intercepta a nivel de Playwright: **no** necesita service worker ni código de
MSW en la app. Es la opción limpia para overrides por test (error 500, vacío, etc.).

```ts
// tests/e2e/fixtures.ts  (descomentar tras instalar @msw/playwright)
import { test as base, expect } from "@playwright/test";
import { createNetworkFixture, type NetworkFixture } from "@msw/playwright";
import { operadoresHandlers } from "../../src/mocks/handlers";

export const test = base.extend<{ network: NetworkFixture }>({
  network: createNetworkFixture({ initialHandlers: operadoresHandlers }),
});
export { expect };
```

```ts
// tests/e2e/operadores.msw.spec.ts
import { http, HttpResponse } from "msw";
import { test, expect } from "./fixtures";

test("muestra el padrón", async ({ page }) => {
  await page.goto("/operadores/padron");
  await expect(page.getByText("CARNICERÍA LA NORITA")).toBeVisible();
});

test("muestra error cuando la API falla", async ({ page, network }) => {
  network.use(
    http.get("/api/registro-operadores", () =>
      new HttpResponse(null, { status: 500 }),
    ),
  );
  await page.goto("/operadores/padron");
  // asertar el estado de error de RTK Query en el UI
});
```

---

## 5. Component tests (CT)

Monta un componente con un store fresco y MSW (SW) respondiendo. Ideal para el
happy path con handlers fijos y para variar estado vía `preloadedState`.

```
playwright-ct.config.ts      → config CT (testMatch **/*.ct.spec.tsx)
playwright/index.tsx          → beforeMount: worker.start + setupStore
src/routes/modulo-i/padron/PadronSucursales.ct.spec.tsx  → ejemplo
```

```bash
npx playwright test -c playwright-ct.config.ts
```

**Límite:** el archivo de test corre en Node y el componente en el browser, así
que no podés pasar `server.use(...)` desde el test al worker. Para respuestas
de error/vacío por test, usá E2E (Opción B). Si `mockServiceWorker.js` da 404
en CT, poné `ctViteConfig: { publicDir: "public" }` en la config.

---

## 6. Tips

- **`onUnhandledRequest: "error"`** en MSW: un handler olvidado falla fuerte
  en vez de tocar el backend real.
- **Store fresco por test**: con RTK Query, un store compartido filtra el
  cache de un test al siguiente.
- **Asertar sobre el UI** (`getByRole`, `getByText`) y dejar que Playwright
  auto-wait — no esperar a llamadas de red.
- **Paths relativos en handlers**: `/api/registro-operadores` coincide con el
  origin de la página en el browser, así que sirve tanto en CT como en E2E.
- **No mockear Redux**: preloaded state + reducers reales son lo que hace
  valiosos estos tests.

---

## Scripts

```bash
npm run test:e2e          # playwright test (tests/e2e)
npm run test:e2e:ui       # modo interactivo
npm run test:e2e:report   # abre el reporte HTML
```
