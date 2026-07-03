import { NextResponse } from "next/server";
import { getServerClient } from "@/lib/supabase/server";

// Callback de OAuth y del enlace de recuperación (D26): intercambia el código
// por una sesión (guardada en cookies) y redirige a la app o al destino pedido.
export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const next = url.searchParams.get("next") ?? "/app";

  if (!code) {
    return NextResponse.redirect(new URL("/auth?error=oauth", url.origin));
  }

  const supabase = await getServerClient();
  const { error } = await supabase.auth.exchangeCodeForSession(code);
  if (error) {
    return NextResponse.redirect(new URL("/auth?error=oauth", url.origin));
  }

  return NextResponse.redirect(new URL(next, url.origin));
}
