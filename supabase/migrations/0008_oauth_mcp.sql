-- Migración 0008: OAuth 2.1 para el MCP (D56)
-- Clientes registrados dinámicamente (RFC 7591) y tokens de acceso/refresh
-- emitidos por el authorization code flow con PKCE. Solo el backend
-- (service_role) escribe/lee; RLS habilitada sin políticas públicas. Los
-- authorization codes no se persisten (viven en memoria, expiran a 10 min).

create table if not exists public.oauth_clients (
    client_id text primary key,
    client_name text not null,
    redirect_uris jsonb not null,
    created_at timestamptz not null default now()
);

comment on table public.oauth_clients is 'Clientes OAuth del MCP, registrados dinámicamente (D56).';

create table if not exists public.oauth_tokens (
    token_hash text primary key,
    user_id uuid not null references auth.users (id) on delete cascade,
    client_id text not null,
    kind text not null check (kind in ('access', 'refresh')),
    expires_at timestamptz not null,
    created_at timestamptz not null default now()
);

comment on table public.oauth_tokens is 'Tokens OAuth del MCP (hash SHA-256), con expiración (D56).';

create index if not exists oauth_tokens_user_idx on public.oauth_tokens (user_id);
create index if not exists oauth_tokens_expiry_idx on public.oauth_tokens (expires_at);

alter table public.oauth_clients enable row level security;
alter table public.oauth_tokens enable row level security;
