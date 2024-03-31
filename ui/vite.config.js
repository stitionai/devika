import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import wasm from "vite-plugin-wasm";

export default defineConfig({
  plugins: [sveltekit(), wasm()],
  server: {
    port: 3000,
  },
});
