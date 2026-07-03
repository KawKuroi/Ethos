import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

// Cliente de Supabase para el navegador (Auth de la web, D26). La sesión se
// guarda en cookies vía @supabase/ssr, lista para las guardas de ruta de la
// shell. Se instancia de forma perezosa (solo al usarse, dentro de handlers)
// para no leer las env ni fallar durante el build cuando no están definidas.
let client: SupabaseClient | undefined;

export function getBrowserClient(): SupabaseClient {
  if (client) return client;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) {
    throw new Error(
      "Falta configurar NEXT_PUBLIC_SUPABASE_URL y NEXT_PUBLIC_SUPABASE_ANON_KEY.",
    );
  }

  client = createBrowserClient(url, anonKey);
  return client;
}
