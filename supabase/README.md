# Supabase — Ethos

Esquema de datos, políticas RLS y migraciones del proyecto.

## Migraciones

- `migrations/0001_foundation.sql` — fundación: `profiles`, `source_state`,
  índices, triggers de `updated_at` y políticas RLS owner-only.

Las tablas específicas de cada proveedor (p. ej. Steam: `games`, `user_games`,
`user_wishlist`, `user_profile_steam`) llegan en Fase 1.

## Aplicar

Con la [Supabase CLI](https://supabase.com/docs/guides/cli) y un proyecto
enlazado:

```bash
supabase db push        # aplica las migraciones pendientes
```

O ejecutar el SQL directamente en el editor SQL del panel de Supabase.

> Requiere un proyecto Supabase real (con `auth.users`). El esquema referencia
> `auth.uid()` para las políticas RLS.
