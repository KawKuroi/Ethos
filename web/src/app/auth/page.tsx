import { Suspense } from "react";
import type { Metadata } from "next";
import { AuthForm } from "@/components/auth/auth-form";
import { BrandPanel } from "@/components/auth/brand-panel";
import styles from "@/components/auth/auth.module.css";

export const metadata: Metadata = {
  title: "Entrar",
  description: "Inicia sesión o crea tu cuenta de Ethos.",
};

export default function AuthPage() {
  return (
    <main className={styles.wrap}>
      <BrandPanel />
      <div className={styles.panel}>
        {/* useSearchParams (retornos de confirmación/OAuth) exige Suspense
            para poder prerenderizar la página. */}
        <Suspense fallback={null}>
          <AuthForm />
        </Suspense>
      </div>
    </main>
  );
}
