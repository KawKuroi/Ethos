import styles from "./auth.module.css";

const PERKS = [
  "Un perfil, todas tus fuentes",
  "Contexto normalizado y listo",
  "Privado por defecto",
];

// Constelación decorativa (tres estrellas + punto), reutilizada de los sparks.
function Spark({ className }: { className: string }) {
  return (
    <span className={className} aria-hidden="true">
      <svg width="110" height="99" viewBox="0 0 34 30">
        <path
          d="M5 18 C3.5 14 8 12 11 14 C14 16 12 20 8.5 20 C7 20 6 19.5 5 18 Z"
          fill="currentColor"
        />
        <path
          d="M21 7 C20 4 25 3 26 6 C27 9 23 10 22 8.5 C21.5 8 21.2 7.6 21 7 Z"
          fill="currentColor"
        />
        <path
          d="M25 22 C24 19.5 28 18.5 29 21 C29.6 22.6 27 24 25.7 23 C25.3 22.7 25.1 22.4 25 22 Z"
          fill="currentColor"
        />
        <circle cx="14" cy="25" r="2" fill="currentColor" />
      </svg>
    </span>
  );
}

// Panel de marca del layout de auth (fijo, estático). Diseño: Auth Ethos.dc.html.
export function BrandPanel() {
  return (
    <div className={styles.brand}>
      <Spark className={`${styles.spark} ${styles.spark1}`} />
      <Spark className={`${styles.spark} ${styles.spark2}`} />
      <Spark className={`${styles.spark} ${styles.spark3}`} />

      <div className={styles.wordmark}>
        <svg width="38" height="34" viewBox="0 0 34 30" style={{ display: "block" }}>
          <path
            d="M8 17 L22 7.5 L26.5 21 L14.5 24.5"
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            strokeLinecap="round"
            strokeDasharray="0.5 2.6"
            opacity=".7"
          />
          <path
            d="M5 18 C3.5 14 8 12 11 14 C14 16 12 20 8.5 20 C7 20 6 19.5 5 18 Z"
            fill="currentColor"
          />
          <path
            d="M21 7 C20 4 25 3 26 6 C27 9 23 10 22 8.5 C21.5 8 21.2 7.6 21 7 Z"
            fill="currentColor"
          />
          <path
            d="M25 22 C24 19.5 28 18.5 29 21 C29.6 22.6 27 24 25.7 23 C25.3 22.7 25.1 22.4 25 22 Z"
            fill="currentColor"
          />
          <circle cx="14" cy="25" r="2" fill="currentColor" />
        </svg>
        <span className={styles.wordmarkText}>Ethos</span>
      </div>

      <div className={styles.narrative}>
        <div className={styles.eyebrow}>Tu gusto, tu contexto</div>
        <h1 className={styles.brandTitle}>
          Tu gusto,
          <br />
          hecho contexto.
        </h1>
        <p className={styles.brandLede}>
          Ethos reúne lo que juegas, escuchas, ves y lees — lo normaliza en un
          perfil vivo y se lo entrega a tu IA cuando lo necesita.
        </p>

        <div className={styles.perks}>
          {PERKS.map((perk) => (
            <div key={perk} className={styles.perk}>
              <span className={styles.perkDot}>
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="3"
                >
                  <path
                    d="M5 12.5l4.2 4.2L19 6.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <span className={styles.perkText}>{perk}</span>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.brandFoot}>
        Perfil privado · tú decides qué se comparte
      </div>
    </div>
  );
}
