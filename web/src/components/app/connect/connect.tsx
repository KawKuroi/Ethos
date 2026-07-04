"use client";

import { useRef, useState } from "react";
import { issueMcpToken, mcpEndpoint } from "@/lib/api";
import { MCP_QUERIES, STEPS, matchQuery, type McpQuery } from "./data";
import styles from "./connect.module.css";

function StarAvatar() {
  return (
    <span className={styles.aiAvatar} aria-hidden="true">
      <svg width="17" height="17" viewBox="0 0 18 18" fill="currentColor">
        <path d="M9 1.4 L10.55 6.75 L15.9 8.3 L10.55 9.85 L9 15.2 L7.45 9.85 L2.1 8.3 L7.45 6.75 Z" />
      </svg>
    </span>
  );
}

export function ConnectAi() {
  const [connected, setConnected] = useState(false);
  const [copied, setCopied] = useState<"endpoint" | "token" | null>(null);
  const [current, setCurrent] = useState<McpQuery | null>(null);
  const [running, setRunning] = useState(false);
  const [input, setInput] = useState("");
  const [endpoint] = useState(() => {
    try {
      return mcpEndpoint();
    } catch {
      return "";
    }
  });
  const [token, setToken] = useState<string | null>(null);
  const [issuing, setIssuing] = useState(false);
  const [tokenError, setTokenError] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  async function generateToken() {
    if (issuing) return;
    setTokenError(false);
    setIssuing(true);
    try {
      const issued = await issueMcpToken();
      setToken(issued.token);
    } catch {
      setTokenError(true);
    } finally {
      setIssuing(false);
    }
  }

  function ask(query: McpQuery) {
    setCurrent(query);
    setRunning(true);
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setRunning(false), 700);
  }

  function submit() {
    const text = input.trim();
    if (!text) return;
    ask(matchQuery(text));
    setInput("");
  }

  function copy(field: "endpoint" | "token", value: string) {
    navigator.clipboard?.writeText(value).catch(() => {});
    setCopied(field);
    setTimeout(() => setCopied(null), 1500);
  }

  return (
    <div className="eth-screen">
      <div className={styles.statusCard}>
        <span
          className={`${styles.statusDot} ${connected ? styles.statusOn : styles.statusOff}`}
        />
        <div className={styles.statusBody}>
          <div className={styles.statusText}>
            {connected ? "Tu IA está conectada" : "Tu IA aún no está conectada"}
          </div>
          <div className={styles.statusDesc}>
            {connected
              ? "Tu perfil está disponible para consultas acotadas vía MCP."
              : "Conecta tu cliente para que la IA pueda leer tu perfil."}
          </div>
        </div>
        <button
          type="button"
          className={styles.statusBtn}
          onClick={() => setConnected((v) => !v)}
        >
          {connected ? "Desconectar" : "Conectar IA"}
        </button>
      </div>

      <div className={styles.grid2}>
        <div className={styles.card}>
          <div className={styles.eyebrow}>Conexión del servidor</div>
          <div className={styles.fieldGap}>
            <div className={styles.fieldLabel}>Endpoint</div>
            <div className={styles.fieldBox}>
              <code className={styles.fieldCode}>{endpoint}</code>
              {copied === "endpoint" ? (
                <span className={styles.copied}>copiado ✓</span>
              ) : (
                <button
                  type="button"
                  className={styles.copyBtn}
                  onClick={() => copy("endpoint", endpoint)}
                >
                  copiar
                </button>
              )}
            </div>
          </div>
          <div>
            <div className={styles.fieldLabel}>Token de acceso</div>
            {token ? (
              <>
                <div className={styles.fieldBox}>
                  <code className={styles.fieldCode}>{token}</code>
                  {copied === "token" ? (
                    <span className={styles.copied}>copiado ✓</span>
                  ) : (
                    <button
                      type="button"
                      className={styles.copyBtn}
                      onClick={() => copy("token", token)}
                    >
                      copiar
                    </button>
                  )}
                </div>
                <div className={styles.note}>
                  Guárdalo ahora: por seguridad no se vuelve a mostrar. Cifrado en
                  reposo; nunca se reenvía a las APIs de origen.
                </div>
              </>
            ) : (
              <>
                <button
                  type="button"
                  className={styles.copyBtn}
                  style={{ padding: "9px 14px" }}
                  onClick={generateToken}
                  disabled={issuing}
                >
                  {issuing ? "Generando…" : "Generar token"}
                </button>
                <div className={styles.note}>
                  {tokenError
                    ? "No se pudo generar el token. Inténtalo de nuevo."
                    : "Genera un token para autenticar tu IA. Cifrado en reposo; nunca se reenvía a las APIs de origen."}
                </div>
              </>
            )}
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.eyebrow}>Tres pasos</div>
          {STEPS.map((step) => (
            <div key={step.n} className={styles.step}>
              <span className={styles.stepNum}>{step.n}</span>
              <div>
                <div className={styles.stepTitle}>{step.title}</div>
                <div className={styles.stepBody}>{step.body}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className={styles.playHead}>
        <div className={styles.playTitle}>Pruébalo: pregúntale a tu IA</div>
        <div className={styles.playSub}>
          Escríbele en el chat o toca una sugerencia. A la izquierda respondes en
          lenguaje natural; a la derecha ves lo que ocurre por detrás.
        </div>
      </div>

      <div className={styles.playGrid}>
        {/* Lado natural */}
        <div className={styles.panel}>
          <div className={styles.panelHead}>
            <span className={styles.panelHeadDot} />
            <span className={styles.panelHeadText}>Para ti · en lenguaje natural</span>
          </div>
          <div className={styles.chatBody}>
            {!current ? (
              <div className={styles.chatEmpty}>
                <div className={styles.aiRow}>
                  <StarAvatar />
                  <div className={styles.aiBubble}>
                    Pregúntame lo que quieras sobre tu gusto. Consulto tus fuentes
                    conectadas con una tool acotada y te respondo aquí. Prueba con
                    una de estas — o escribe la tuya abajo:
                  </div>
                </div>
                <div className={styles.chips}>
                  {MCP_QUERIES.map((query) => (
                    <button
                      key={query.id}
                      type="button"
                      className={styles.chip}
                      onClick={() => ask(query)}
                    >
                      {query.q}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <>
                <div className={styles.userRow}>
                  <div className={styles.userBubble}>{current.q}</div>
                </div>
                <div className={styles.aiRow}>
                  <StarAvatar />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    {running ? (
                      <div className={styles.typing}>
                        <span className={styles.typingDot} />
                        <span className={styles.typingDot} />
                        <span className={styles.typingDot} />
                      </div>
                    ) : (
                      <>
                        <div className={styles.answer}>{current.answer}</div>
                        {current.items.length > 0 && (
                          <div className={styles.itemList}>
                            {current.items.map((item) => (
                              <div key={item.label} className={styles.item}>
                                <div className={styles.itemBody}>
                                  <div className={styles.itemLabel}>{item.label}</div>
                                  <div className={styles.itemSub}>{item.sub}</div>
                                  {item.bar !== null && (
                                    <div className={styles.itemBar}>
                                      <div
                                        className={styles.itemBarFill}
                                        style={{ width: `${item.bar}%` }}
                                      />
                                    </div>
                                  )}
                                </div>
                                <div className={styles.itemValue}>{item.value}</div>
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
          <div className={styles.composer}>
            <div className={styles.composerBox}>
              <input
                className={styles.composerInput}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") submit();
                }}
                placeholder="Escribe tu pregunta… p. ej. ¿mis juegos con más horas?"
                aria-label="Escribe tu pregunta"
              />
              <button
                type="button"
                className={styles.sendBtn}
                onClick={submit}
                aria-label="Enviar"
              >
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M5 12h13M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        {/* Lado técnico */}
        <div className={styles.panel}>
          <div className={styles.panelHead}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--muted)" strokeWidth="1.8">
              <path d="M8 6 3 12l5 6M16 6l5 6-5 6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <span className={styles.panelHeadText}>Lo que pasa por detrás</span>
          </div>
          <div className={styles.techBody}>
            {!current ? (
              <div className={styles.techEmpty}>
                Cuando hagas una pregunta verás aquí la <strong>tool</strong> que se
                llama, cuánto contexto viaja al modelo y la respuesta{" "}
                <strong>JSON</strong> cruda.
              </div>
            ) : (
              <>
                <div>
                  <div className={styles.techLabel}>1 · Llama una tool acotada</div>
                  <div className={styles.toolRow}>
                    <span className={styles.toolDot} />
                    <code className={styles.toolName}>{current.tool}</code>
                    <code className={styles.toolArgs}>({current.args})</code>
                    <span className={styles.toolGrow} />
                    {running ? (
                      <span className={styles.toolArgs}>ejecutando…</span>
                    ) : (
                      <span className={styles.toolOk}>200 OK</span>
                    )}
                  </div>
                </div>
                <div>
                  <div className={styles.techLabel}>2 · Solo viaja lo necesario</div>
                  <div className={styles.ctxBox}>
                    <div className={styles.ctxHead}>
                      <span>
                        <span className={styles.ctxStrong}>{current.ctx}</span>{" "}
                        <span className={styles.ctxMuted}>de {current.full}</span>
                      </span>
                      <span className={styles.ctxMuted}>al modelo</span>
                    </div>
                    <div className={styles.ctxBar}>
                      <div
                        className={styles.ctxBarFill}
                        style={{ width: `${current.pct}%` }}
                      />
                    </div>
                  </div>
                </div>
                <div>
                  <div className={styles.techLabel}>3 · Respuesta cruda (JSON)</div>
                  <pre className={styles.responsePre}>{current.response}</pre>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
