"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";

import { Logo } from "@/components/logo";
import { WALK_STEPS } from "./data";
import styles from "./landing.module.css";

const AUTOPLAY_MS = 4200;

// Recorrido de Juegos en 4 pasos: rail con autoplay en bucle + escenario con
// paneles superpuestos que se funden (como el prototipo).
export function Walkthrough() {
  const [active, setActive] = useState(0);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const startLoop = useCallback(() => {
    if (timer.current) clearInterval(timer.current);
    timer.current = setInterval(
      () => setActive((current) => (current + 1) % WALK_STEPS.length),
      AUTOPLAY_MS,
    );
  }, []);

  useEffect(() => {
    startLoop();
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [startLoop]);

  const goTo = (index: number) => {
    setActive(index);
    startLoop();
  };

  const panelClass = (index: number) =>
    `${styles.panel} ${active === index ? styles.panelOn : ""}`;

  return (
    <div className={styles.walkGrid}>
      {/* Rail de pasos */}
      <div className={styles.rail}>
        {WALK_STEPS.map((step, index) => (
          <button
            key={step.title}
            type="button"
            onClick={() => goTo(index)}
            className={`${styles.railBtn} ${
              active === index ? styles.railBtnOn : ""
            }`}
          >
            <div className={styles.railHead}>
              <span className={styles.railNum}>{index + 1}</span>
              <span className={styles.railTitle}>{step.title}</span>
            </div>
            <p className={styles.railSub}>{step.sub}</p>
            <div className={styles.railTrack}>
              {/* key reinicia la animación de progreso al reactivarse */}
              <div key={active === index ? "on" : "off"} className={styles.railFill} />
            </div>
          </button>
        ))}
        <div className={styles.loopNote}>
          <span className={styles.loopDot} />
          Reproduciendo en bucle
        </div>
      </div>

      {/* Escenario */}
      <div className={styles.stage}>
        {/* Paso 1 — conectas la fuente */}
        <div className={panelClass(0)} data-testid="walk-panel-0">
          <div className={styles.panelPad}>
            <div className={styles.srcHead}>
              <div className={styles.srcId}>
                <span className={styles.srcBadge}>S</span>
                <div>
                  <div className={styles.srcTitle}>Steam</div>
                  <div className={styles.srcMeta}>cuenta conectada</div>
                </div>
              </div>
              <div className={styles.syncBadge}>
                <span className={styles.syncDot} />
                <span className={styles.syncLabel}>Sincronizado</span>
              </div>
            </div>
            <div className={styles.panelNote}>
              Ethos importa tu actividad tal cual la guarda Steam:
            </div>
            <div className={styles.codeBox}>
              <div className={styles.codeHead}>
                GET /player/owned-games&nbsp;&nbsp;→&nbsp;&nbsp;
                <span className={styles.codeHeadAccent}>
                  124 juegos · 1.840 h
                </span>
              </div>
              <div className={styles.codeRow}>
                <span>Elden Ring</span>
                <span className={styles.codeDim}>96 h · 38/42 logros</span>
              </div>
              <div className={styles.codeRow}>
                <span>Hollow Knight</span>
                <span className={styles.codeDim}>42 h · 24/63 logros</span>
              </div>
              <div className={styles.codeRow}>
                <span>Hades</span>
                <span className={styles.codeDim}>31 h · 49/49 logros</span>
              </div>
              <div className={`${styles.codeRow} ${styles.codeDim}`}>
                <span>
                  + 121 más
                  <span className={styles.cursor} />
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Paso 2 — Ethos la normaliza */}
        <div className={panelClass(1)} data-testid="walk-panel-1">
          <div className={styles.panelPad}>
            <div className={styles.panelNote}>
              Ethos traduce los campos de Steam a un{" "}
              <strong className={styles.panelNoteStrong}>esquema común</strong>
              , igual para toda fuente:
            </div>
            <div className={styles.normGrid}>
              <div className={styles.rawBox}>
                <div className={styles.boxLabel}>crudo · Steam</div>
                <div className={styles.rawRow}>appid: 1245620</div>
                <div className={styles.rawRow}>playtime_forever: 5760</div>
                <div className={styles.rawRow}>achievements: 38</div>
                <div className={styles.rawRow}>name: &quot;Elden Ring&quot;</div>
              </div>
              <div className={styles.normArrow}>→</div>
              <div className={styles.normBox}>
                <div className={styles.scan} />
                <div className={styles.normLabel}>ethos.juegos</div>
                <div className={styles.normRow}>
                  <span className={styles.codeDim}>titulo:</span> &quot;Elden
                  Ring&quot;
                </div>
                <div className={styles.normRow}>
                  <span className={styles.codeDim}>horas:</span> 96
                </div>
                <div className={styles.normRow}>
                  <span className={styles.codeDim}>logros:</span> 38
                </div>
                <div className={styles.normRow}>
                  <span className={styles.codeDim}>plataforma:</span>{" "}
                  &quot;Steam&quot;
                </div>
              </div>
            </div>
            <div className={styles.normNote}>
              <span className={styles.accDot} />
              minutos → horas · ids → títulos · mismo formato que PlayStation,
              GOG, Xbox…
            </div>
          </div>
        </div>

        {/* Paso 3 — queda como categoría */}
        <div className={panelClass(2)} data-testid="walk-panel-2">
          <div className={styles.panelPad}>
            <div className={styles.catHead}>
              <div className={styles.catId}>
                <span className={styles.catBadge}>J</span>
                <div>
                  <div className={styles.catTitle}>Juegos</div>
                  <div className={styles.catMeta}>
                    <span className={styles.okDot} />
                    actualizado hoy · Steam + PlayStation
                  </div>
                </div>
              </div>
              <span className={styles.catChip}>en tu perfil</span>
            </div>
            <div className={styles.statTri}>
              <div className={styles.statCard}>
                <div className={styles.statRule} />
                <div className={styles.statVal}>1.840</div>
                <div className={styles.statLabel}>horas</div>
              </div>
              <div className={styles.statCard}>
                <div className={`${styles.statRule} ${styles.statRule70}`} />
                <div className={styles.statVal}>124</div>
                <div className={styles.statLabel}>juegos</div>
              </div>
              <div className={styles.statCard}>
                <div className={`${styles.statRule} ${styles.statRule45}`} />
                <div className={styles.statVal}>312</div>
                <div className={styles.statLabel}>logros</div>
              </div>
            </div>
            <div className={styles.topLabel}>Más jugados</div>
            <div className={styles.topRows}>
              <div className={styles.topRow}>
                <span className={`${styles.topRank} ${styles.topRankFirst}`}>
                  1
                </span>
                <span className={styles.topName}>Elden Ring</span>
                <div className={styles.topTrack}>
                  <div
                    className={styles.topFill}
                    style={
                      { "--w": "100%", background: "var(--acc)" } as CSSProperties
                    }
                  />
                </div>
                <span className={`${styles.topVal} ${styles.topValFirst}`}>
                  96 h
                </span>
              </div>
              <div className={styles.topRow}>
                <span className={styles.topRank}>2</span>
                <span className={styles.topName}>Hollow Knight</span>
                <div className={styles.topTrack}>
                  <div
                    className={styles.topFill}
                    style={
                      {
                        "--w": "44%",
                        background:
                          "color-mix(in oklab, var(--acc) 72%, #fff)",
                      } as CSSProperties
                    }
                  />
                </div>
                <span className={styles.topVal}>42 h</span>
              </div>
              <div className={styles.topRow}>
                <span className={styles.topRank}>3</span>
                <span className={styles.topName}>Hades</span>
                <div className={styles.topTrack}>
                  <div
                    className={styles.topFill}
                    style={
                      {
                        "--w": "32%",
                        background:
                          "color-mix(in oklab, var(--acc) 55%, #fff)",
                      } as CSSProperties
                    }
                  />
                </div>
                <span className={styles.topVal}>31 h</span>
              </div>
            </div>
          </div>
        </div>

        {/* Paso 4 — tu IA la usa */}
        <div className={panelClass(3)} data-testid="walk-panel-3">
          <div className={styles.panelChat}>
            <div className={styles.userMsg}>¿A qué he jugado más este año?</div>
            <div className={styles.mcpChip}>
              <span className={styles.accDot} />
              MCP lee <span className={styles.mcpChipTool}>ethos.juegos</span>
              <span className={styles.kbChip}>2,4 kB</span>
            </div>
            <div className={styles.aiAnswerRow}>
              <span className={styles.aiAvatarSmall}>
                <Logo width={15} height={15} withPath={false} />
              </span>
              <div className={styles.aiAnswer}>
                Sobre todo <strong>Elden Ring</strong> (96 h). Después Hollow
                Knight (42 h) y Hades (31 h). En total llevas{" "}
                <strong>1.840 h</strong> en 124 juegos este año.
                <span className={styles.answerCursor} />
              </div>
            </div>
            <div className={styles.privacyNote}>
              <svg
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#2f9e6b"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ flex: "0 0 auto" }}
              >
                <path d="M12 2 L20 6 V11 C20 16 16.5 20 12 22 C7.5 20 4 16 4 11 V6 Z" />
                <path d="M9 12 l2 2 l4 -4" />
              </svg>
              <span>
                Tu IA recibió{" "}
                <strong className={styles.privacyStrong}>
                  solo tus juegos
                </strong>{" "}
                — no tu música, tus libros ni tu ubicación.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
