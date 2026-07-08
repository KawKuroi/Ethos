import { ImageResponse } from "next/og";
import { Logo } from "@/components/logo";

// Favicon PNG 32×32 con el logo constelación (el SVG de icon.svg cubre el
// resto de tamaños). El logo va casi a sangre: a este tamaño, con margen
// los astros quedan en puntos ilegibles.

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
        }}
      >
        <Logo width={30} height={26} bold />
      </div>
    ),
    size,
  );
}
