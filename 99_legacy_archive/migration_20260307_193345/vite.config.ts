<<<<<<< HEAD:vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
=======
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig(({ mode }) => {
  // Load env vars from .env files
  const env = loadEnv(mode, process.cwd(), "");

  const pagesBase = env.PAGES_BASE || "/";
  const pagesDeploy = env.PAGES_DEPLOY === "true";

  return {
    base: pagesBase,

    define: {
      "import.meta.env.PAGES_DEPLOY": JSON.stringify(pagesDeploy),
    },

    plugins: [react()],

    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },

    server: {
      port: 5173,
      strictPort: true,
    },

    preview: {
      port: 5173,
      strictPort: true,
    },
  };
});
>>>>>>> fix/desktop-bridge:99_legacy_archive/migration_20260307_193345/vite.config.ts
