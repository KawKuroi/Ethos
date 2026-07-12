"use client";

import { useEffect, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { getBrowserClient } from "@/lib/supabase/client";

export type SessionUser = {
  name: string | null;
  email: string | null;
  // Proveedores de identidad de la cuenta ("email", "google"…). Sirve para
  // mostrar el cambio de contraseña solo a quien inició con correo.
  providers: string[];
};

const EMPTY: SessionUser = { name: null, email: null, providers: [] };

// El registro guarda el nombre en user_metadata.full_name; Google entrega
// full_name o name según la cuenta.
function nameFrom(meta: Record<string, unknown>): string | null {
  for (const key of ["full_name", "name"]) {
    const value = meta[key];
    if (typeof value === "string" && value.trim().length > 0)
      return value.trim();
  }
  return null;
}

function toSessionUser(user: User | null): SessionUser {
  if (!user) return EMPTY;
  const providers = (user.identities ?? [])
    .map((identity) => identity.provider)
    .filter((provider): provider is string => typeof provider === "string");
  return {
    name: nameFrom(user.user_metadata ?? {}),
    email: user.email ?? null,
    providers,
  };
}

// Nombre y correo del usuario de la sesión de Supabase. Se mantiene al día
// con onAuthStateChange (incluye USER_UPDATED al guardar el perfil). Sin
// variables de entorno o sin sesión devuelve nulls.
export function useUser(): SessionUser {
  const [user, setUser] = useState<SessionUser>(EMPTY);

  useEffect(() => {
    let supabase: ReturnType<typeof getBrowserClient>;
    try {
      supabase = getBrowserClient();
    } catch {
      return; // Entorno sin configurar (tests, build): sin sesión.
    }
    let active = true;
    void supabase.auth.getSession().then(({ data }) => {
      if (active) setUser(toSessionUser(data.session?.user ?? null));
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_event, session) => {
      if (active) setUser(toSessionUser(session?.user ?? null));
    });
    return () => {
      active = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  return user;
}
