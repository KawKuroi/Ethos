"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/logo";
import { NAV } from "./nav";
import { NavIcon, GearIcon } from "./nav-icons";
import styles from "./app.module.css";

// TODO: sustituir por el estado real de conexión del MCP (tarea Conectar IA).
const MCP_CONNECTED = false;

export function Sidebar() {
  const pathname = usePathname();

  function isActive(href: string): boolean {
    if (href === "/app") {
      return pathname === "/app" || pathname.startsWith("/app/categoria");
    }
    return pathname === href || pathname.startsWith(`${href}/`);
  }

  return (
    <aside className={styles.aside}>
      <div className={styles.brand}>
        <Logo width={38} height={34} />
        <span className={styles.brandText}>Ethos</span>
      </div>

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
        <div className={styles.avatar}>E</div>
        <div className={styles.profile}>
          <span className={styles.profileName}>Tu perfil</span>
          <span className={styles.profileHandle}>@tu_gusto</span>
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
