# Testing frontend — Vitest + React Testing Library + MSW (integración)

Guía de cómo testear el frontend ROCCA (Vite + React 18 + Redux Toolkit +
RTK Query). Hay **tres capas**, todas centralizadas en `tests/`:

| Capa | Herramienta | Corren en | Sufijo |
| --- | --- | --- | --- |
| **Integración** | Vitest + React Testing Library + MSW | Node (jsdom) | `*.test.tsx` |
| **Component (CT)** | Playwright Component Testing | Browser real (Edge/Chromium) | `*.ct.spec.tsx` |
| **E2E** | Playwright | Browser real (Edge/Chromium) | `*.spec.ts` |

> Stack integración: **Vitest 2.x** (compatible con Vite 5) · **React Testing
> Library** · **user-event** · **MSW 2.x** (server de Node) · **RTK Query real**
> (no se mockea Redux).

---

## 1. Qué es un test de integración (y por qué no unit-test de Redux)

Según la guía "Testing Redux: Integration Testing Connected Components and
Redux Logic", el valor está en montar el **componente conectado al store
real** y asertar sobre **comportamiento de usuario**, no sobre el estado
interno de Redux:

- ✅ `renderWithProviders(<Padron />)` → escribes en la búsqueda → la tabla se
  filtra en el DOM.
- ✅ El store es el **real** (reducer + cache de RTK Query reales), solo la
  **API** está mockeada (MSW).
- ❌ No testear el reducer en aislamiento: si un test unitario de `setBusqueda`
  pasa pero el componente no filtra, la feature está rota igual.

**Store fresco por test** (`setupStore()`): RTK Query cachea en el store; si
compartís el singleton entre tests, el cache de uno se filtra al siguiente.

---

## 2. Arquitectura

**Todos los tests viven en `tests/`** (ninguno en `src/`). La estructura
`tests/routes/...` refleja el árbol de `src/routes/...` para que sea fácil
encontrar el test de cada componente.

```
tests/
  setup.ts           → setupFiles de Vitest: jest-dom + MSW server + polyfills
  render.tsx         → renderWithProviders (Provider + store fresco [+ MemoryRouter])
  ct-utils.ts        → helpers de CT (mount + store fresco + rutas mockeadas)
  mocks/
    data.ts          → OPERADORES_MOCK, ACTIVIDADES_MOCK, crearOperadorMock()
    handlers.ts      → createHandlers(opts) — URLs RELATIVAS /api/... (factory, estado fresco)
    server.ts        → setupServer(...handlers) (MSW Node)
    browser.ts       → setupWorker(...)  (worker in-app para dev/E2E)
  playwright/
    index.tsx        → entry point de CT (beforeMount: Provider + worker.start)
  e2e/               → specs E2E de Playwright (*.spec.ts)
  routes/            → tests de integración (Vitest) + CT (Playwright), reflejando src/
    login.flow.test.tsx
    modulo-i/
      padron/
        PadronSucursales.integration.test.tsx
        PadronSucursales.ct.spec.tsx
        CartonF102.integration.test.tsx
        VerCarton.integration.test.tsx
      inscripcion/
        FormularioF102.integration.test.tsx
        FormularioF102.ct.spec.tsx
        PaginaRegistroOperadores.integration.test.tsx
        Minimo.ct.spec.tsx

vitest.config.ts          → environment jsdom, globals, setupFiles, include *.test.{ts,tsx}
playwright-ct.config.ts   → CT: testDir ./tests, testMatch **/*.ct.spec.tsx
playwright.config.ts      → E2E: testDir ./tests/e2e, testMatch *.spec.ts
```

- **`renderWithProviders`** (tests/render.tsx): crea `setupStore(preloadedState)`,
  envuelve en `<Provider>` (y `<MemoryRouter>` si `withRouter`), y devuelve
  `{ store, user, ...rtl }` para dispatchear/inspeccionar después.
- **`createHandlers()`** (tests/mocks/handlers.ts): factory con estado propio.
  Opciones: `operadores`, `unauthenticated`, `loginResponse`, `duplicarAlta`,
  `delayMs`. URLs **relativas** (`/api/...`) porque RTK Query usa
  `baseUrl: "/api"` y en jsdom el fetch es relativo a `http://localhost`.
- **`ct-utils.ts`** (tests/ct-utils.ts): extiende el fixture `mount` de
  `@playwright/experimental-ct-react` para devolver el store fresco creado en
  `beforeMount` (interfaz `WithStore`), y exporta helpers como `mockRoccaApi`.
  La configuración global (Provider + rutas mockeadas) vive en
  `tests/playwright/index.tsx` (`beforeMount`).

> Los tres sufijos no se pisan: Vitest solo matchea `*.test.{ts,tsx}`
> (la config `include`), así que los `*.ct.spec.tsx` y `*.spec.ts` de
> Playwright no entran en la suite de Vitest.

---

## 3. Correr los tests

```bash
cd src/frontend
npm test                        # vitest run (integración, jsdom)
npm run test:watch              # vitest en modo watch
npx vitest run tests/routes/login.flow.test.tsx   # un archivo

npm run test:e2e                # playwright test (E2E, browser real)
npm run test:e2e:ui             # E2E en modo UI
npx playwright test -c playwright-ct.config.ts    # CT (browser real)
npx playwright test -c playwright-ct.config.ts --list   # solo listar specs CT
```

- **Integración** (Vitest): no requiere navegador ni backend.
- **CT y E2E** (Playwright): requieren un browser. El config de CT usa el
  Edge instalado por defecto (`executablePath`); sobreescribir con
  `CHROMIUM_EXECUTABLE_PATH` para usar otro.

---

## 4. Ejemplo: probar un flujo con la API mockeada (integración)

```tsx
import { describe, it, expect, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../../render";
import { server } from "../../../mocks/server";
import { createHandlers } from "../../../mocks/handlers";
import { PadronSucursales } from "../../../../src/routes/modulo-i/padron/PadronSucursales";

describe("Integración · Padrón", () => {
  beforeEach(() => server.resetHandlers(...createHandlers()));

  it("filtra al escribir en la búsqueda", async () => {
    const { user, store } = renderWithProviders(<PadronSucursales />);
    await waitFor(() =>
      expect(screen.getAllByText("CARNICERÍA LA NORITA").length).toBeGreaterThan(0),
    );

    await user.type(screen.getByPlaceholderText(/Buscar por N° Cartón/i), "NORITA");
    await waitFor(() =>
      expect(screen.getByText(/establecimientos registrados/i)).toHaveTextContent("1"),
    );
  });
});
```

Overrides por test con `server.use(...)`:

```tsx
import { http, HttpResponse } from "msw";

server.use(
  http.get("/api/registro-operadores", () =>
    HttpResponse.json({ detail: "Boom" }, { status: 500 }),
  ),
);
```

> Nota: `razon_social` se renderiza dos veces por fila (columnas
> "Establecimiento" y "Persona Titular"), así que para ese texto usá
> `getAllByText` (o `within(...)` para acotar el alcance).

---

## 5. Ejemplo: test de componente (CT, browser real)

Los specs CT usan el fixture `mount` extendido por `ct-utils.ts` (Provider +
store fresco + rutas mockeadas con `page.route`). El entry point global es
`tests/playwright/index.tsx` (`beforeMount`). Se importa `test`/`expect` de
`@playwright/experimental-ct-react` y el tipo `HooksConfig` de `tests/playwright`.

```tsx
import { test, expect } from "@playwright/experimental-ct-react";
import type { HooksConfig } from "../../../playwright";
import { PadronSucursales } from "../../../../src/routes/modulo-i/padron/PadronSucursales";

test("renderiza los operadores mockeados", async ({ mount }) => {
  const component = await mount<HooksConfig>(<PadronSucursales />);
  await expect(component.getByText("CARNICERÍA LA NORITA")).toBeVisible();
});
```

---

## 6. Tips

- **No mockear Redux**: store real + `preloadedState` para sembrar slices.
- **Asertar sobre el UI** (`getByRole`, `getByText`, `toHaveTextContent`) —
  el estado de Redux se verifica como *efecto colateral* del comportamiento,
  o directamente contra `store.getState()` cuando sea el contrato relevante.
- **`onUnhandledRequest: "warn"`** (tests/setup.ts): la app dispara peticiones
  colaterales (logout del header, etc.); MSW las loguea sin tumbar el test.
  Si querés que fallemos fuerte, cambiá a `"error"`.
- **`userEvent.setup()`** por test (no `fireEvent`): simula eventos completos
  (click → change → blur) como un usuario real.
- **jsdom no soporta `{SelectAll}`** ni Backspace en cadena de forma fiable:
  para vaciar un input controlado usá `fireEvent.change(input, { value: "" })`.
- **`getByRole("status", { name })` no coincide en live regions**: consultá
  con `getByRole("status")` y asertá sobre `toHaveTextContent(...)`.
- **Stub de `URL`**: si necesitás mockear `URL.createObjectURL`, no usés
  `vi.stubGlobal("URL", {...})` (rompe el constructor que usa `new Request()`);
  extendé la clase (`class extends URL`) para conservar el constructor.
- **RTK Query**: `await waitFor(...)` sobre el DOM; no hacer `await` manual
  sobre la query (el auto-waiting de RTL lo cubre).

---

## Scripts

```bash
npm test                     # vitest run (integración, jsdom)
npm run test:watch           # vitest (watch)
npm run test:e2e             # playwright test (E2E, browser real)
npm run test:e2e:ui          # playwright test --ui
npx playwright test -c playwright-ct.config.ts   # CT (browser real)
```
