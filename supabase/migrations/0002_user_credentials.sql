-- Migración 0002: credenciales de terceros por usuario
-- Token cifrado a nivel de app (Fernet/AES-GCM); la llave vive en el secret
-- manager, nunca en la BD. RLS owner-only. Reutiliza set_updated_at() de 0001.

create table if not exists public.user_credentials (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    category text not null,
    provider text not null,
    encrypted_token text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, provider)
);

comment on table public.user_credentials is 'Credenciales de terceros por usuario, cifradas a nivel de app.';

create index if not exists user_credentials_user_idx on public.user_credentials (user_id);

create trigger user_credentials_set_updated_at
    before update on public.user_credentials
    for each row execute function public.set_updated_at();

alter table public.user_credentials enable row level security;

create policy "user_credentials_select_own" on public.user_credentials
    for select using (auth.uid() = user_id);
create policy "user_credentials_modify_own" on public.user_credentials
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
