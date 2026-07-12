import type { CategoryDetailData } from "./data";

function slugify(s: string): string {
  return s
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "");
}

// Preview del contexto descargable (JSON), como `ctxJson` del prototipo.
export function contextJson(c: CategoryDetailData): string {
  const J = (v: string) => JSON.stringify(v);
  const stats = c.stats ?? [];
  const top = c.top ?? [];
  const tags = c.tags ?? [];
  const sum = stats
    .slice(0, 3)
    .map((s) => `    "${slugify(s.label)}": ${J(s.value)}`)
    .join(",\n");
  const topLines = top
    .slice(0, 3)
    .map(
      (t, i) =>
        `    { "rank": ${i + 1}, "name": ${J(t.name)}, "value": ${J(t.value)}, "tag": ${J(t.sub)} }`,
    )
    .join(",\n");
  const tagLine = tags.slice(0, 4).map(J).join(", ");
  return [
    "{",
    `  "namespace": ${J(c.ns)},`,
    `  "provider": ${J(c.provider)},`,
    `  "updated": "2026-06-30T09:12Z",`,
    `  "summary": {`,
    sum,
    "  },",
    `  "${slugify(c.topTitle ?? "top")}": [`,
    topLines,
    "  ],",
    `  "tags": [${tagLine}]`,
    "}",
  ].join("\n");
}
