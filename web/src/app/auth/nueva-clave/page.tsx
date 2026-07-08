import type { Metadata } from "next";
import { NewPasswordForm } from "@/components/auth/new-password-form";
import { BrandPanel } from "@/components/auth/brand-panel";
import styles from "@/components/auth/auth.module.css";

export const metadata: Metadata = {
  title: "Nueva contraseña",
  description: "Elige una contraseña nueva para tu cuenta.",
};

export default function NewPasswordPage() {
  return (
    <main className={styles.wrap}>
      <BrandPanel />
      <div className={styles.panel}>
        <NewPasswordForm />
      </div>
    </main>
  );
}
