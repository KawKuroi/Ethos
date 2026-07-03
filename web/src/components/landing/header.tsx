import Link from "next/link";

import { Logo } from "@/components/logo";
import { ThemeToggle } from "@/components/theme-toggle";
import { GITHUB_URL } from "./data";
import styles from "./landing.module.css";

export function LandingHeader() {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <Logo />
        <span className={styles.brandName}>Ethos</span>
      </div>
      <nav className={styles.nav}>
        <ThemeToggle className={styles.iconBtn} />
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener"
          title="Ver en GitHub"
          aria-label="Ver en GitHub"
          className={styles.iconBtn}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 1.8a10.2 10.2 0 0 0-3.22 19.88c.51.09.7-.22.7-.49v-1.9c-2.84.62-3.44-1.2-3.44-1.2-.46-1.18-1.14-1.5-1.14-1.5-.93-.63.07-.62.07-.62 1.03.07 1.57 1.06 1.57 1.06.91 1.57 2.4 1.12 2.98.85.09-.66.36-1.12.65-1.37-2.27-.26-4.65-1.13-4.65-5.05 0-1.11.4-2.02 1.05-2.73-.1-.26-.46-1.3.1-2.7 0 0 .86-.27 2.8 1.04a9.7 9.7 0 0 1 5.1 0c1.94-1.31 2.8-1.04 2.8-1.04.56 1.4.2 2.44.1 2.7.66.71 1.05 1.62 1.05 2.73 0 3.93-2.39 4.79-4.66 5.04.37.32.7.94.7 1.9v2.82c0 .27.18.59.7.49A10.2 10.2 0 0 0 12 1.8z" />
          </svg>
        </a>
        <Link href="/app" className={styles.primaryBtn}>
          Abrir la app
        </Link>
      </nav>
    </header>
  );
}
