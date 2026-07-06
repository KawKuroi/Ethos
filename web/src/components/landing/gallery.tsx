import type { CSSProperties } from "react";

import { NotifyForm } from "@/components/notify-form";
import { CATS, DEFERRED_CATS } from "./data";
import styles from "./landing.module.css";

// "La misma secuencia, para cada parte de tu gusto": una tarjeta por
// categoría del catálogo (D27) con sus fuentes de datos.
export function Gallery() {
  return (
    <div className={styles.galleryBlock}>
      <div className={styles.galleryHead}>
        <h3 className={styles.h3}>
          La misma secuencia, para cada parte de tu gusto
        </h3>
        <span className={styles.galleryNote}>
          Cambia la categoría, no el flujo.
        </span>
      </div>
      <p className={styles.galleryIntro}>
        Conectas la fuente → Ethos la normaliza → queda en tu perfil → tu IA la
        pide. Lo que viste con Juegos vale, tal cual, para cada una de tus
        categorías.
      </p>
      <div className={styles.galleryGrid}>
        {CATS.map((category) => (
          <div
            key={category.name}
            className={styles.galleryCard}
            style={{ "--ca": category.accent } as CSSProperties}
          >
            <div className={styles.cardPad}>
              <div className={styles.cardHead}>
                <span className={styles.cardInitial}>
                  {category.name.charAt(0)}
                </span>
                <div className={styles.cardName}>{category.name}</div>
                <span className={styles.cardCount}>
                  {category.providers.length}
                </span>
              </div>
              <div className={styles.cardSrcLabel}>Fuentes de datos</div>
              <div className={styles.srcList}>
                {category.providers.map((provider) => (
                  <div key={provider} className={styles.srcRow}>
                    <span className={styles.srcRowInitial}>
                      {provider.charAt(0)}
                    </span>
                    <span className={styles.srcRowName}>{provider}</span>
                    <span className={styles.srcRowDot} title="Conectada" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.soonBlock}>
        <div className={styles.soonBlockHead}>
          <h3 className={styles.h3}>En camino</h3>
          <span className={styles.galleryNote}>Aún no, pero llegan.</span>
        </div>
        <p className={styles.galleryIntro}>
          Estas categorías están en desarrollo. Déjanos tu correo y te avisamos
          en cuanto puedas conectarlas.
        </p>
        <div className={styles.soonGrid}>
          {DEFERRED_CATS.map((category) => (
            <div
              key={category.slug}
              className={styles.soonCard}
              style={{ "--ca": category.accent } as CSSProperties}
            >
              <div className={styles.cardHead}>
                <span className={styles.cardInitial}>{category.name.charAt(0)}</span>
                <div className={styles.cardName}>{category.name}</div>
                <span className={styles.soonTag}>en desarrollo</span>
              </div>
              <p className={styles.soonCardNote}>{category.note}</p>
              <NotifyForm category={category.slug} accent={category.accent} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
