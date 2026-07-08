// Logo constelación de Ethos (SVG del prototipo). Hereda el color del texto.
type LogoProps = {
  width?: number;
  height?: number;
  withPath?: boolean;
  // Trazo más grueso y puntos más densos: para tamaños pequeños (avatares,
  // favicons), donde el punteado fino desaparece.
  bold?: boolean;
};

export function Logo({
  width = 34,
  height = 30,
  withPath = true,
  bold = false,
}: LogoProps) {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 34 30"
      aria-hidden="true"
      style={{ display: "block" }}
    >
      {withPath && (
        // Trazo más grueso y opaco que el prototipo: a petición del usuario,
        // las líneas se perdían sobre algunos fondos.
        <path
          d="M8 17 L22 7.5 L26.5 21 L14.5 24.5"
          fill="none"
          stroke="currentColor"
          strokeWidth={bold ? 2.2 : 1.5}
          strokeLinecap="round"
          strokeDasharray={bold ? "0.9 2.6" : "0.6 2.4"}
          opacity=".95"
        />
      )}
      <path
        d="M5 18 C3.5 14 8 12 11 14 C14 16 12 20 8.5 20 C7 20 6 19.5 5 18 Z"
        fill="currentColor"
      />
      <path
        d="M21 7 C20 4 25 3 26 6 C27 9 23 10 22 8.5 C21.5 8 21.2 7.6 21 7 Z"
        fill="currentColor"
      />
      <path
        d="M25 22 C24 19.5 28 18.5 29 21 C29.6 22.6 27 24 25.7 23 C25.3 22.7 25.1 22.4 25 22 Z"
        fill="currentColor"
      />
      <circle cx="14" cy="25" r="2" fill="currentColor" />
    </svg>
  );
}
