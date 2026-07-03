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
        <div className={styles.headerTitle}>{title}</div>
        {sub && <div className={styles.headerSub}>{sub}</div>}
      </div>
    </div>
  );
}
