import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    // Expone afterEach global para el auto-cleanup de Testing Library.
    globals: true,
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.{ts,tsx}", "src/**/*.d.ts"],
      // Umbrales D59: bloquean regresiones. Medición real (todos los archivos
      // de src, 2026-07-06): 57,0% stmts · 63,5% branches · 55,4% funcs ·
      // 59,7% lines; el gate queda ~3-4 puntos por debajo.
      thresholds: {
        statements: 53,
        branches: 60,
        functions: 52,
        lines: 56,
      },
    },
  },
});
