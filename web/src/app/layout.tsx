import type { Metadata } from "next";
import { Bricolage_Grotesque, Hanken_Grotesk } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import "./globals.css";

// Tipografías fijas del diseño (design.md §1): display y texto/UI.
const display = Bricolage_Grotesque({
  variable: "--font-display",
  subsets: ["latin"],
});

const body = Hanken_Grotesk({
  variable: "--font-body",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Ethos — Tu gusto, hecho contexto",
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
  return (
    <html lang="es" suppressHydrationWarning>
      <body className={`${display.variable} ${body.variable}`}>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
