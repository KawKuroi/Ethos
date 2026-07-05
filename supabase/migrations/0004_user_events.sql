-- Migración 0004: eventos con timestamp (modelo temporal, D38)
-- Genérica por categoría; Música (listens) la estrena. Identificadores en
-- inglés; comentarios en español. Reutiliza set_updated_at() de 0001.

create table if not exists public.user_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    category text not null,
    -- Marca temporal del evento (p. ej. cuándo sonó el track).
    occurred_at timestamptz not null,
    -- Campos del evento (artist, track, release…) del NormalizedEvent.
    payload jsonb not null,
    created_at timestamptz not null default now()
);

comment on table public.user_events is 'Eventos con timestamp por usuario y categoría (D38).';

-- Índice para las consultas por ventana temporal (más escuchadas en 30 días).
create index if not exists user_events_user_category_time_idx
    on public.user_events (user_id, category, occurred_at desc);

alter table public.user_events enable row level security;

create policy "user_events_select_own" on public.user_events
    for select using (auth.uid() = user_id);
create policy "user_events_modify_own" on public.user_events
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
