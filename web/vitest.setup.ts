// Matchers de Testing Library (toBeInTheDocument, etc.) para Vitest.
import "@testing-library/jest-dom/vitest";

// jsdom no implementa matchMedia y next-themes lo necesita para el tema
// "sistema". Polyfill mínimo y estático para los tests.
if (typeof window !== "undefined" && !window.matchMedia) {
  const matchMediaStub = (query: string): MediaQueryList =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }) as MediaQueryList;
  window.matchMedia = matchMediaStub;
}
