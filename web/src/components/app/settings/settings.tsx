"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useTheme } from "next-themes";
import {
  deleteAllData,
  getAccountDeletion,
  requestAccountDeletion,
  undoAccountDeletion,
} from "@/lib/api";
import { fmtInt } from "@/lib/format";
import { goToLanding } from "@/lib/navigation";
import { getBrowserClient } from "@/lib/supabase/client";
import { useActiveSources } from "@/lib/use-active-sources";
import { invalidateSourceCache } from "@/lib/use-source";
import { useUser } from "@/lib/use-user";
import styles from "./settings.module.css";

// El tema real solo se conoce en cliente; evita desajustes de hidratación
// sin llamar a setState dentro de un efecto.
const emptySubscribe = () => () => {};

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
    body: "Se eliminan tu perfil, tus fuentes y todo tu contexto de forma permanente. Se cerrará tu sesión y recibirás un correo con 30 días para deshacerlo (inicia sesión de nuevo para cancelarlo).",
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
  const { name: sessionName, email } = useUser();
  // Hasta que el usuario edita, el campo sigue al nombre de la sesión
  // (que llega asíncrono desde Supabase); después manda el borrador.
  const [draft, setDraft] = useState<string | null>(null);
  const name = draft ?? sessionName ?? "";
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState<ConfirmKind>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  // Fecha de purga si el borrado de cuenta ya está programado (D53).
  const [purgeAfter, setPurgeAfter] = useState<string | null>(null);
  const [signingOut, setSigningOut] = useState(false);
  // Fuentes reales del usuario para las cifras de "Datos y contexto".
  const { loading: sourcesLoading, views } = useActiveSources();

  useEffect(() => {
    let active = true;
    getAccountDeletion()
      .then((status) => {
        if (active && status.scheduled) setPurgeAfter(status.purge_after);
      })
      .catch(() => {
        // Sin sesión o backend no disponible: sin banner de borrado.
      });
    return () => {
      active = false;
    };
  }, []);

  async function save() {
    if (saving) return;
    const trimmed = name.trim();
    if (trimmed.length === 0) {
      setProfileError("Escribe un nombre antes de guardar.");
      return;
    }
    setSaving(true);
    setProfileError(null);
    try {
      // El nombre vive en user_metadata (lo fija el registro); el sidebar
      // se actualiza solo vía onAuthStateChange (USER_UPDATED).
      const { error } = await getBrowserClient().auth.updateUser({
        data: { full_name: trimmed },
      });
      if (error) throw error;
      setSaved(true);
      setTimeout(() => setSaved(false), 1600);
    } catch {
      setProfileError("No se pudo guardar el nombre. Reinténtalo.");
    } finally {
      setSaving(false);
    }
  }

  function flashNotice(text: string) {
    setNotice(text);
    setTimeout(() => setNotice(null), 4000);
  }

  async function signOut() {
    if (signingOut) return;
    setSigningOut(true);
    try {
      await getBrowserClient().auth.signOut();
      invalidateSourceCache();
      goToLanding();
    } catch {
      setSigningOut(false);
      flashNotice("No se pudo cerrar la sesión. Reinténtalo.");
    }
  }

  async function runConfirm() {
    if (working || !confirm) return;
    const kind = confirm;
    setWorking(true);
    try {
      if (kind === "wipe") {
        await deleteAllData();
        // Las pantallas cacheadas (Inicio, Fuentes…) deben volver a pedir
        // el estado: ya no hay contexto que mostrar.
        invalidateSourceCache();
        flashNotice(
          "Datos eliminados. Reconecta tus fuentes cuando quieras empezar de nuevo.",
        );
        setConfirm(null);
      } else {
        await requestAccountDeletion();
        // Cuenta programada para purga: se cierra la sesión y se vuelve a la
        // landing. Al iniciar sesión de nuevo, Ajustes ofrece deshacer.
        await getBrowserClient()
          .auth.signOut()
          .catch(() => {
            // La purga ya está programada; la sesión caduca sola.
          });
        invalidateSourceCache();
        goToLanding();
        return;
      }
    } catch {
      flashNotice("No se pudo completar la acción. Reinténtalo.");
    } finally {
      setWorking(false);
    }
  }

  async function undoDeletion() {
    if (working) return;
    setWorking(true);
    try {
      await undoAccountDeletion();
      setPurgeAfter(null);
      flashNotice("Borrado cancelado. Tu cuenta sigue activa.");
    } catch {
      flashNotice("No se pudo deshacer. Reinténtalo.");
    } finally {
      setWorking(false);
    }
  }

  const purgeDate = purgeAfter
    ? new Date(purgeAfter).toLocaleDateString("es-ES", {
        day: "numeric",
        month: "long",
        year: "numeric",
      })
    : null;

  const liveViews = views.filter((view) => view.live);
  const totalRecords = liveViews.reduce((sum, view) => sum + view.records, 0);

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
              onChange={(e) => setDraft(e.target.value)}
              aria-label="Nombre"
            />
          </div>
          <div>
            <div className={styles.fieldLabel}>Correo</div>
            <input
              className={styles.input}
              value={email ?? ""}
              readOnly
              disabled
              aria-label="Correo"
            />
          </div>
        </div>
        <div className={styles.saveRow}>
          <button
            type="button"
            className={styles.saveBtn}
            onClick={save}
            disabled={saving}
          >
            {saved ? "Guardado ✓" : saving ? "Guardando…" : "Guardar cambios"}
          </button>
        </div>
        {profileError && (
          <div className={styles.notice} role="alert">
            {profileError}
          </div>
        )}
      </div>

      {/* Apariencia */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>Apariencia</div>
        <div className={styles.sectionSub}>
          Tema de toda la interfaz (landing y panel). Se guarda en este
          dispositivo.
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
            <div className={styles.statValue}>
              {sourcesLoading ? "—" : liveViews.length}
            </div>
            <div className={styles.statLabel}>
              {liveViews.length === 1 ? "fuente activa" : "fuentes activas"}
            </div>
          </div>
          <div className={styles.statBox}>
            <div className={styles.statValue}>
              {sourcesLoading ? "—" : fmtInt(totalRecords)}
            </div>
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

      {/* Sesión */}
      <div className={styles.section}>
        <div className={styles.sectionTitle}>Sesión</div>
        <div className={styles.sectionSub}>
          Cierra tu sesión en este dispositivo. Tus fuentes y tu contexto se
          conservan.
        </div>
        <button
          type="button"
          className={styles.linkBtn}
          onClick={signOut}
          disabled={signingOut}
        >
          {signingOut ? "Cerrando sesión…" : "Cerrar sesión"}
        </button>
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
                {purgeDate
                  ? `Borrado programado: se eliminará el ${purgeDate}.`
                  : "Elimina tu perfil, fuentes y contexto de forma permanente."}
              </div>
            </div>
            {purgeDate ? (
              <button
                type="button"
                className={styles.dangerGhost}
                onClick={undoDeletion}
                disabled={working}
              >
                Deshacer
              </button>
            ) : (
              <button
                type="button"
                className={styles.dangerSolid}
                onClick={() => setConfirm("delete")}
              >
                Eliminar cuenta
              </button>
            )}
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
                disabled={working}
              >
                {working ? "Un momento…" : CONFIRM_COPY[confirm].label}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
