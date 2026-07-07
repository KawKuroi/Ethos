import { ImageResponse } from "next/og";

// apple-touch-icon (180×180, fondo opaco: iOS no admite transparencia).

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
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
          fontSize: 112,
          fontWeight: 700,
        }}
      >
        E
      </div>
    ),
    size,
  );
}
