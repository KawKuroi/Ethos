import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ImageResponse } from "next/og";
import { Logo } from "@/components/logo";

// Tarjeta OG (1200×630) generada en build con los tokens del diseño y las
// tipografías reales de la web (Bricolage Grotesque + Hanken Grotesk).
// Las TTF viven en web/assets/og: instancias estáticas con subset latino
// generadas desde las fuentes variables de Google Fonts.

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt =
  "Ethos — Tu gusto en un panel para ti y contexto para tu IA";

const CATEGORY_ACCENTS = [
  "#3b82c4",
  "#d8543f",
  "#8b5cf6",
  "#e0883c",
  "#c64b78",
  "#2f9e6b",
  "#6f8f3f",
  "#b07b3e",
  "#3f8f8f",
];

function font(file: string): Promise<Buffer> {
  return readFile(join(process.cwd(), "assets", "og", file));
}

export default async function OpengraphImage() {
  const [bricolage, hanken, hankenSemi] = await Promise.all([
    font("bricolage-700.ttf"),
    font("hanken-400.ttf"),
    font("hanken-600.ttf"),
  ]);

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#141619",
          color: "#eef0f3",
          padding: "64px 80px 60px",
          fontFamily: "Hanken Grotesk",
          position: "relative",
        }}
      >
        {/* Marca de agua: la constelación grande, apenas visible */}
        <div
          style={{
            position: "absolute",
            right: -60,
            top: 96,
            opacity: 0.08,
            display: "flex",
          }}
        >
          <Logo width={560} height={494} bold />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <Logo width={58} height={51} bold />
          <div
            style={{
              fontFamily: "Bricolage Grotesque",
              fontSize: 44,
              fontWeight: 700,
              letterSpacing: "-0.02em",
            }}
          >
            Ethos
          </div>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 28,
            maxWidth: 920,
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              fontFamily: "Bricolage Grotesque",
              fontSize: 76,
              fontWeight: 700,
              lineHeight: 1.08,
              letterSpacing: "-0.03em",
            }}
          >
            {/* Cortes fijos: satori dejaba "IA." huérfano al envolver solo. */}
            <div>Tu gusto, en un panel para ti</div>
            <div>y como contexto para tu IA.</div>
          </div>
          <div
            style={{
              fontSize: 31,
              fontWeight: 400,
              color: "#9aa0aa",
              lineHeight: 1.4,
              maxWidth: 840,
            }}
          >
            Lo reunimos de las apps donde ya vive, lo normalizamos y lo
            entregamos como archivos o servidor MCP.
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", gap: 13 }}>
            {CATEGORY_ACCENTS.map((accent) => (
              <div
                key={accent}
                style={{
                  width: 17,
                  height: 17,
                  borderRadius: 9,
                  background: accent,
                }}
              />
            ))}
          </div>
          <div style={{ fontSize: 26, fontWeight: 600, color: "#9aa0aa" }}>
            ethos-steel.vercel.app
          </div>
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [
        {
          name: "Bricolage Grotesque",
          data: bricolage,
          weight: 700,
          style: "normal",
        },
        { name: "Hanken Grotesk", data: hanken, weight: 400, style: "normal" },
        {
          name: "Hanken Grotesk",
          data: hankenSemi,
          weight: 600,
          style: "normal",
        },
      ],
    },
  );
}
