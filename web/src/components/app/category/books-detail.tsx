"use client";

import { useState } from "react";
import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import type { BooksSource, BooksSummary } from "@/lib/api";
import { fmtInt, relativeTime } from "@/lib/format";
import { useBooksSource } from "@/lib/use-books-source";
import { ImportPanel } from "../import-panel";
import { LoadingState } from "../loading-state";
import { ContextDownloadModal } from "./context-modal";
import { CATEGORY_DETAIL } from "./data";
import { ManualEntries } from "./manual-entries";
import styles from "./category.module.css";

const BOOKS = CATEGORY_DETAIL.books;

function accentVar(): CSSProperties {
  return { "--catAccent": BOOKS.accent } as CSSProperties;
}

function mcpPreview(): string {
  return [
    "// Tu IA descubre y llama la herramienta",
    'ethos.context({ tool: "books.*", ask: "qué estoy leyendo" })',
    "",
    "→ 200 OK · contexto acotado servido en vivo",
    "  { provider, summary, currently_reading, top_authors, recent_reads }",
  ].join("\n");
}

function Header({ actions }: { actions?: ReactNode }) {
  return (
    <div className={styles.header}>
      <span className={styles.headerIcon}>L</span>
      <div className={styles.headerBody}>
        <h2 className={styles.headerName}>Libros</h2>
        <div className={styles.headerBlurb}>{BOOKS.blurb}</div>
      </div>
      {actions && <div className={styles.headerActions}>{actions}</div>}
    </div>
  );
}

function CurrentlyReading({ summary }: { summary: BooksSummary }) {
  if (summary.currently_reading.length === 0) return null;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>Leyendo ahora</div>
      {summary.currently_reading.map((book) => (
        <div key={book.title} className={styles.recentRow}>
          <span className={styles.recentDot} />
          <div className={styles.recentBody}>
            <div className={styles.recentName}>{book.title}</div>
            <div className={styles.recentSub}>{book.author}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function TopAuthors({ summary }: { summary: BooksSummary }) {
  if (summary.top_authors.length === 0) return null;
  const max = summary.top_authors[0]?.books || 1;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>Autores más leídos</div>
      {summary.top_authors.map((author, i) => (
        <div key={author.name} className={styles.topRow}>
          <div className={styles.rank}>{i + 1}</div>
          <div className={styles.topBody}>
            <div className={styles.topHead}>
              <span className={styles.topName}>{author.name}</span>
              <span className={styles.topValue}>
                {author.books} {author.books === 1 ? "libro" : "libros"}
              </span>
            </div>
            <div className={styles.topBar}>
              <div
                className={styles.topBarFill}
                style={{ width: `${Math.round((author.books / max) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function RecentReads({ summary }: { summary: BooksSummary }) {
  if (summary.recent_reads.length === 0) return null;
  return (
    <div className={styles.section}>
      <div className={styles.eyebrow}>Últimas lecturas</div>
      {summary.recent_reads.map((read) => (
        <div key={read.title} className={styles.recentRow}>
          <span className={styles.recentDot} />
          <div className={styles.recentBody}>
            <div className={styles.recentName}>{read.title}</div>
            <div className={styles.recentSub}>
              {read.author}
              {read.rating != null ? ` · ${read.rating}/100` : ""}
            </div>
          </div>
          <span className={styles.recentTime}>{relativeTime(read.finished_at)}</span>
        </div>
      ))}
    </div>
  );
}

function ConnectedView({
  source,
  summary,
  onImported,
}: {
  source: BooksSource;
  summary: BooksSummary;
  onImported: () => void;
}) {
  const [modalOpen, setModalOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);

  const stats = [
    { value: fmtInt(summary.pages_read), label: "páginas leídas" },
    { value: fmtInt(summary.currently_reading.length), label: "leyendo ahora" },
    { value: fmtInt(summary.wishlisted), label: "por leer" },
  ];

  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>

      <Header
        actions={
          <>
            <button
              type="button"
              className={styles.btnGhost}
              onClick={() => setImportOpen((v) => !v)}
            >
              Volver a importar
            </button>
            <button type="button" className={styles.btnPrimary} onClick={() => setModalOpen(true)}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 3v11m0 0 4-4m-4 4-4-4" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M5 19h14" strokeLinecap="round" />
              </svg>
              Descargar contexto
            </button>
          </>
        }
      />

      <div className={styles.strip}>
        <span className={styles.stripItem}>
          <span className={`${styles.healthDot} ${styles.healthOk}`} />
          <span className={styles.stripStrong}>Operativa</span>
        </span>
        <span className={styles.stripSep} />
        <span className={styles.stripItem}>
          Proveedor <span className={styles.provider}>Goodreads</span>
        </span>
        <span className={styles.stripItem}>
          Modo <span className={styles.stripStrong}>Import · manual</span>
        </span>
        <span className={styles.stripGrow} />
        <span className={styles.stripItem}>
          Importado {relativeTime(source.synced_at)}
        </span>
      </div>

      {importOpen && (
        <div className={styles.section}>
          <div className={styles.eyebrow}>Actualizar tus libros</div>
          <p className={styles.recentSub} style={{ marginBottom: "12px" }}>
            El refresco de un import es volver a subir el export: reemplaza tus
            libros con el archivo nuevo.
          </p>
          <ImportPanel
            className={styles.btnPrimary}
            onImported={() => {
              setImportOpen(false);
              onImported();
            }}
          />
        </div>
      )}

      <div className={styles.statBand}>
        <div className={styles.statHero}>
          <div>
            <div className={styles.heroValue}>{fmtInt(summary.books_read)}</div>
            <div className={styles.heroLabel}>libros leídos</div>
          </div>
        </div>
        <div className={styles.statGrid}>
          {stats.map((stat) => (
            <div key={stat.label} className={styles.statCell}>
              <div className={styles.statValue}>{stat.value}</div>
              <div className={styles.statLabel}>{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      <CurrentlyReading summary={summary} />
      <TopAuthors summary={summary} />
      <RecentReads summary={summary} />
      <ManualEntries slug="books" accent={BOOKS.accent} onChange={onImported} />

      {modalOpen && (
        <ContextDownloadModal
          slug="books"
          mcpPreview={mcpPreview()}
          onClose={() => setModalOpen(false)}
        />
      )}
    </div>
  );
}

function ImportView({ onImported }: { onImported: () => void }) {
  return (
    <div className="eth-screen" style={accentVar()}>
      <Link href="/app" className={styles.back}>
        ← Inicio
      </Link>
      <Header />
      <div className={styles.soon}>
        <div className={styles.soonTitle}>Sube tus libros</div>
        <p className={styles.soonNote}>
          Goodreads no tiene API pública: exporta tu biblioteca y súbela aquí.
          Leemos el CSV, lo normalizamos y tu IA podrá consultarlo.
        </p>
        <div style={{ marginTop: "20px" }}>
          <ImportPanel className={styles.btnPrimary} onImported={onImported} />
        </div>
      </div>
    </div>
  );
}

export function BooksDetail() {
  const { loading, source, error, reload, silentReload } = useBooksSource();

  if (loading) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <LoadingState label="Cargando tus libros…" />
      </div>
    );
  }

  if (error || !source) {
    return (
      <div className="eth-screen">
        <Link href="/app" className={styles.back}>
          ← Inicio
        </Link>
        <p className={styles.headerBlurb}>
          No se pudo cargar tus libros. Inténtalo de nuevo más tarde.
        </p>
      </div>
    );
  }

  // silentReload: reimportar o editar entradas sustituye las cifras en sitio,
  // sin volver a pasar por la pantalla de carga. El primer import sí usa
  // reload: la transición a la vista conectada necesita su estado de carga.
  if (source.state === "fresh" && source.summary) {
    return <ConnectedView source={source} summary={source.summary} onImported={silentReload} />;
  }
  return <ImportView onImported={reload} />;
}
