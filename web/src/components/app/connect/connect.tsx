"use client";

import { useRef, useState } from "react";
import { getMcpStatus, issueMcpToken, mcpEndpoint } from "@/lib/api";
import { useSource } from "@/lib/use-source";
import { MCP_QUERIES, clientGuides, matchQuery, type McpQuery } from "./data";
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
  // Estado real de la conexión (¿hay clientes OAuth autorizados?).
  const {
    loading: checking,
    data: status,
    error: statusError,
    reload: checkStatus,
  } = useSource(getMcpStatus);
  const [activeGuide, setActiveGuide] = useState("claude");
  const [copied, setCopied] = useState<"endpoint" | "token" | "command" | null>(null);
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

  function copy(field: "endpoint" | "token" | "command", value: string) {
    navigator.clipboard?.writeText(value).catch(() => {});
    setCopied(field);
    setTimeout(() => setCopied(null), 1500);
  }

  const connected = status?.oauth_connected ?? false;
  const guides = clientGuides(endpoint);
  const guide = guides.find((g) => g.id === activeGuide) ?? guides[0];

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
              ? "Hay al menos un cliente autorizado que puede consultar tu perfil vía MCP."
              : statusError
                ? "No se pudo comprobar el estado. Inténtalo de nuevo en unos segundos."
                : status?.token_issued
                  ? "Tienes un token manual generado. Si tu cliente soporta OAuth, los dos pasos de abajo son más simples."
                  : "Sigue los dos pasos de abajo: conectar tarda menos de un minuto."}
          </div>
        </div>
        <button
          type="button"
          className={styles.statusBtn}
          onClick={checkStatus}
          disabled={checking}
        >
          {checking ? "Comprobando…" : "Comprobar conexión"}
        </button>
      </div>

      <div className={`${styles.card} ${styles.connectCard}`}>
        <div className={styles.eyebrow}>Conecta tu cliente</div>
        <div className={styles.fieldGap}>
          <div className={styles.fieldLabel}>1 · Copia la URL del servidor MCP</div>
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
          <div className={styles.fieldLabel}>
            2 · Añádela en tu cliente y autoriza el acceso
          </div>
          <div className={styles.tabs} role="tablist" aria-label="Elige tu cliente">
            {guides.map((g) => (
              <button
                key={g.id}
                type="button"
                role="tab"
                aria-selected={g.id === guide.id}
                className={`${styles.tab} ${g.id === guide.id ? styles.tabActive : ""}`}
                onClick={() => setActiveGuide(g.id)}
              >
                {g.name}
              </button>
            ))}
          </div>
          <div>
            {guide.steps.map((text, index) => (
              <div key={text} className={styles.step}>
                <span className={styles.stepNum}>{index + 1}</span>
                <div className={styles.stepText}>{text}</div>
              </div>
            ))}
          </div>
          {guide.command && (
            <div className={styles.cmdBox}>
              <pre className={styles.cmdCode}>{guide.command}</pre>
              {copied === "command" ? (
                <span className={styles.copied}>copiado ✓</span>
              ) : (
                <button
                  type="button"
                  className={styles.copyBtn}
                  onClick={() => copy("command", guide.command ?? "")}
                >
                  copiar
                </button>
              )}
            </div>
          )}
          {guide.note && <div className={styles.note}>{guide.note}</div>}
          <div className={styles.note}>
            Al conectar, tu cliente te traerá a una página de Ethos para autorizar
            el acceso con tu cuenta — sin tokens ni configuración extra. Cuando
            termines, vuelve aquí y pulsa «Comprobar conexión».
          </div>
        </div>
      </div>

      <div className={styles.grid2}>
        <div className={styles.card}>
          <div className={styles.eyebrow}>Qué puede hacer tu IA</div>
          <div className={styles.step}>
            <span className={styles.stepNum}>✓</span>
            <div className={styles.stepText}>
              Solo lectura: consulta tu gusto con tools acotadas (
              <code className={styles.inlineCode}>games_summary</code>,{" "}
              <code className={styles.inlineCode}>music_top_artists</code>…), nunca
              modifica nada.
            </div>
          </div>
          <div className={styles.step}>
            <span className={styles.stepNum}>✓</span>
            <div className={styles.stepText}>
              Solo viaja lo necesario: cada respuesta reporta los KB servidos frente
              al contexto total de tu perfil.
            </div>
          </div>
          <div className={styles.step}>
            <span className={styles.stepNum}>✓</span>
            <div className={styles.stepText}>
              Revocable cuando quieras: desconecta el conector desde tu cliente o
              regenera el token manual para invalidar el anterior.
            </div>
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.eyebrow}>Avanzado · token manual</div>
          <div className={styles.note} style={{ marginTop: 0, marginBottom: 12 }}>
            Solo para clientes sin soporte OAuth: genera un token y envíalo en la
            cabecera <code className={styles.inlineCode}>Authorization: Bearer …</code>.
          </div>
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
                  : "Generar uno nuevo invalida el anterior. Cifrado en reposo; nunca se reenvía a las APIs de origen."}
              </div>
            </>
          )}
        </div>
      </div>

      <div className={styles.playHead}>
        <div className={styles.playTitle}>Pruébalo: así consulta tu IA</div>
        <div className={styles.playSub}>
          Escríbele en el chat o toca una sugerencia. A la izquierda respondes en
          lenguaje natural; a la derecha ves lo que ocurre por detrás.
        </div>
        <div className={styles.playNotice} role="note">
          Demostración con <strong>datos de ejemplo</strong>: este playground no
          consulta tu perfil real ni usa un modelo de IA — enseña cómo fluye una
          consulta cuando conectas tu propio cliente MCP.
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
                    Soy un ejemplo: te enseño cómo respondería tu IA usando una
                    tool acotada, con datos de muestra. Prueba con una de estas —
                    o escribe la tuya abajo:
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
