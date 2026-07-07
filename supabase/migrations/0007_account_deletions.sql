-- Migración 0007: borrado de cuenta diferido con deshacer de 30 días (D53)
-- Marca una cuenta para purga futura; el usuario puede deshacerlo hasta
-- `purge_after`. Un job programado purga las vencidas (borra el usuario de
-- auth.users, que cascada al resto). Solo el backend (service_role) gestiona;
-- el usuario puede leer su propio estado (RLS select own).

create table if not exists public.account_deletions (
    user_id uuid primary key references auth.users (id) on delete cascade,
    requested_at timestamptz not null default now(),
    purge_after timestamptz not null
);

comment on table public.account_deletions is 'Cuentas marcadas para borrado diferido con deshacer de 30 días (D53).';

create index if not exists account_deletions_purge_idx
    on public.account_deletions (purge_after);

alter table public.account_deletions enable row level security;

create policy "account_deletions_select_own" on public.account_deletions
    for select using (auth.uid() = user_id);
