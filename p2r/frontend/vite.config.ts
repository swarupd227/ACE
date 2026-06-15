import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, proxy /api to the P2R backend (:8100) and strip the /api prefix
// (P2R routes live at root). In the container, nginx does the same.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5174,
    proxy: {
      "/api": {
        target: "http://localhost:8100",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
  build: { outDir: "dist" },
});
