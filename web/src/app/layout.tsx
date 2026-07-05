import type { Metadata } from "next";
import {
  Bricolage_Grotesque,
  Hanken_Grotesk,
  JetBrains_Mono,
} from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import "./globals.css";

// Tipografías fijas del diseño (design.md §1): display, texto/UI y código.
// Bricolage necesita el eje óptico (opsz 12..96) que el prototipo carga:
// sin él, los titulares grandes no se ven como el diseño.
const display = Bricolage_Grotesque({
  variable: "--font-display",
  subsets: ["latin"],
  axes: ["opsz"],
});

const body = Hanken_Grotesk({
  variable: "--font-body",
  subsets: ["latin"],
});

const code = JetBrains_Mono({
  variable: "--font-code",
  subsets: ["latin"],
});

// Título corto por pestaña: la landing es "Ethos" y cada pantalla pone el
// suyo ("Inicio", "Fuentes", …) con su propio metadata.
export const metadata: Metadata = {
  title: "Ethos",
  description:
    "Reúne tu gusto de las apps donde ya vive, lo normaliza y lo entrega dos veces: como panel para ti y como contexto para tu IA (archivos o servidor MCP).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // suppressHydrationWarning: next-themes escribe data-theme en <html> antes
  // de la hidratación (patrón estándar del paquete).
  // Las variables de fuente van en <html>: los alias --fd/--fb/--code de
  // globals.css se resuelven en :root, así que --font-* debe existir ahí.
  return (
    <html
      lang="es"
      suppressHydrationWarning
      className={`${display.variable} ${body.variable} ${code.variable}`}
    >
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
