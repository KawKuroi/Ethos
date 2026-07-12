"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { CSSProperties } from "react";
import { Logo } from "@/components/logo";
import { isMcpConnected, useMcpStatus } from "@/lib/use-mcp-status";
import { useUser } from "@/lib/use-user";
import { CATEGORY_DETAIL } from "./category/data";
import { NAV } from "./nav";
import { NavIcon, GearIcon } from "./nav-icons";
import styles from "./app.module.css";

const CATEGORIES = Object.values(CATEGORY_DETAIL);

export function Sidebar() {
  const pathname = usePathname();
  const { name, email } = useUser();
  // El badge de "IA sin conectar" se apaga solo cuando el estado confirma
  // la conexión (OAuth o token manual).
  const { status } = useMcpStatus();
  const displayName = name ?? "Tu perfil";
  const initial = (name ?? email ?? "E").charAt(0).toUpperCase();

  // Las categorías tienen su propia entrada en la barra, así que Inicio solo
  // se resalta en su ruta exacta.
  function isActive(href: string): boolean {
    if (href === "/app") return pathname === "/app";
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
              {item.id === "mcp" && !isMcpConnected(status) && (
                <span className={styles.badge} aria-label="IA sin conectar" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Acceso directo a cada categoría desde cualquier pantalla, sin pasar
          por Inicio o Fuentes. El punto lleva el acento de la categoría. */}
      <div className={styles.navSectionLabel}>Categorías</div>
      <nav className={styles.nav} aria-label="Categorías">
        {CATEGORIES.map((category) => {
          const href = `/app/categoria/${category.slug}`;
          const active = pathname === href;
          return (
            <Link
              key={category.slug}
              href={href}
              className={`${styles.navItem} ${active ? styles.navItemActive : ""}`}
              aria-current={active ? "page" : undefined}
            >
              <span className={styles.navIcon}>
                <span
                  className={styles.catDot}
                  style={{ "--catAccent": category.accent } as CSSProperties}
                />
              </span>
              <span className={styles.navLabel}>{category.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className={styles.spacer} />

      <div className={styles.foot}>
        <div className={styles.avatar}>{initial}</div>
        <div className={styles.profile}>
          <span className={styles.profileName}>{displayName}</span>
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
