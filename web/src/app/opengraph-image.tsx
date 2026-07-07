import { ImageResponse } from "next/og";
import { Logo } from "@/components/logo";

// Tarjeta OG (1200×630) generada en build con los tokens del diseño
// (paleta slate oscura y acentos por categoría de globals.css).

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

export default function OpengraphImage() {
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
          padding: "72px 80px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <Logo width={52} height={46} />
          <div
            style={{
              fontSize: 34,
              fontWeight: 700,
              letterSpacing: "0.18em",
            }}
          >
            ETHOS
          </div>
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 26,
            maxWidth: 980,
          }}
        >
          <div
            style={{
              fontSize: 76,
              fontWeight: 700,
              lineHeight: 1.08,
              letterSpacing: "-0.02em",
            }}
          >
            Tu gusto, en un panel para ti y como contexto para tu IA.
          </div>
          <div style={{ fontSize: 30, color: "#888d97", lineHeight: 1.35 }}>
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
          <div style={{ display: "flex", gap: 12 }}>
            {CATEGORY_ACCENTS.map((accent) => (
              <div
                key={accent}
                style={{
                  width: 16,
                  height: 16,
                  borderRadius: 8,
                  background: accent,
                }}
              />
            ))}
          </div>
          <div style={{ fontSize: 26, color: "#888d97" }}>
            ethos-steel.vercel.app
          </div>
        </div>
      </div>
    ),
    size,
  );
}
