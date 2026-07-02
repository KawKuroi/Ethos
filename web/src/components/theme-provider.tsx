"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ReactNode } from "react";

// Tema claro / oscuro / sistema, persistido en el dispositivo (design.md §5).
// La clave de almacenamiento es la del prototipo: ethos_theme_mode.
export function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <NextThemesProvider
      attribute="data-theme"
      defaultTheme="system"
      enableSystem
      storageKey="ethos_theme_mode"
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}
