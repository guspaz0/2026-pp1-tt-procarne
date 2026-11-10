import React from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import App from "./App";
import { store } from "./store/store";
import "./rocca.css";

// Arranque condicional del worker de MSW (mocks de /api/registro-operadores).
// Se activa de dos formas, ambas opt-in para no interferir con el flujo
// real contra el backend:
//   - Query string `?mocks=1`  →  http://localhost:5173/?mocks=1
//   - Env de build  VITE_ENABLE_MSW=1
async function maybeStartMsw() {
  const wantsMocks =
    window.location.search.includes("mocks=1") ||
    import.meta.env.VITE_ENABLE_MSW === "1";
  if (!wantsMocks) return;
  const { browserWorker } = await import("../tests/mocks/browser");
  await browserWorker.start({
    // "bypass" (default): lo que no tiene handler sigue al backend real.
    onUnhandledFrame: "bypass",
    quiet: true,
  });
  // Expone el worker para que los tests de E2E hagan overrides por test vía
  // `page.evaluate`: window.__mswWorker.use(...) / resetHandlers().
  (window as unknown as { __mswWorker: unknown }).__mswWorker = browserWorker;
}

maybeStartMsw().then(() => {
  createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <Provider store={store}>
        <App />
      </Provider>
    </React.StrictMode>,
  );
});
