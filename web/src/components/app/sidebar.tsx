"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/logo";
import { useUser } from "@/lib/use-user";
import { NAV } from "./nav";
import { NavIcon, GearIcon } from "./nav-icons";
import styles from "./app.module.css";

// TODO: sustituir por el estado real de conexión del MCP (tarea Conectar IA).
const MCP_CONNECTED = false;

export function Sidebar() {
  const pathname = usePathname();
  const { name, email } = useUser();
  const displayName = name ?? "Tu perfil";
  const initial = (name ?? email ?? "E").charAt(0).toUpperCase();

  function isActive(href: string): boolean {
    if (href === "/app") {
      return pathname === "/app" || pathname.startsWith("/app/categoria");
    }
    return pathname === href || pathname.startsWith(`${href}/`);
  }

  return (
    <aside className={styles.aside}>
      {/* El logo lleva a la landing; la sesión de Supabase persiste. */}
      <Link href="/" className={styles.brand} title="Ir a la página principal">
        <Logo width={38} height={34} />
        <span className={styles.brandText}>Ethos</span>
      </Link>

      <nav className={styles.nav} aria-label="Navegación principal">
        {NAV.map((item) => {
          const active = isActive(item.href);
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`${styles.navItem} ${active ? styles.navItemActive : ""}`}
              aria-current={active ? "page" : undefined}
            >
              <span className={styles.navIcon}>
                <NavIcon name={item.icon} />
              </span>
              <span className={styles.navLabel}>{item.label}</span>
              {item.id === "mcp" && !MCP_CONNECTED && (
                <span className={styles.badge} aria-label="IA sin conectar" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className={styles.spacer} />

      <div className={styles.foot}>
        <div className={styles.avatar}>{initial}</div>
        <div className={styles.profile}>
          <span className={styles.profileName}>{displayName}</span>
          {email && <span className={styles.profileHandle}>{email}</span>}
        </div>
        <Link
          href="/app/ajustes"
          title="Ajustes"
          aria-label="Ajustes"
          className={`${styles.gearBtn} ${
            pathname === "/app/ajustes" ? styles.gearActive : ""
          }`}
        >
          <GearIcon />
        </Link>
      </div>
    </aside>
  );
}
