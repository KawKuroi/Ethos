"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import type { CSSProperties } from "react";
import { CATEGORY_DETAIL } from "./category/data";
import { NAV, SCREEN_META } from "./nav";
import styles from "./quick-nav.module.css";

type Target = {
  href: string;
  label: string;
  hint: string;
  accent?: string;
  keys?: string;
};

const CATEGORY_PREFIX = "/app/categoria/";
const CATEGORY_SLUGS = Object.keys(CATEGORY_DETAIL);

// Cordales "g + tecla" para las pantallas del shell.
const CHORD_SCREENS: Record<string, string> = {
  i: "/app",
  f: "/app/fuentes",
  c: "/app/conectar-ia",
  a: "/app/ayuda",
  s: "/app/ajustes",
};

const SCREEN_KEYS: Record<string, string> = {
  "/app": "g i",
  "/app/fuentes": "g f",
  "/app/conectar-ia": "g c",
  "/app/ayuda": "g a",
  "/app/ajustes": "g s",
};

// Ajustes vive en el pie de la barra (engranaje), pero la paleta lo lista
// como destino de primera clase.
const SCREENS: Target[] = [
  ...NAV.map((item) => ({
    href: item.href,
    label: item.label,
    hint: SCREEN_META[item.href]?.sub ?? "",
    keys: SCREEN_KEYS[item.href],
  })),
  {
    href: "/app/ajustes",
    label: "Ajustes",
    hint: SCREEN_META["/app/ajustes"].sub,
    keys: SCREEN_KEYS["/app/ajustes"],
  },
];

const CATEGORIES: Target[] = Object.values(CATEGORY_DETAIL).map((c, i) => ({
  href: `${CATEGORY_PREFIX}${c.slug}`,
  label: c.name,
  hint: c.provider,
  accent: c.accent,
  keys: `g ${i + 1}`,
}));

// Lista única de atajos: la comparte el modal "?" y la pantalla de Ayuda.
export const KEYBOARD_SHORTCUTS: { keys: string; text: string }[] = [
  { keys: "Ctrl K", text: "Abrir la paleta e ir a cualquier pantalla" },
  { keys: "g i", text: "Ir a Inicio" },
  { keys: "g f", text: "Ir a Fuentes" },
  { keys: "g c", text: "Ir a Conectar IA" },
  { keys: "g a", text: "Ir a Ayuda" },
  { keys: "g s", text: "Ir a Ajustes" },
  { keys: "g 1…5", text: "Ir a una categoría, en el orden de la barra" },
  { keys: "[ ]", text: "Categoría anterior / siguiente (dentro de una categoría)" },
  { keys: "?", text: "Mostrar esta ayuda" },
];

// Búsqueda sin distinguir mayúsculas ni acentos ("musica" encuentra "Música").
function norm(text: string): string {
  return text
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
}

function inEditable(target: EventTarget | null): boolean {
  return (
    target instanceof HTMLElement &&
    target.closest("input, textarea, select, [contenteditable]") != null
  );
}

function matches(target: Target, q: string): boolean {
  return !q || norm(`${target.label} ${target.hint}`).includes(q);
}

export function QuickNav() {
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState<"palette" | "help" | null>(null);
  const [query, setQuery] = useState("");
  const [cursor, setCursor] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);
  // "g" pendiente del cordal: espera la segunda tecla durante un instante.
  const chordArmed = useRef(false);
  const chordTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const q = norm(query.trim());
  const screens = useMemo(() => SCREENS.filter((t) => matches(t, q)), [q]);
  const categories = useMemo(() => CATEGORIES.filter((t) => matches(t, q)), [q]);
  const results = useMemo(() => [...screens, ...categories], [screens, categories]);

  function openPalette() {
    setQuery("");
    setCursor(0);
    setOpen("palette");
  }

  function go(href: string) {
    setOpen(null);
    if (href !== pathname) router.push(href);
  }

  useEffect(() => {
    if (open === "palette") inputRef.current?.focus();
  }, [open]);

  // Mantiene visible la opción resaltada al moverse con las flechas.
  useEffect(() => {
    const el = listRef.current?.querySelector('[aria-selected="true"]');
    if (el instanceof HTMLElement && typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ block: "nearest" });
    }
  }, [cursor, open]);

  useEffect(() => {
    function disarmChord() {
      chordArmed.current = false;
      if (chordTimer.current) {
        clearTimeout(chordTimer.current);
        chordTimer.current = null;
      }
    }

    function onKeyDown(e: KeyboardEvent) {
      // La paleta se abre/cierra incluso con el foco en un campo.
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((prev) => (prev === "palette" ? null : "palette"));
        setQuery("");
        setCursor(0);
        return;
      }
      if (open !== null) {
        if (e.key === "Escape") setOpen(null);
        return;
      }
      if (inEditable(e.target) || e.ctrlKey || e.metaKey || e.altKey) {
        disarmChord();
        return;
      }

      if (e.key === "?") {
        e.preventDefault();
        setOpen("help");
        return;
      }

      if (chordArmed.current) {
        disarmChord();
        const screen = CHORD_SCREENS[e.key.toLowerCase()];
        if (screen) {
          e.preventDefault();
          if (screen !== pathname) router.push(screen);
          return;
        }
        const index = Number.parseInt(e.key, 10) - 1;
        const slug = CATEGORY_SLUGS[index];
        if (!Number.isNaN(index) && slug) {
          e.preventDefault();
          const href = `${CATEGORY_PREFIX}${slug}`;
          if (href !== pathname) router.push(href);
        }
        return;
      }

      if (e.key.toLowerCase() === "g") {
        chordArmed.current = true;
        chordTimer.current = setTimeout(disarmChord, 1500);
        return;
      }

      // Recorrido secuencial del catálogo dentro de una categoría.
      if ((e.key === "[" || e.key === "]") && pathname.startsWith(CATEGORY_PREFIX)) {
        const current = CATEGORY_SLUGS.indexOf(pathname.slice(CATEGORY_PREFIX.length));
        if (current !== -1) {
          e.preventDefault();
          const delta = e.key === "]" ? 1 : -1;
          const total = CATEGORY_SLUGS.length;
          const slug = CATEGORY_SLUGS[(current + delta + total) % total];
          router.push(`${CATEGORY_PREFIX}${slug}`);
        }
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      disarmChord();
    };
  }, [open, pathname, router]);

  function onInputKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (results.length === 0) return;
      const delta = e.key === "ArrowDown" ? 1 : -1;
      setCursor((prev) => (prev + delta + results.length) % results.length);
      return;
    }
    if (e.key === "Enter") {
      e.preventDefault();
      const target = results[cursor] ?? results[0];
      if (target) go(target.href);
      return;
    }
    if (e.key === "Escape") setOpen(null);
  }

  function renderOption(target: Target, index: number) {
    const active = cursor === index;
    return (
      <button
        key={target.href}
        type="button"
        role="option"
        aria-selected={active}
        className={`${styles.option} ${active ? styles.optionActive : ""}`}
        onMouseEnter={() => setCursor(index)}
        onClick={() => go(target.href)}
      >
        <span
          className={`${styles.optionDot} ${target.accent ? "" : styles.optionDotScreen}`}
          style={
            target.accent
              ? ({ "--catAccent": target.accent } as CSSProperties)
              : undefined
          }
        />
        <span className={styles.optionLabel}>{target.label}</span>
        {target.href === pathname && (
          <span className={styles.optionHere}>estás aquí</span>
        )}
        <span className={styles.optionHint}>{target.hint}</span>
        {target.keys && <kbd className={styles.kbdSmall}>{target.keys}</kbd>}
      </button>
    );
  }

  return (
    <>
      <button
        type="button"
        className={styles.trigger}
        onClick={openPalette}
        aria-label="Ir a… (Ctrl+K)"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
          <circle cx="11" cy="11" r="7" />
          <path d="m20 20-3.5-3.5" strokeLinecap="round" />
        </svg>
        <span className={styles.triggerText}>Ir a…</span>
        <kbd className={styles.kbd}>Ctrl K</kbd>
      </button>

      {open === "palette" && (
        <div className={styles.overlay} onClick={() => setOpen(null)}>
          <div
            className={styles.panel}
            role="dialog"
            aria-modal="true"
            aria-label="Ir a"
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.searchRow}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <circle cx="11" cy="11" r="7" />
                <path d="m20 20-3.5-3.5" strokeLinecap="round" />
              </svg>
              <input
                ref={inputRef}
                className={styles.searchInput}
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setCursor(0);
                }}
                onKeyDown={onInputKeyDown}
                placeholder="Buscar pantalla o categoría…"
                aria-label="Buscar destino"
              />
              <kbd className={styles.kbdSmall}>esc</kbd>
            </div>
            <div className={styles.list} role="listbox" aria-label="Destinos" ref={listRef}>
              {results.length === 0 && (
                <div className={styles.empty}>Sin resultados para «{query}»</div>
              )}
              {screens.length > 0 && (
                <div className={styles.groupLabel}>Pantallas</div>
              )}
              {screens.map((target, i) => renderOption(target, i))}
              {categories.length > 0 && (
                <div className={styles.groupLabel}>Categorías</div>
              )}
              {categories.map((target, i) => renderOption(target, screens.length + i))}
            </div>
            <div className={styles.footHints}>
              ↑↓ moverse · Enter abrir · esc cerrar · ? todos los atajos
            </div>
          </div>
        </div>
      )}

      {open === "help" && (
        <div className={styles.overlay} onClick={() => setOpen(null)}>
          <div
            className={styles.panel}
            role="dialog"
            aria-modal="true"
            aria-label="Atajos de teclado"
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.helpHead}>
              <div className={styles.helpTitle}>Atajos de teclado</div>
              <button
                type="button"
                className={styles.helpClose}
                onClick={() => setOpen(null)}
                aria-label="Cerrar"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M6 6l12 12M18 6 6 18" strokeLinecap="round" />
                </svg>
              </button>
            </div>
            <div className={styles.helpBody}>
              {KEYBOARD_SHORTCUTS.map((row) => (
                <div key={row.keys} className={styles.helpRow}>
                  <kbd className={styles.kbdSmall}>{row.keys}</kbd>
                  <span className={styles.helpText}>{row.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
