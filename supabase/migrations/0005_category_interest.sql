-- Migración 0005: lista de interés en categorías en desarrollo (D50)
-- Registra a quién avisar cuando una categoría diferida (Lugares, Comida,
-- Juegos de mesa) se active. Solo el backend (service_role) escribe y lee;
-- RLS habilitada sin políticas públicas deniega el acceso de cualquier otro
-- cliente. `user_id` es opcional: la landing pública captura solo el correo.

create table if not exists public.category_interest (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users (id) on delete set null,
    email text not null,
    category text not null,
    created_at timestamptz not null default now(),
    unique (email, category)
);

comment on table public.category_interest is 'Interés en categorías en desarrollo: a quién avisar al activarlas (D50).';

create index if not exists category_interest_category_idx
    on public.category_interest (category);

alter table public.category_interest enable row level security;
