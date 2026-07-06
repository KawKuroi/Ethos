-- Migración 0006: sugerencias y contacto (D52)
-- Persiste el envío real de sugerencias (landing y Ayuda). Solo el backend
-- (service_role) escribe/lee; RLS habilitada sin políticas públicas deniega el
-- acceso de cualquier otro cliente. `user_id` es opcional (envío anónimo).

create table if not exists public.feedback (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users (id) on delete set null,
    -- 'suggestion' (por defecto) o 'contact'; extensible.
    kind text not null default 'suggestion',
    -- Categoría o proveedor al que apunta la sugerencia (opcional).
    category text,
    name text,
    email text,
    message text not null,
    created_at timestamptz not null default now()
);

comment on table public.feedback is 'Sugerencias y contacto de los usuarios (D52).';

create index if not exists feedback_created_idx on public.feedback (created_at desc);

alter table public.feedback enable row level security;
