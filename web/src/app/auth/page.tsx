import type { Metadata } from "next";
import { AuthForm } from "@/components/auth/auth-form";
import { BrandPanel } from "@/components/auth/brand-panel";
import { ThemeToggle } from "@/components/theme-toggle";
import styles from "@/components/auth/auth.module.css";

export const metadata: Metadata = {
  title: "Entrar · Ethos",
  description: "Inicia sesión o crea tu cuenta de Ethos.",
};

export default function AuthPage() {
  return (
    <main className={styles.wrap}>
      <BrandPanel />
      <div className={styles.panel}>
        <ThemeToggle className={styles.themeToggle} />
        <AuthForm />
      </div>
    </main>
  );
}
