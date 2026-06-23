import { defineConfig } from 'vite';

export default defineConfig({
  base: './',
  server: { port: 5173 },
  build: { sourcemap: false, target: 'es2022' },
  test: { environment: 'node', globals: true },
});
