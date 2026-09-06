import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  server: { proxy: {
    "/api/catalog": "http://localhost:8001", "/api/governance": "http://localhost:8002",
    "/api/lineage": "http://localhost:8003", "/api/pipeline": "http://localhost:8004",
    "/api/recon": "http://localhost:8005"
  } }
});