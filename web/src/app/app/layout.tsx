import { Sidebar } from "@/components/app/sidebar";
import { AppHeader } from "@/components/app/app-header";
import styles from "@/components/app/app.module.css";

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
