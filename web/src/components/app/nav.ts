// Navegación y metadatos de pantalla del shell de la app (design.md §2).
import { CATEGORY_DETAIL } from "./category/data";

export type NavId = "overview" | "sources" | "mcp" | "help";

export type NavItem = {
  id: NavId;
  label: string;
  href: string;
  icon: "grid" | "nodes" | "star" | "help";
};

export const NAV: NavItem[] = [
  { id: "overview", label: "Inicio", href: "/app", icon: "grid" },
  { id: "sources", label: "Fuentes", href: "/app/fuentes", icon: "nodes" },
  { id: "mcp", label: "Conectar IA", href: "/app/conectar-ia", icon: "star" },
  { id: "help", label: "Ayuda", href: "/app/ayuda", icon: "help" },
];

// Título y subtítulo del header por ruta (textos del diseño).
export const SCREEN_META: Record<string, { title: string; sub: string }> = {
  "/app": { title: "Tu perfil", sub: "El gusto, reunido y normalizado" },
  "/app/fuentes": {
    title: "Fuentes",
    sub: "Contexto por categoría · para descargar o servir por MCP",
  },
  "/app/conectar-ia": {
    title: "Conectar IA",
    sub: "Entrega tu perfil vía servidor MCP",
  },
  "/app/ayuda": {
    title: "Ayuda",
    sub: "Qué es Ethos y qué hace con tu contexto",
  },
  "/app/ajustes": {
    title: "Ajustes",
    sub: "Personaliza tu experiencia en Ethos",
  },
};

export const DEFAULT_META = { title: "Ethos", sub: "" };

const CATEGORY_PREFIX = "/app/categoria/";

export function metaForPath(pathname: string): { title: string; sub: string } {
  const exact = SCREEN_META[pathname];
  if (exact) return exact;
  if (pathname.startsWith(CATEGORY_PREFIX)) {
    const slug = pathname.slice(CATEGORY_PREFIX.length);
    const category = CATEGORY_DETAIL[slug];
    if (category) {
      return { title: category.name, sub: "Fuente de contexto para tu IA" };
    }
  }
  return DEFAULT_META;
}
