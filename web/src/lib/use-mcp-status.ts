"use client";

import { getMcpStatus, type McpStatus } from "@/lib/api";
import { useSource } from "@/lib/use-source";

export type McpStatusState = {
  loading: boolean;
  status: McpStatus | null;
  error: boolean;
  reload: () => void;
};

// Estado real de la conexión del MCP, compartido por Inicio, la sidebar y
// Conectar IA (misma caché de useSource: una petición por sesión de vista).
export function useMcpStatus(): McpStatusState {
  const { loading, data, error, reload } = useSource(getMcpStatus);
  return { loading, status: data, error, reload };
}

// Conectada si hay un cliente OAuth autorizado o un token manual emitido.
export function isMcpConnected(status: McpStatus | null): boolean {
  return !!status && (status.oauth_connected || status.token_issued);
}
