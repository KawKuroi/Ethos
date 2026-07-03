"use client";

import { useTheme } from "next-themes";
import { useSyncExternalStore } from "react";

const emptySubscribe = () => () => {};

// Alterna claro/oscuro con los iconos del prototipo. El modo "sistema" se
// gestiona en Ajustes de la app; la landing alterna directo, como el diseño.
export function ThemeToggle({ className }: { className?: string }) {
  const { resolvedTheme, setTheme } = useTheme();
  // El tema real solo se conoce en cliente (evita desajustes de hidratación).
  const mounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );
  const isDark = mounted && resolvedTheme === "dark";

  return (
    <button
      type="button"
      onClick={() => setTheme(isDark ? "light" : "dark")}
      title="Cambiar tema"
      aria-label="Cambiar tema"
      className={className}
    >
      {isDark ? (
        <svg
          width="17"
          height="17"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        >
          <circle cx="12" cy="12" r="4.4" />
          <path
            d="M12 2.4v2.2M12 19.4v2.2M4.6 4.6l1.5 1.5M17.9 17.9l1.5 1.5M2.4 12h2.2M19.4 12h2.2M4.6 19.4l1.5-1.5M17.9 6.1l1.5-1.5"
            strokeLinecap="round"
          />
        </svg>
      ) : (
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        >
          <path
            d="M20.5 14.8A8.2 8.2 0 0 1 9.2 3.5a7.2 7.2 0 1 0 11.3 11.3z"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </button>
  );
}
