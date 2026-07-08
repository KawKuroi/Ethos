import type { Metadata } from "next";
import { Sidebar } from "@/components/app/sidebar";
import { AppHeader } from "@/components/app/app-header";
import styles from "@/components/app/app.module.css";

// El panel es zona privada (los datos requieren sesión): fuera del índice
// de buscadores; el posicionamiento se concentra en la landing.
export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={styles.shell}>
      <Sidebar />
      <main className={styles.main}>
        <AppHeader />
        <div className={styles.content}>{children}</div>
      </main>
    </div>
  );
}
