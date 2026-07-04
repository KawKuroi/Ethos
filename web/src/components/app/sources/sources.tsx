"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import type { GamesSource } from "@/lib/api";
import { useGamesSource } from "@/lib/use-games-source";
import { CATEGORY_DETAIL, type CategoryDetailData } from "../category/data";
import styles from "./sources.module.css";

function accentVar(accent: string): CSSProperties {
  return { "--catAccent": accent } as CSSProperties;
}

const GAMES = CATEGORY_DETAIL.games;
const SOON = Object.values(CATEGORY_DETAIL).filter((c) => c.state === "soon");

function isLiveState(source: GamesSource | null): boolean {
  return source?.state === "fresh" || source?.state === "syncing";
}

function GamesLiveCard({ source }: { source: GamesSource }) {
  const syncing = source.state === "syncing";
  const games = source.summary?.games ?? 0;
  return (
    <Link
      href={`/app/categoria/${GAMES.slug}`}
      className={styles.card}
      style={accentVar(GAMES.accent)}
    >
      <span className={styles.cardIcon}>{GAMES.name.charAt(0)}</span>
      <div className={styles.cardBody}>
        <div className={styles.cardTitleRow}>
          <span className={styles.cardName}>{GAMES.name}</span>
          <span className={`${styles.healthDot} ${styles.healthOk}`} />
        </div>
        <div className={styles.cardMeta}>
          {GAMES.provider} · API · {syncing ? "sincronizando…" : `${games} juegos`}
        </div>
      </div>
      <span className={styles.cardCta}>Abrir →</span>
    </Link>
  );
}

function GamesOffCard() {
  return (
    <Link
      href={`/app/categoria/${GAMES.slug}`}
      className={styles.card}
      style={accentVar(GAMES.accent)}
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
            {GAMES.name}
          </span>
          <span className={styles.groupDotOff} />
        </div>
        <div className={styles.cardMeta}>{GAMES.provider} · API · sin empezar</div>
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
  const { loading, source } = useGamesSource();
  const live = isLiveState(source);
  const off = !loading && !live;

  const summary = [
    { value: live ? "1" : "0", label: "activas" },
    { value: live ? "1" : "0", label: "expuestas por MCP" },
    { value: off ? "1" : "0", label: "apagadas" },
    { value: String(SOON.length), label: "en desarrollo" },
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
        <div className={styles.loading}>Cargando tus fuentes…</div>
      ) : (
        <>
          {live && source && (
            <>
              <div className={styles.groupHead}>
                <span className={styles.groupDotLive} />
                <div className={styles.groupTitle}>Activas</div>
                <div className={styles.groupLine} />
                <span className={styles.groupCount}>1</span>
              </div>
              <div className={styles.grid}>
                <GamesLiveCard source={source} />
              </div>
            </>
          )}

          {off && (
            <>
              <div className={styles.groupHead}>
                <span className={styles.groupDotOff} />
                <div className={styles.groupTitle}>Apagadas · sin empezar</div>
                <div className={styles.groupLine} />
                <span className={styles.groupCount}>1</span>
              </div>
              <p className={styles.groupNote}>
                Existen en tu perfil pero todavía no tienen datos. Conéctalas
                cuando quieras.
              </p>
              <div className={styles.grid}>
                <GamesOffCard />
              </div>
            </>
          )}
        </>
      )}

      <div className={`${styles.groupHead} ${styles.groupHeadSpaced}`}>
        <span className={styles.groupDotSoon} />
        <div className={styles.groupTitle}>En desarrollo · próximamente</div>
        <div className={styles.groupLine} />
        <span className={styles.groupCount}>{SOON.length}</span>
      </div>
      <p className={styles.groupNote}>
        Estamos construyendo estos conectores. Todavía no se pueden activar, pero
        llegarán pronto.
      </p>
      <div className={styles.grid}>
        {SOON.map((category) => (
          <SoonCard key={category.slug} category={category} />
        ))}
      </div>
    </div>
  );
}
