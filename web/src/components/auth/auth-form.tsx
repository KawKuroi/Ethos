"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getBrowserClient } from "@/lib/supabase/client";
import styles from "./auth.module.css";

type Mode = "login" | "register";
type Provider = "google" | "github";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Traduce los errores de Supabase (en inglés) a mensajes en español.
function messageForError(message: string): string {
  const m = message.toLowerCase();
  if (m.includes("invalid login credentials"))
    return "Correo o contraseña incorrectos.";
  if (m.includes("already registered") || m.includes("already been registered"))
    return "Ya existe una cuenta con este correo.";
  if (m.includes("email not confirmed"))
    return "Confirma tu correo antes de iniciar sesión.";
  return "Algo salió mal. Inténtalo de nuevo.";
}

function GoogleIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M23 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.2a5.3 5.3 0 0 1-2.3 3.5v2.9h3.7c2.2-2 3.4-5 3.4-8.6z"
      />
      <path
        fill="#34A853"
        d="M12 24c3.1 0 5.7-1 7.6-2.8l-3.7-2.9c-1 .7-2.4 1.1-3.9 1.1-3 0-5.5-2-6.4-4.8H1.8v3C3.7 21.4 7.5 24 12 24z"
      />
      <path
        fill="#FBBC05"
        d="M5.6 14.6a7.2 7.2 0 0 1 0-4.6v-3H1.8a12 12 0 0 0 0 10.6l3.8-3z"
      />
      <path
        fill="#EA4335"
        d="M12 4.8c1.7 0 3.2.6 4.4 1.7l3.3-3.3C17.7 1.2 15.1 0 12 0 7.5 0 3.7 2.6 1.8 6.4l3.8 3C6.5 6.7 9 4.8 12 4.8z"
      />
    </svg>
  );
}

function GithubIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 .5A11.5 11.5 0 0 0 8.4 22.9c.6.1.8-.2.8-.5v-2c-3.3.7-4-1.4-4-1.4-.5-1.4-1.3-1.7-1.3-1.7-1.1-.7 0-.7 0-.7 1.2 0 1.8 1.2 1.8 1.2 1.1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2 0-.4-.5-1.6.2-3.2 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17.3 4.7 18.3 5 18.3 5c.7 1.6.2 2.8.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 5.9.4.4.8 1.1.8 2.2v3.3c0 .3.2.6.8.5A11.5 11.5 0 0 0 12 .5z" />
    </svg>
  );
}

function EyeIcon({ off }: { off: boolean }) {
  if (off) {
    return (
      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
        <path d="M3 3l18 18" strokeLinecap="round" />
        <path
          d="M10.6 5.1A9.9 9.9 0 0 1 12 5c5.5 0 9 5.5 9 7-.3 1-1.3 2.5-2.8 3.8M6.2 6.3C3.9 7.8 3 10.2 3 12c0 1.2 3.5 7 9 7 1.6 0 3-.5 4.2-1.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path d="M9.8 9.9a3 3 0 0 0 4.2 4.2" strokeLinecap="round" />
      </svg>
    );
  }
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <path d="M3 12s3.5-7 9-7 9 7 9 7-3.5 7-9 7-9-7-9-7z" strokeLinejoin="round" />
      <circle cx="12" cy="12" r="2.6" />
    </svg>
  );
}

export function AuthForm() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [agree, setAgree] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const isLogin = mode === "login";
  const isRegister = !isLogin;

  function switchMode(next: Mode) {
    setMode(next);
    setShowPw(false);
    setError(null);
    setNotice(null);
  }

  async function onSocial(provider: Provider) {
    if (loading) return;
    setError(null);
    setNotice(null);
    setLoading(true);
    try {
      const { error: authError } = await getBrowserClient().auth.signInWithOAuth({
        provider,
        options: { redirectTo: `${window.location.origin}/auth/callback` },
      });
      if (authError) {
        setError(messageForError(authError.message));
        setLoading(false);
      }
      // En éxito, Supabase redirige al proveedor: no reseteamos loading.
    } catch {
      setError("No se pudo conectar. Revisa tu conexión e inténtalo de nuevo.");
      setLoading(false);
    }
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (loading) return;
    setError(null);
    setNotice(null);

    if (isRegister && name.trim().length === 0) {
      setError("Dinos cómo te llamamos.");
      return;
    }
    if (!EMAIL_RE.test(email)) {
      setError("Escribe un correo válido.");
      return;
    }
    if (password.length < 8) {
      setError("La contraseña necesita al menos 8 caracteres.");
      return;
    }
    if (isRegister && !agree) {
      setError("Acepta los Términos y la Política de privacidad para continuar.");
      return;
    }

    setLoading(true);
    try {
      const supabase = getBrowserClient();
      if (isLogin) {
        const { error: authError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (authError) {
          setError(messageForError(authError.message));
          setLoading(false);
          return;
        }
        router.push("/app");
      } else {
        const { data, error: authError } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: name.trim() },
            emailRedirectTo: `${window.location.origin}/auth/callback`,
          },
        });
        if (authError) {
          setError(messageForError(authError.message));
          setLoading(false);
          return;
        }
        // Si la confirmación por correo está activa no hay sesión todavía.
        if (data.session) {
          router.push("/app");
        } else {
          setNotice("Te enviamos un correo para confirmar tu cuenta.");
          setLoading(false);
        }
      }
    } catch {
      setError("No se pudo conectar. Revisa tu conexión e inténtalo de nuevo.");
      setLoading(false);
    }
  }

  return (
    <div className={styles.card}>
      <div className={styles.segmented}>
        <button
          type="button"
          onClick={() => switchMode("login")}
          className={`${styles.tab} ${isLogin ? styles.tabActive : ""}`}
        >
          Iniciar sesión
        </button>
        <button
          type="button"
          onClick={() => switchMode("register")}
          className={`${styles.tab} ${isRegister ? styles.tabActive : ""}`}
        >
          Crear cuenta
        </button>
      </div>

      <h2 className={styles.heading}>
        {isLogin ? "Bienvenido de vuelta" : "Crea tu cuenta"}
      </h2>
      <p className={styles.sub}>
        {isLogin
          ? "Entra para consultar y gestionar tu perfil de gusto."
          : "Reúne tu gusto en un solo lugar y conéctalo a tu IA."}
      </p>

      <div className={styles.social}>
        <button
          type="button"
          className={styles.socialBtn}
          onClick={() => onSocial("google")}
          disabled={loading}
        >
          <GoogleIcon />
          Continuar con Google
        </button>
        <button
          type="button"
          className={styles.socialBtn}
          onClick={() => onSocial("github")}
          disabled={loading}
        >
          <GithubIcon />
          Continuar con GitHub
        </button>
      </div>

      <div className={styles.divider}>
        <span className={styles.dividerLine} />
        <span className={styles.dividerText}>o con tu correo</span>
        <span className={styles.dividerLine} />
      </div>

      <form className={styles.form} onSubmit={onSubmit} noValidate>
        {isRegister && (
          <label className={`${styles.field} ${styles.fieldIn}`}>
            <span className={styles.label}>Nombre</span>
            <input
              className={styles.input}
              type="text"
              placeholder="Cómo te llamamos"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
            />
          </label>
        )}

        <label className={styles.field}>
          <span className={styles.label}>Correo</span>
          <input
            className={styles.input}
            type="email"
            placeholder="tu@correo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
          />
        </label>

        <label className={styles.field}>
          <span className={styles.labelRow}>
            <span className={styles.label}>Contraseña</span>
            {isLogin && (
              <Link href="/auth/recuperar" className={styles.forgot}>
                ¿Olvidaste tu contraseña?
              </Link>
            )}
          </span>
          <span className={styles.pwWrap}>
            <input
              className={`${styles.input} ${styles.pwInput}`}
              type={showPw ? "text" : "password"}
              placeholder={isLogin ? "Tu contraseña" : "Mínimo 8 caracteres"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isLogin ? "current-password" : "new-password"}
            />
            <button
              type="button"
              className={styles.pwToggle}
              onClick={() => setShowPw((v) => !v)}
              title="Mostrar u ocultar contraseña"
              aria-label="Mostrar u ocultar contraseña"
            >
              <EyeIcon off={showPw} />
            </button>
          </span>
        </label>

        {isRegister && (
          <label className={`${styles.terms} ${styles.fieldIn}`}>
            <button
              type="button"
              onClick={() => setAgree((v) => !v)}
              className={`${styles.check} ${agree ? styles.checkOn : ""}`}
              role="checkbox"
              aria-checked={agree}
              aria-label="Acepto los Términos y la Política de privacidad"
            >
              {agree && (
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--on-accent)" strokeWidth="3.2" aria-hidden="true">
                  <path d="M5 12.5l4.2 4.2L19 6.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </button>
            <span className={styles.termsText}>
              Acepto los{" "}
              <Link href="/terminos" className={styles.termsLink}>
                Términos
              </Link>{" "}
              y la{" "}
              <Link href="/privacidad" className={styles.termsLink}>
                Política de privacidad
              </Link>
              .
            </span>
          </label>
        )}

        {error && <p className={styles.error}>{error}</p>}
        {notice && <p className={styles.ok}>{notice}</p>}

        <button type="submit" className={styles.submit} disabled={loading}>
          {loading ? (
            <span className={styles.spinner} aria-hidden="true" />
          ) : isLogin ? (
            "Iniciar sesión"
          ) : (
            "Crear cuenta"
          )}
        </button>
      </form>

      <div className={styles.switch}>
        {isLogin ? "¿Aún no tienes cuenta? " : "¿Ya tienes cuenta? "}
        <button
          type="button"
          className={styles.switchLink}
          onClick={() => switchMode(isLogin ? "register" : "login")}
        >
          {isLogin ? "Crear una" : "Iniciar sesión"}
        </button>
      </div>
    </div>
  );
}
