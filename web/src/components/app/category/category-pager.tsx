import Link from "next/link";
import type { CSSProperties } from "react";
import { CATEGORY_DETAIL } from "./data";
import styles from "./category.module.css";

function accentVar(accent: string): CSSProperties {
  return { "--catAccent": accent } as CSSProperties;
}

// Recorrido secuencial del catálogo desde el pie del detalle, con ciclo en
// los extremos. Equivale a los atajos [ y ].
export function CategoryPager({ slug }: { slug: string }) {
  const slugs = Object.keys(CATEGORY_DETAIL);
  const index = slugs.indexOf(slug);
  if (index === -1 || slugs.length < 2) return null;

  const total = slugs.length;
  const prev = CATEGORY_DETAIL[slugs[(index - 1 + total) % total]];
  const next = CATEGORY_DETAIL[slugs[(index + 1) % total]];

  return (
    <nav className={`eth-screen ${styles.pager}`} aria-label="Otras categorías">
      <Link
        href={`/app/categoria/${prev.slug}`}
        className={styles.pagerLink}
        style={accentVar(prev.accent)}
      >
        <span className={styles.pagerArrow} aria-hidden="true">
          ←
        </span>
        <span className={styles.pagerBody}>
          <span className={styles.pagerLabel}>Anterior</span>
          <span className={styles.pagerName}>
            <span className={styles.pagerDot} />
            {prev.name}
          </span>
        </span>
      </Link>
      <Link
        href={`/app/categoria/${next.slug}`}
        className={`${styles.pagerLink} ${styles.pagerNext}`}
        style={accentVar(next.accent)}
      >
        <span className={styles.pagerArrow} aria-hidden="true">
          →
        </span>
        <span className={styles.pagerBody}>
          <span className={styles.pagerLabel}>Siguiente</span>
          <span className={styles.pagerName}>
            <span className={styles.pagerDot} />
            {next.name}
          </span>
        </span>
      </Link>
    </nav>
  );
}
