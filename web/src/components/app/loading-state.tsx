import styles from "./loading-state.module.css";

// Estado de carga compartido por las vistas que traen datos del backend:
// spinner + esqueleto pulsante en vez del texto plano, para que las cargas
// largas se sientan vivas.
export function LoadingState({ label }: { label: string }) {
  return (
    <div className={styles.wrap} role="status" aria-live="polite">
      <div className={styles.head}>
        <span className={styles.spinner} />
        <span className={styles.label}>{label}</span>
      </div>
      <div className={styles.skeleton} aria-hidden="true">
        <span className={styles.bar} style={{ width: "38%" }} />
        <span className={styles.bar} style={{ width: "74%" }} />
        <span className={styles.bar} style={{ width: "56%" }} />
      </div>
    </div>
  );
}
