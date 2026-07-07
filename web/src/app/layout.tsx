import type { Metadata, Viewport } from "next";
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

const SITE_URL = "https://ethos-steel.vercel.app";

const DESCRIPTION =
  "Reúne tu gusto de las apps donde ya vive, lo normaliza y lo entrega dos veces: como panel para ti y como contexto para tu IA (archivos o servidor MCP).";

// Título descriptivo para buscadores/compartir en la landing; cada pantalla
// interna pone el suyo ("Inicio", "Fuentes", …) y la plantilla añade la marca.
const TITLE = "Ethos — Tu gusto en un panel para ti y contexto para tu IA";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: TITLE,
    template: "%s · Ethos",
  },
  description: DESCRIPTION,
  // "./" se compone con la ruta actual: cada página obtiene su propia
  // canónica (y og:url) en vez de heredar la de la raíz.
  alternates: { canonical: "./" },
  openGraph: {
    type: "website",
    url: "./",
    siteName: "Ethos",
    locale: "es_ES",
    title: TITLE,
    description: DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

// theme-color acorde al tema del sistema (tokens --paper de globals.css).
export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#eff1f3" },
    { media: "(prefers-color-scheme: dark)", color: "#141619" },
  ],
};

// Datos estructurados para buscadores (JSON-LD).
const JSON_LD = {
  "@context": "https://schema.org",
  "@type": "WebApplication",
  name: "Ethos",
  url: SITE_URL,
  description: DESCRIPTION,
  applicationCategory: "LifestyleApplication",
  operatingSystem: "Web",
  inLanguage: "es",
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
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(JSON_LD) }}
        />
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
