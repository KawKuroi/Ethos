-- Migración 0009: uso del MCP por usuario (estadísticas de Conectar IA)
-- Contador de llamadas por tool: cada llamada autenticada a una tool del MCP
-- incrementa su fila. Solo el backend (service_role) escribe/lee; RLS
-- habilitada sin políticas públicas, como el resto de tablas del MCP.

create table if not exists public.mcp_usage (
    user_id uuid not null references auth.users (id) on delete cascade,
    tool text not null,
    calls integer not null default 0,
    last_called_at timestamptz not null default now(),
    primary key (user_id, tool)
);

comment on table public.mcp_usage is 'Llamadas a tools del MCP por usuario (estadísticas de Conectar IA).';

alter table public.mcp_usage enable row level security;
