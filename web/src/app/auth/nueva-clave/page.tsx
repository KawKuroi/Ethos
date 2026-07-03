import type { Metadata } from "next";
import { NewPasswordForm } from "@/components/auth/new-password-form";
import { BrandPanel } from "@/components/auth/brand-panel";
import { ThemeToggle } from "@/components/theme-toggle";
import styles from "@/components/auth/auth.module.css";

export const metadata: Metadata = {
  title: "Nueva contraseña · Ethos",
  description: "Elige una contraseña nueva para tu cuenta.",
};

export default function NewPasswordPage() {
  return (
    <main className={styles.wrap}>
      <BrandPanel />
      <div className={styles.panel}>
        <ThemeToggle className={styles.themeToggle} />
        <NewPasswordForm />
      </div>
    </main>
  );
}
