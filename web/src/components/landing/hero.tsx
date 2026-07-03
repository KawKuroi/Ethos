import Link from "next/link";
import type { CSSProperties } from "react";

import { Logo } from "@/components/logo";
import { CATS, HERO_SOURCES } from "./data";
import styles from "./landing.module.css";

export function Hero() {
  return (
    <section className={styles.hero}>
      <div>
        <div className={styles.eyebrow}>Tu panel · y el contexto de tu IA</div>
        <h1 className={styles.heroTitle}>
          Reúne lo que te gusta y
          <br />
          Dáselo a tu <span className={styles.heroTitleAccent}>IA</span>
        </h1>
        <p className={styles.heroSub}>
          Conectate con tus apps, extrae la información, mira estadísticas y
          deja que tu IA lo consulte como contexto.
        </p>
        <div className={styles.heroCtas}>
          <Link href="/auth" className={styles.ctaPrimary}>
            Abrir la app →
          </Link>
          <a href="#mcp" className={styles.ctaGhost}>
            ¿Qué es un MCP?
          </a>
        </div>
      </div>

      {/* Flujo: tus apps → Ethos → tu IA */}
      <div className={styles.flowCard}>
        <div className={styles.flowLabel}>Reúne de tus apps</div>
        <div className={styles.sourcePills}>
          {HERO_SOURCES.map((source) => (
            <div
              key={source.name}
              className={styles.sourcePill}
              style={{ "--ca": source.accent } as CSSProperties}
            >
              <span className={styles.sourceInitial}>{source.initial}</span>
              <span className={styles.sourceName}>{source.name}</span>
            </div>
          ))}
          <div className={styles.morePill}>+4 más</div>
        </div>

        <div className={styles.connector}>
          <span className={styles.connectorDot} />
        </div>

        <div className={styles.hubCard}>
          <span style={{ width: 36, height: 32, color: "var(--ink)" }}>
            <Logo />
          </span>
          <div className={styles.hubBody}>
            <div className={styles.hubTitle}>Ethos · tu perfil</div>
            <div className={styles.hubMeta}>
              {CATS.length} categorías, normalizadas y al día
            </div>
          </div>
          <span className={styles.hubChip}>servidor MCP</span>
        </div>

        <div className={styles.connector}>
          <span
            className={`${styles.connectorDot} ${styles.connectorDotDelayed}`}
          />
        </div>

        <div className={styles.aiRow}>
          <span className={styles.aiAvatar}>
            <Logo width={16} height={16} withPath={false} />
          </span>
          <div className={styles.aiBubble}>
            <div className={styles.aiBubbleLabel}>
              Tu IA pregunta a Ethos, no a ti
            </div>
            <div className={styles.aiBubbleText}>
              Este año has jugado <strong>1.840 h</strong> — sobre todo Elden
              Ring.{" "}
              <span className={styles.aiBubbleDim}>
                Leí solo tus juegos: 2,4&nbsp;kB.
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
