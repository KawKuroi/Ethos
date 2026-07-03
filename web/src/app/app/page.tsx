import Link from "next/link";

// Placeholder de la app: la shell real (design.md §2) llega en su tarea.
export default function AppPlaceholder() {
  return (
    <main
      className="eth-screen"
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "14px",
        padding: "40px 24px",
        textAlign: "center",
      }}
    >
      <h1
        style={{
          fontFamily: "var(--fd)",
          fontWeight: 700,
          letterSpacing: "-.025em",
          fontSize: "34px",
          margin: 0,
        }}
      >
        La app está en construcción
      </h1>
      <p
        style={{
          fontFamily: "var(--fb)",
          color: "var(--muted)",
          fontSize: "15px",
          margin: 0,
          maxWidth: "420px",
          lineHeight: 1.6,
        }}
      >
        Estamos construyendo el panel sobre el diseño final. Mientras tanto, la
        landing cuenta lo que viene.
      </p>
      <Link
        href="/"
        style={{
          fontFamily: "var(--fb)",
          fontWeight: 700,
          fontSize: "14px",
          color: "var(--accent)",
        }}
      >
        ← Volver a la landing
      </Link>
    </main>
  );
}
