// @ts-check
import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  integrations: [react()],
  vite: {
    plugins: [tailwindcss()],
    server: {
      host: "0.0.0.0",
      port: 3000,
      watch: {
        usePolling: true,
        interval: 1000,
      },
      proxy: {
        "/api": "http://localhost:8000",
      },
    },
  },
});
