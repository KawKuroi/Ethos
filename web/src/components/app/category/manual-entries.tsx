"use client";

import { useEffect, useState, type CSSProperties, type FormEvent } from "react";
import {
  addManualItem,
  deleteManualItem,
  listManualItems,
  type ItemStatus,
  type ManualItem,
} from "@/lib/api";
import styles from "./manual-entries.module.css";

const STATUS_LABELS: Record<ItemStatus, string> = {
  consumed: "Terminado",
  in_progress: "En curso",
  wishlist: "Pendiente",
  in_library: "En biblioteca",
  abandoned: "Abandonado",
};

const STATUS_ORDER: ItemStatus[] = [
  "consumed",
  "in_progress",
  "wishlist",
  "in_library",
  "abandoned",
];

// Entradas a mano de una categoría (D51): añade y borra registros sin
// proveedor. Se muestran junto a los datos del proveedor y cuentan en el
// resumen; `onChange` deja al detalle recargar sus cifras.
export function ManualEntries({
  slug,
  accent,
  onChange,
}: {
  slug: string;
  accent: string;
  onChange?: () => void;
}) {
  const [items, setItems] = useState<ManualItem[]>([]);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [statusValue, setStatusValue] = useState<ItemStatus>("consumed");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    listManualItems(slug)
      .then((rows) => {
        if (active) setItems(rows);
      })
      .catch(() => {
        // Sin sesión o sin datos: la sección arranca vacía.
      });
    return () => {
      active = false;
    };
  }, [slug]);

  async function add(event: FormEvent) {
    event.preventDefault();
    if (saving || !title.trim()) return;
    setSaving(true);
    setError("");
    try {
      const created = await addManualItem({
        category: slug,
        title: title.trim(),
        status: statusValue,
      });
      setItems((prev) => [...prev, created]);
      setTitle("");
      onChange?.();
    } catch {
      setError("No se pudo añadir. Reinténtalo.");
    } finally {
      setSaving(false);
    }
  }

  async function remove(externalId: string) {
    try {
      await deleteManualItem(slug, externalId);
      setItems((prev) => prev.filter((i) => i.external_id !== externalId));
      onChange?.();
    } catch {
      setError("No se pudo borrar. Reinténtalo.");
    }
  }

  return (
    <div className={styles.section} style={{ "--catAccent": accent } as CSSProperties}>
      <button
        type="button"
        className={styles.head}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span className={styles.eyebrow}>Añadido a mano</span>
        {items.length > 0 && <span className={styles.count}>{items.length}</span>}
        <span className={styles.toggle}>{open ? "Cerrar" : "Añadir +"}</span>
      </button>

      {items.length > 0 && (
        <div className={styles.list}>
          {items.map((item) => (
            <div key={item.external_id} className={styles.row}>
              <div className={styles.rowBody}>
                <span className={styles.rowTitle}>{item.title}</span>
                <span className={styles.rowStatus}>{STATUS_LABELS[item.status]}</span>
              </div>
              <button
                type="button"
                className={styles.remove}
                aria-label={`Borrar ${item.title}`}
                onClick={() => remove(item.external_id)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      {open && (
        <form className={styles.form} onSubmit={add}>
          <input
            type="text"
            className={styles.input}
            placeholder="Título"
            aria-label="Título"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={300}
          />
          <select
            className={styles.select}
            aria-label="Estado"
            value={statusValue}
            onChange={(e) => setStatusValue(e.target.value as ItemStatus)}
          >
            {STATUS_ORDER.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABELS[s]}
              </option>
            ))}
          </select>
          <button type="submit" className={styles.add} disabled={saving || !title.trim()}>
            {saving ? "Añadiendo…" : "Añadir"}
          </button>
          {error && (
            <span className={styles.error} role="alert">
              {error}
            </span>
          )}
        </form>
      )}
    </div>
  );
}
