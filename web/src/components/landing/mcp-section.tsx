import { Logo } from "@/components/logo";
import { MCP_POINTS } from "./data";
import styles from "./landing.module.css";

export function McpSection() {
  return (
    <section id="mcp" className={`eth-reveal ${styles.mcpSection}`}>
      <div className={styles.mcpIntro}>
        <div className={styles.mcpEyebrow}>El puente · MCP</div>
        <h2 className={styles.h2}>¿Qué es un MCP y por qué te interesa?</h2>
        <p className={styles.lead}>
          MCP (<em className={styles.leadStrong}>Model Context Protocol</em>)
          es un estándar abierto que deja que tu IA —Claude y otras— se conecte
          a una fuente de datos y le pida información cuando la necesita, en
          vez de que tú se la pegues a mano.{" "}
          <strong className={styles.leadStrong}>
            Ethos es tu servidor MCP:
          </strong>{" "}
          habla ese idioma para que tu IA consulte tu perfil directamente.
        </p>
      </div>

      {/* Diagrama: tu IA ↔ Ethos vía protocolo MCP */}
      <div className={styles.mcpDiagram}>
        <div className={styles.diagNode}>
          <span className={styles.diagIconAi}>
            <Logo width={26} height={24} withPath={false} />
          </span>
          <div className={styles.diagTitle}>Tu IA</div>
          <div className={styles.diagMeta}>Claude · ChatGPT · etc.</div>
        </div>

        <div className={styles.linkCol}>
          <div>
            <div className={styles.linkLabel}>Tu IA pide</div>
            <div className={styles.linkRow}>
              <div className={styles.dashTrack}>
                <span className={styles.dashDotReq} />
              </div>
              <span className={styles.reqChip}>ethos.juegos</span>
            </div>
          </div>
          <div className={styles.protoLabel}>protocolo MCP</div>
          <div>
            <div className={`${styles.linkLabel} ${styles.linkLabelRight}`}>
              Ethos responde
            </div>
            <div className={`${styles.linkRow} ${styles.linkRowReverse}`}>
              <div className={styles.dashTrack}>
                <span className={styles.dashDotRes} />
              </div>
              <span className={styles.resChip}>124 juegos · 2,4 kB</span>
            </div>
          </div>
        </div>

        <div className={styles.diagNode}>
          <span className={styles.diagIconEthos}>
            <Logo width={30} height={26} withPath={false} />
          </span>
          <div className={styles.diagTitle}>Ethos</div>
          <div className={styles.diagMeta}>tu perfil · servidor MCP</div>
        </div>
      </div>

      <div className={styles.mcpPoints}>
        {MCP_POINTS.map((point) => (
          <div key={point.k} className={styles.pointCard}>
            <div className={styles.pointK}>{point.k}</div>
            <div className={styles.pointT}>{point.t}</div>
            <p className={styles.pointD}>{point.d}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
