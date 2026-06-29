-- Migración 0001: fundación
-- Tablas base, índices, triggers y políticas RLS.
-- Identificadores en inglés; comentarios en español.

create extension if not exists "pgcrypto";

-- Perfil de aplicación, uno por usuario de Supabase Auth.
create table if not exists public.profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    display_name text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

comment on table public.profiles is 'Perfil de aplicación por usuario (1:1 con auth.users).';

-- Estado de la fuente activa por categoría: ingesta y frescura.
create table if not exists public.source_state (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    category text not null,
    provider text not null,
    mode text not null check (mode in ('api', 'import')),
    status text not null default 'never_synced'
        check (status in ('never_synced', 'queued', 'syncing', 'synced', 'error')),
    last_synced_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, category)
);

comment on table public.source_state is 'Fuente activa y su frescura por usuario y categoría.';

create index if not exists source_state_user_idx on public.source_state (user_id);

-- Mantiene updated_at en cada actualización.
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create trigger profiles_set_updated_at
    before update on public.profiles
    for each row execute function public.set_updated_at();

create trigger source_state_set_updated_at
    before update on public.source_state
    for each row execute function public.set_updated_at();

-- Row-Level Security: cada usuario solo accede a lo suyo.
alter table public.profiles enable row level security;
alter table public.source_state enable row level security;

create policy "profiles_select_own" on public.profiles
    for select using (auth.uid() = id);
create policy "profiles_insert_own" on public.profiles
    for insert with check (auth.uid() = id);
create policy "profiles_update_own" on public.profiles
    for update using (auth.uid() = id) with check (auth.uid() = id);

create policy "source_state_select_own" on public.source_state
    for select using (auth.uid() = user_id);
create policy "source_state_modify_own" on public.source_state
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
