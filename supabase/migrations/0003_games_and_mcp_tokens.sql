-- Migración 0003: persistencia del slice de juegos y tokens del MCP (D35)
-- Identificadores en inglés; comentarios en español. Reutiliza set_updated_at() de 0001.

-- Registros normalizados por usuario y categoría (genérica: Música reutiliza la tabla).
create table if not exists public.user_items (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    category text not null,
    -- Id canónico dentro de la fuente (p. ej. steam_appid); deduplica por fuente.
    external_id text not null,
    status text not null,
    title text not null default '',
    -- Extraído del payload para ordenar/filtrar sin abrir el jsonb.
    playtime_minutes integer not null default 0,
    -- El NormalizedItem completo (contrato de schema.py, versionado dentro).
    payload jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, category, external_id)
);

comment on table public.user_items is 'Registros normalizados (NormalizedItem) por usuario y categoría.';

create index if not exists user_items_user_category_idx
    on public.user_items (user_id, category);
create index if not exists user_items_playtime_idx
    on public.user_items (user_id, category, playtime_minutes desc);

create trigger user_items_set_updated_at
    before update on public.user_items
    for each row execute function public.set_updated_at();

alter table public.user_items enable row level security;

create policy "user_items_select_own" on public.user_items
    for select using (auth.uid() = user_id);
create policy "user_items_modify_own" on public.user_items
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Tokens del MCP: solo el hash SHA-256; un token activo por usuario (rotación por upsert).
create table if not exists public.mcp_tokens (
    user_id uuid primary key references auth.users (id) on delete cascade,
    token_hash text not null unique,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

comment on table public.mcp_tokens is 'Token del MCP por usuario, guardado como hash SHA-256.';

create trigger mcp_tokens_set_updated_at
    before update on public.mcp_tokens
    for each row execute function public.set_updated_at();

alter table public.mcp_tokens enable row level security;

-- Solo lectura propia; la resolución por hash la hace el backend (service_role).
create policy "mcp_tokens_select_own" on public.mcp_tokens
    for select using (auth.uid() = user_id);

-- source_state: estado 'private' (perfil de Steam privado, D36), detalle del
-- estado y el perfil del proveedor (persona, avatar, visibilidad).
alter table public.source_state
    drop constraint if exists source_state_status_check;
alter table public.source_state
    add constraint source_state_status_check
    check (status in ('never_synced', 'queued', 'syncing', 'synced', 'private', 'error'));
alter table public.source_state
    add column if not exists detail text;
alter table public.source_state
    add column if not exists provider_profile jsonb;
