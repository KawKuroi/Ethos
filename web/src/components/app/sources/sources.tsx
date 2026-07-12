"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { useActiveSources, type ActiveSourceView } from "@/lib/use-active-sources";
import { CATEGORY_DETAIL, type CategoryDetailData } from "../category/data";
import { LoadingState } from "../loading-state";
import styles from "./sources.module.css";

function accentVar(accent: string): CSSProperties {
  return { "--catAccent": accent } as CSSProperties;
}

// Categorías del catálogo aún sin conector (ninguna con la Fase 3 completa).
const SOON = Object.values(CATEGORY_DETAIL).filter((c) => c.state === "soon");

// Aviso de que la categoría admite más proveedores además del mostrado, sin
// tener que abrir el detalle.
function MoreProviders({ names }: { names: string[] }) {
  if (names.length <= 1) return null;
  return (
    <span
      className={styles.cardMore}
      title={`${names.length} proveedores disponibles: ${names.join(", ")}`}
    >
      +{names.length - 1}
    </span>
  );
}

function LiveCard({ view }: { view: ActiveSourceView }) {
  return (
    <Link
      href={`/app/categoria/${view.slug}`}
      className={styles.card}
      style={accentVar(view.accent)}
    >
      <span className={styles.cardIcon}>{view.initial}</span>
      <div className={styles.cardBody}>
        <div className={styles.cardTitleRow}>
          <span className={styles.cardName}>{view.name}</span>
          <span className={`${styles.healthDot} ${styles.healthOk}`} />
        </div>
        <div className={styles.cardMeta}>
          {view.provider}
          <MoreProviders names={view.providerNames} /> · {view.modeLabel} ·{" "}
          {view.syncing ? "sincronizando…" : view.countLabel}
        </div>
      </div>
      <span className={styles.cardCta}>Abrir →</span>
    </Link>
  );
}

function OffCard({ view }: { view: ActiveSourceView }) {
  return (
    <Link
      href={`/app/categoria/${view.slug}`}
      className={styles.card}
      style={accentVar(view.accent)}
    >
      <span className={`${styles.cardIcon} ${styles.cardIconOff}`}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 3v8.5" strokeLinecap="round" />
          <path d="M6.4 7.2a8 8 0 1 0 11.2 0" strokeLinecap="round" />
        </svg>
      </span>
      <div className={styles.cardBody}>
        <div className={styles.cardTitleRow}>
          <span className={`${styles.cardName} ${styles.cardNameSoon}`}>
            {view.name}
          </span>
          <span className={styles.groupDotOff} />
        </div>
        <div
          className={styles.cardMeta}
          title={
            view.providerNames.length > 1
              ? `Proveedores: ${view.providerNames.join(", ")}`
              : undefined
          }
        >
          {view.providerNames.length > 1
            ? `${view.providerNames.length} proveedores disponibles`
            : `${view.provider} · ${view.modeLabel}`}{" "}
          · sin empezar
        </div>
      </div>
      <span className={`${styles.cardCta} ${styles.cardCtaAccent}`}>Empezar →</span>
    </Link>
  );
}

function SoonCard({ category }: { category: CategoryDetailData }) {
  return (
    <Link
      href={`/app/categoria/${category.slug}`}
      className={`${styles.card} ${styles.cardSoon}`}
    >
      <span className={styles.cardSoonHatch} aria-hidden="true" />
      <span className={`${styles.cardIcon} ${styles.cardIconSoon}`}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="9" />
          <path d="M12 8v4l3 2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
      <div className={`${styles.cardBody} ${styles.cardBodySoon}`}>
        <div className={styles.cardTitleRow}>
          <span className={`${styles.cardName} ${styles.cardNameSoon}`}>
            {category.name}
          </span>
          <span className={styles.soonDot} />
        </div>
        <div className={styles.cardMeta}>
          {category.provider} · {category.soonEta}
        </div>
      </div>
      <span className={styles.soonChip}>Próximamente</span>
    </Link>
  );
}

export function Sources() {
  const { loading, views } = useActiveSources();

  const live = views.filter((v) => v.live);
  // Las diferidas "en desarrollo" tienen su propia sección (SOON); fuera de las
  // apagadas para no duplicarlas.
  const off = views.filter((v) => !v.live && !v.soon);

  const summary = [
    { value: String(live.length), label: "activas" },
    { value: String(live.length), label: "expuestas por MCP" },
    { value: String(loading ? 0 : off.length), label: "apagadas" },
    // Solo cuando haya categorías "en desarrollo" (ninguna por ahora).
    ...(SOON.length > 0
      ? [{ value: String(SOON.length), label: "en desarrollo" }]
      : []),
  ];

  return (
    <div className="eth-screen">
      <p className={styles.intro}>
        Cada categoría es una <strong>fuente de contexto</strong> para tu IA.
        Conéctala por <strong>API</strong> o súbela por <strong>import</strong>;
        luego descarga su contexto o exponlo en vivo por <strong>MCP</strong>.
      </p>

      <div className={styles.summary}>
        {summary.map((item) => (
          <div key={item.label} className={styles.summaryCard}>
            <div className={styles.summaryValue}>{item.value}</div>
            <div className={styles.summaryLabel}>{item.label}</div>
          </div>
        ))}
      </div>

      {loading ? (
        <LoadingState label="Cargando tus fuentes…" />
      ) : (
        <>
          {live.length > 0 && (
            <>
              <div className={styles.groupHead}>
                <span className={styles.groupDotLive} />
                <div className={styles.groupTitle}>Activas</div>
                <div className={styles.groupLine} />
                <span className={styles.groupCount}>{live.length}</span>
              </div>
              <div className={styles.grid}>
                {live.map((view) => (
                  <LiveCard key={view.slug} view={view} />
                ))}
              </div>
            </>
          )}

          {off.length > 0 && (
            <>
              <div className={styles.groupHead}>
                <span className={styles.groupDotOff} />
                <div className={styles.groupTitle}>Apagadas · sin empezar</div>
                <div className={styles.groupLine} />
                <span className={styles.groupCount}>{off.length}</span>
              </div>
              <p className={styles.groupNote}>
                Existen en tu perfil pero todavía no tienen datos. Conéctalas
                cuando quieras.
              </p>
              <div className={styles.grid}>
                {off.map((view) => (
                  <OffCard key={view.slug} view={view} />
                ))}
              </div>
            </>
          )}
        </>
      )}

      {SOON.length > 0 && (
        <>
          <div className={`${styles.groupHead} ${styles.groupHeadSpaced}`}>
            <span className={styles.groupDotSoon} />
            <div className={styles.groupTitle}>En desarrollo · próximamente</div>
            <div className={styles.groupLine} />
            <span className={styles.groupCount}>{SOON.length}</span>
          </div>
          <p className={styles.groupNote}>
            Estamos construyendo estos conectores. Todavía no se pueden activar,
            pero llegarán pronto.
          </p>
          <div className={styles.grid}>
            {SOON.map((category) => (
              <SoonCard key={category.slug} category={category} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
