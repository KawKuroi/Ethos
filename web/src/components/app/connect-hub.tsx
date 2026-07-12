"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import { connectSource } from "@/lib/api";
import {
  providersFor,
  providerName,
  type CategoryProvider,
} from "./category/providers";
import { ConnectUsernameForm } from "./connect-username";
import { ImportPanel } from "./import-panel";

// Selector de proveedor por categoría (D62): lista las fuentes disponibles y,
// según el proveedor elegido, muestra su guía paso a paso (con enlaces) y el
// alta que corresponda: username público, token o subida del export.

const listStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "8px",
  justifyContent: "center",
};

const cardStyle = (active: boolean): CSSProperties => ({
  padding: "8px 14px",
  borderRadius: "var(--rs)",
  border: active ? "1.5px solid var(--catAccent, var(--ink))" : "1px solid var(--line)",
  background: "var(--surface)",
  color: "var(--ink)",
  fontSize: "13px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: "7px",
});

const chipStyle: CSSProperties = {
  fontSize: "10.5px",
  padding: "1.5px 7px",
  borderRadius: "999px",
  border: "1px solid var(--line)",
  color: "var(--soft)",
  textTransform: "uppercase",
  letterSpacing: "0.04em",
};

const stepsStyle: CSSProperties = {
  margin: "0 auto",
  paddingLeft: "18px",
  maxWidth: "460px",
  textAlign: "left",
  color: "var(--soft)",
  fontSize: "12.5px",
  lineHeight: 1.65,
};

function Steps({ provider }: { provider: CategoryProvider }) {
  if (provider.steps.length === 0) return null;
  return (
    <ol aria-label={`Cómo conectar ${provider.name}`} style={stepsStyle}>
      {provider.steps.map((step) => (
        <li key={step.text}>
          {step.text}
          {step.href && (
            <>
              {" "}
              <a
                href={step.href}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--catAccent, var(--ink))", textDecoration: "underline" }}
              >
                {step.linkLabel ?? step.href}
              </a>
            </>
          )}
        </li>
      ))}
    </ol>
  );
}

export function ConnectHub({
  slug,
  onConnected,
  currentProvider,
  className,
}: {
  slug: string;
  onConnected: () => void;
  // Proveedor conectado hoy (si lo hay): avisa que conectar otro reemplaza.
  currentProvider?: string | null;
  className?: string;
}) {
  const providers = providersFor(slug);
  const connectable = providers.filter((provider) => provider.kind !== "soon");
  const [selectedId, setSelectedId] = useState<string>(
    currentProvider && connectable.some((p) => p.id === currentProvider)
      ? currentProvider
      : (connectable[0]?.id ?? ""),
  );
  const selected = providers.find((provider) => provider.id === selectedId);
  const switching =
    !!currentProvider && !!selected && selected.id !== currentProvider;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div style={listStyle} role="radiogroup" aria-label="Elige tu proveedor">
        {providers.map((provider) => {
          const soon = provider.kind === "soon";
          const active = provider.id === selectedId;
          return (
            <button
              key={provider.id}
              type="button"
              role="radio"
              aria-checked={active}
              disabled={soon}
              onClick={() => setSelectedId(provider.id)}
              style={{ ...cardStyle(active), opacity: soon ? 0.55 : 1 }}
            >
              {provider.name}
              <span style={chipStyle}>
                {soon ? "pronto" : provider.mode === "api" ? "API" : "Import"}
              </span>
            </button>
          );
        })}
      </div>

      {selected && (
        <div
          style={{ display: "flex", flexDirection: "column", gap: "12px" }}
          aria-label={`Conectar ${selected.name}`}
        >
          <p style={{ margin: 0, color: "var(--soft)", fontSize: "13px" }}>
            {selected.description}
          </p>
          <Steps provider={selected} />
          {switching && (
            <p
              role="note"
              style={{
                margin: "0 auto",
                maxWidth: "460px",
                fontSize: "12.5px",
                color: "var(--warn, #b45309)",
              }}
            >
              Conectar {selected.name} reemplaza los datos actuales de{" "}
              {providerName(currentProvider)} en esta categoría; las entradas a
              mano se conservan.
            </p>
          )}
          {(selected.kind === "username" || selected.kind === "token") && (
            <ConnectUsernameForm
              className={className}
              placeholder={selected.placeholder ?? `Tu usuario de ${selected.name}`}
              ariaLabel={selected.placeholder ?? `Credencial de ${selected.name}`}
              errorText={`No se pudo conectar. Revisa tus datos de ${selected.name} e inténtalo de nuevo.`}
              connect={(secret) => connectSource(selected.id, secret)}
              onConnected={onConnected}
            />
          )}
          {selected.kind === "import" && (
            <ImportPanel
              className={className}
              accept={selected.accept}
              onImported={onConnected}
            />
          )}
        </div>
      )}
    </div>
  );
}
