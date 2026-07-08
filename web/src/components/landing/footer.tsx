import { Logo } from "@/components/logo";
import styles from "./landing.module.css";

export function LandingFooter() {
  return (
    <footer className={styles.footer}>
      <span className={styles.footerBrand}>
        <span className={styles.footerLogo}>
          <Logo width={18} height={16} bold />
        </span>
        Ethos — tu gusto, ordenado.
      </span>
      <span>contexto para tu IA · MCP</span>
    </footer>
  );
}
