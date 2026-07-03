"use client";

import { useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useTheme } from "next-themes";
import styles from "./settings.module.css";

// El tema real solo se conoce en cliente; evita desajustes de hidratación
// sin llamar a setState dentro de un efecto.
const emptySubscribe = () => () => {};

const TIMEZONES = [
  "America/Bogota",
  "America/Mexico_City",
  "America/Argentina/Buenos_Aires",
  "Europe/Madrid",
  "America/New_York",
  "America/Los_Angeles",
  "UTC",
];

type ThemeMode = { id: string; label: string; icon: React.ReactNode };

const THEME_MODES: ThemeMode[] = [
  {
    id: "light",
    label: "Claro",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <circle cx="12" cy="12" r="4.2" />
        <path d="M12 2.6v2.2M12 19.2v2.2M4.7 4.7l1.5 1.5M17.8 17.8l1.5 1.5M2.6 12h2.2M19.2 12h2.2M4.7 19.3l1.5-1.5M17.8 6.2l1.5-1.5" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: "dark",
    label: "Oscuro",
    icon: (
      <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M20.5 14.8A8.2 8.2 0 0 1 9.2 3.5a7.2 7.2 0 1 0 11.3 11.3z" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    id: "system",
    label: "Sistema",
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <rect x="3" y="4" width="18" height="12" rx="1.6" />
        <path d="M9 20h6M12 16v4" strokeLinecap="round" />
      </svg>
    ),
  },
];

type ConfirmKind = "wipe" | "delete" | null;

const CONFIRM_COPY: Record<
  "wipe" | "delete",
  { title: string; body: string; label: string }
> = {
  wipe: {
    title: "Eliminar todos los datos",
    body: "Se borra el contexto de todas tus fuentes. Tu cuenta y tus ajustes se conservan, pero tendrás que reconectar cada fuente.",
    label: "Eliminar datos",
  },
  delete: {
    title: "Eliminar tu cuenta",
    body: "Se eliminan tu perfil, tus fuentes y todo tu contexto de forma permanente. Recibirás un correo con 30 días para deshacerlo.",
    label: "Eliminar cuenta",
  },
};

export function Settings() {
  const { theme, setTheme } = useTheme();
  const mounted = useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false,
  );
  const [name, setName] = useState("Tu perfil");
  const [handle, setHandle] = useState("tu_gusto");
  const [timezone, setTimezone] = useState("America/Bogota");
  const [saved, setSaved] = useState(false);
  const [confirm, setConfirm] = useState<ConfirmKind>(null);
  const [notice, setNotice] = useState<string | null>(null);

  function save() {
    // Persistencia real del perfil: Fase 4.
    setSaved(true);
    setTimeout(() => setSaved(false), 1600);
  }

  function runConfirm() {
    // El borrado real (correo + purga diferida de 30 días) llega en Fase 4.
    setConfirm(null);
    setNotice(
      "El borrado real llegará con el backend (correo + deshacer de 30 días).",
    );
    setTimeout(() => setNotice(null), 3200);
  }

  return (
    <div className={`eth-screen ${styles.screen}`}>
      {/* Perfil */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>Perfil</div>
        <div className={styles.sectionSub}>
          Cómo apareces en tu perfil de gusto y en las descargas de contexto.
        </div>
        <div className={styles.grid2}>
          <div>
            <div className={styles.fieldLabel}>Nombre</div>
            <input
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
              aria-label="Nombre"
            />
          </div>
          <div>
            <div className={styles.fieldLabel}>Usuario</div>
            <div className={styles.handleBox}>
              <span className={styles.handleAt}>@</span>
              <input
                className={styles.handleInput}
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                aria-label="Usuario"
              />
            </div>
          </div>
        </div>
        <div className={styles.fieldGap}>
          <div className={styles.fieldLabel}>Zona horaria</div>
          <select
            className={styles.select}
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            aria-label="Zona horaria"
          >
            {TIMEZONES.map((tz) => (
              <option key={tz} value={tz}>
                {tz}
              </option>
            ))}
          </select>
          <div className={styles.hint}>
            Usada para fechar tus sincronizaciones y actividad.
          </div>
        </div>
        <div className={styles.saveRow}>
          <button type="button" className={styles.saveBtn} onClick={save}>
            {saved ? "Guardado ✓" : "Guardar cambios"}
          </button>
        </div>
      </div>

      {/* Apariencia */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>Apariencia</div>
        <div className={styles.sectionSub}>
          Tema de la interfaz. Se guarda en este dispositivo.
        </div>
        <div className={styles.fieldLabel}>Tema</div>
        <div className={styles.themeGrid}>
          {THEME_MODES.map((mode) => {
            const active = mounted && theme === mode.id;
            return (
              <button
                key={mode.id}
                type="button"
                className={`${styles.themeBtn} ${active ? styles.themeActive : ""}`}
                onClick={() => setTheme(mode.id)}
                aria-pressed={active}
              >
                {mode.icon}
                {mode.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Datos y contexto */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>Datos y contexto</div>
        <div className={styles.sectionSub}>
          Lo que Ethos tiene normalizado y a quién se lo entrega.
        </div>
        <div className={styles.statsGrid}>
          <div className={styles.statBox}>
            <div className={styles.statValue}>1</div>
            <div className={styles.statLabel}>fuentes activas</div>
          </div>
          <div className={styles.statBox}>
            <div className={styles.statValue}>312</div>
            <div className={styles.statLabel}>registros de contexto</div>
          </div>
        </div>
        <div className={styles.links}>
          <Link href="/app/fuentes" className={styles.linkBtn}>
            Gestionar fuentes →
          </Link>
          <Link href="/app/conectar-ia" className={styles.linkBtn}>
            Conexión con la IA →
          </Link>
        </div>
      </div>

      {/* Zona de peligro */}
      <div className={styles.danger}>
        <div className={styles.dangerTitle}>Zona de peligro</div>
        <div className={styles.dangerSub}>
          Acciones destructivas. Al eliminar la cuenta recibirás un correo con 30
          días para deshacerlo.
        </div>
        <div className={styles.dangerList}>
          <div className={styles.dangerRow}>
            <div className={styles.dangerRowBody}>
              <div className={styles.dangerRowTitle}>Eliminar todos los datos</div>
              <div className={styles.dangerRowSub}>
                Borra el contexto de todas tus fuentes. La cuenta se conserva.
              </div>
            </div>
            <button
              type="button"
              className={styles.dangerGhost}
              onClick={() => setConfirm("wipe")}
            >
              Eliminar datos
            </button>
          </div>
          <div className={styles.dangerRow}>
            <div className={styles.dangerRowBody}>
              <div className={styles.dangerRowTitle}>Eliminar cuenta</div>
              <div className={styles.dangerRowSub}>
                Elimina tu perfil, fuentes y contexto de forma permanente.
              </div>
            </div>
            <button
              type="button"
              className={styles.dangerSolid}
              onClick={() => setConfirm("delete")}
            >
              Eliminar cuenta
            </button>
          </div>
        </div>
        {notice && <div className={styles.notice}>{notice}</div>}
      </div>

      {confirm && (
        <div
          className={styles.overlay}
          role="dialog"
          aria-modal="true"
          aria-label={CONFIRM_COPY[confirm].title}
          onClick={() => setConfirm(null)}
        >
          <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalTitle}>{CONFIRM_COPY[confirm].title}</div>
            <div className={styles.modalBody}>{CONFIRM_COPY[confirm].body}</div>
            <div className={styles.modalActions}>
              <button
                type="button"
                className={styles.modalCancel}
                onClick={() => setConfirm(null)}
              >
                Cancelar
              </button>
              <button
                type="button"
                className={styles.dangerSolid}
                onClick={runConfirm}
              >
                {CONFIRM_COPY[confirm].label}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
