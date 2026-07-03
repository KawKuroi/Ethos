import styles from "./app.module.css";

// Placeholder de pantalla dentro del shell: cada pantalla real llega en su
// propia tarea del roadmap. Entra con el deslizamiento `eth-screen`.
export function ScreenPlaceholder({ name }: { name: string }) {
  return (
    <div className={`eth-screen ${styles.placeholder}`}>
      <h2 className={styles.placeholderTitle}>{name} en construcción</h2>
      <p className={styles.placeholderText}>
        Estamos construyendo esta pantalla sobre el diseño final. El armazón ya
        está listo; el contenido llega pronto.
      </p>
    </div>
  );
}
