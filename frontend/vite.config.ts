import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, proxy /api to the backend. In the container, nginx handles /api.
export default defineConfig({
  // Served at root standalone; under "/coding/" inside the unified Nous RCM Studio gateway.
  base: process.env.VITE_BASE_PATH || "/",
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
  build: { outDir: "dist" },
});
