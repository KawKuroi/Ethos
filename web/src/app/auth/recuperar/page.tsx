import type { Metadata } from "next";
import { RecoverForm } from "@/components/auth/recover-form";
import { BrandPanel } from "@/components/auth/brand-panel";
import { ThemeToggle } from "@/components/theme-toggle";
import styles from "@/components/auth/auth.module.css";

export const metadata: Metadata = {
  title: "Recuperar contraseña",
  description: "Te enviamos un enlace para restablecer tu contraseña.",
};

export default function RecoverPage() {
  return (
    <main className={styles.wrap}>
      <BrandPanel />
      <div className={styles.panel}>
        <ThemeToggle className={styles.themeToggle} />
        <RecoverForm />
      </div>
    </main>
  );
}
