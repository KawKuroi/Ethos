import { ImageResponse } from "next/og";

// Favicon PNG 32×32 (nítido en pestañas; el SVG de icon.svg cubre el resto).

export const size = { width: 32, height: 32 };
export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#1b1e23",
          color: "#eef0f3",
          borderRadius: 7,
          fontSize: 21,
          fontWeight: 700,
        }}
      >
        E
      </div>
    ),
    size,
  );
}
