import { defineConfig } from 'vite';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  resolve: {
    alias: {
      // Use browser-safe UnoCSS exports to avoid Node-only deps during build.
      unocss: fileURLToPath(new URL('./src/unocss-browser.ts', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
  },
  build: {
    outDir: 'dist',
  },
});
