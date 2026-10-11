import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// El build se emite en dist/ con assets bajo dist/static/,
// que el backend Python monta en /static.
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: {
    outDir: "dist",
    assetsDir: "static",
  },
  server: {
    // En dev, Vite proxy-kea la API al backend Python (uvicorn en :8000).
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
