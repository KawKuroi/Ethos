// Placeholder mínimo sobre los tokens del diseño. La landing real (design.md
// §4) lo sustituye en su propia tarea.
export default function Home() {
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
      }}
    >
      <h1
        style={{
          fontFamily: "var(--fd)",
          fontWeight: "var(--dw)" as never,
          letterSpacing: "var(--dls)",
          fontSize: "42px",
          margin: 0,
        }}
      >
        Ethos
      </h1>
      <p
        style={{
          fontFamily: "var(--fb)",
          color: "var(--muted)",
          fontSize: "15px",
          margin: 0,
          textAlign: "center",
        }}
      >
        Tu gusto, hecho contexto. La interfaz se está construyendo sobre el
        diseño final.
      </p>
    </main>
  );
}
