"use client";

import { usePathname } from "next/navigation";
import { metaForPath } from "./nav";
import styles from "./app.module.css";

export function AppHeader() {
  const pathname = usePathname();
  const { title, sub } = metaForPath(pathname);

  return (
    <div className={styles.header}>
      <div>
        {/* h1: único encabezado principal de cada pantalla del panel (SEO
            y jerarquía de accesibilidad). */}
        <h1 className={styles.headerTitle}>{title}</h1>
        {sub && <div className={styles.headerSub}>{sub}</div>}
      </div>
    </div>
  );
}
