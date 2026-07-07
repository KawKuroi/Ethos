import type { MetadataRoute } from "next";

// Manifest de la web app (habilita "Añadir a pantalla de inicio" en Android
// y da nombre/iconos/tema; Next lo sirve y enlaza automáticamente).
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Ethos",
    short_name: "Ethos",
    description:
      "Reúne tu gusto de las apps donde ya vive, lo normaliza y lo entrega dos veces: como panel para ti y como contexto para tu IA (archivos o servidor MCP).",
    start_url: "/",
    display: "standalone",
    background_color: "#141619",
    theme_color: "#141619",
    icons: [
      { src: "/icon.svg", sizes: "any", type: "image/svg+xml" },
      { src: "/favicon.ico", sizes: "48x48", type: "image/x-icon" },
    ],
  };
}
