// Catálogo de proveedores por categoría (D62). Alimenta el ConnectHub: cada
// proveedor declara cómo se conecta (username público, token o import) y su
// guía paso a paso con enlaces para que el usuario consiga sus datos.

export type ProviderStep = {
  text: string;
  // Enlace del paso (se abre en pestaña nueva) y su texto visible.
  href?: string;
  linkLabel?: string;
};

export type CategoryProvider = {
  // Id del backend (endpoint /sources/<id>); los `soon` aún no lo tienen.
  id: string;
  name: string;
  mode: "api" | "import";
  // Cómo se da de alta: input de username, input de token, subida de export,
  // OpenID (Steam, flujo propio) o pendiente de integración.
  kind: "username" | "token" | "import" | "openid" | "soon";
  description: string;
  placeholder?: string;
  // Tipos de archivo del import (atributo accept del input).
  accept?: string;
  steps: ProviderStep[];
  soonNote?: string;
};

export const CATEGORY_PROVIDERS: Record<string, CategoryProvider[]> = {
  games: [
    {
      id: "steam",
      name: "Steam",
      mode: "api",
      kind: "openid",
      description: "Inicia sesión con Steam y traemos tu biblioteca al momento.",
      steps: [
        {
          text: "Tu perfil y tus detalles de juego deben ser públicos:",
          href: "https://steamcommunity.com/my/edit/settings",
          linkLabel: "ajustes de privacidad de Steam",
        },
        { text: "Pulsa “Conectar Steam” e inicia sesión; no vemos tu contraseña." },
      ],
    },
    {
      id: "xbox",
      name: "Xbox",
      mode: "api",
      kind: "soon",
      description: "Vía OpenXBL, con una API key propia y gratuita.",
      soonNote:
        "Próximamente: te guiaremos para crear tu key gratuita en xbl.io y pegarla aquí.",
      steps: [],
    },
    {
      id: "playstation",
      name: "PlayStation",
      mode: "api",
      kind: "soon",
      description: "Vía el token NPSSO de tu cuenta (no oficial).",
      soonNote:
        "Próximamente: te guiaremos para copiar tu token NPSSO y conectar tu historial de juego.",
      steps: [],
    },
  ],
  music: [
    {
      id: "listenbrainz",
      name: "ListenBrainz",
      mode: "api",
      kind: "username",
      description: "Scrobbles abiertos y en vivo por tu username público.",
      placeholder: "Tu usuario de ListenBrainz",
      steps: [
        {
          text: "Crea tu cuenta (o entra) en",
          href: "https://listenbrainz.org/",
          linkLabel: "listenbrainz.org",
        },
        {
          text: "¿Vienes de Spotify o Last.fm? ListenBrainz puede importar y seguir grabando tu historial:",
          href: "https://listenbrainz.org/settings/music-services/details/",
          linkLabel: "conectar servicios",
        },
        { text: "Escribe tu username y pulsa Conectar; no pedimos tu contraseña." },
      ],
    },
    {
      id: "lastfm",
      name: "Last.fm",
      mode: "api",
      kind: "username",
      description: "Tus scrobbles de siempre, leídos por tu username público.",
      placeholder: "Tu usuario de Last.fm",
      steps: [
        {
          text: "Tu historial debe ser visible (“Hide recent listening information” desmarcado):",
          href: "https://www.last.fm/settings/privacy",
          linkLabel: "privacidad de Last.fm",
        },
        { text: "Escribe tu username y pulsa Conectar; no pedimos tu contraseña." },
      ],
    },
    {
      id: "spotify",
      name: "Spotify",
      mode: "import",
      kind: "import",
      description: "Sube tu historial ampliado (Spotify no da API para esto).",
      accept: ".json,application/json",
      steps: [
        {
          text: "Abre la página de privacidad de tu cuenta:",
          href: "https://www.spotify.com/account/privacy/",
          linkLabel: "spotify.com/account/privacy",
        },
        {
          text: "En “Descargar tus datos” marca solo “Historial de streaming ampliado” y solicita.",
        },
        { text: "Espera el correo de Spotify (hasta 30 días) y descarga el ZIP." },
        {
          text: "Descomprímelo y sube aquí cada archivo Streaming_History_Audio_*.json (uno por uno; se combinan).",
        },
      ],
    },
    {
      id: "applemusic",
      name: "Apple Music",
      mode: "import",
      kind: "import",
      description: "Sube tu historial de reproducción exportado desde Apple.",
      accept: ".csv,text/csv",
      steps: [
        {
          text: "Entra con tu Apple ID en",
          href: "https://privacy.apple.com/",
          linkLabel: "privacy.apple.com",
        },
        {
          text: "Solicita una copia de tus datos y elige “Información de Apple Media Services”.",
        },
        { text: "Espera el correo de Apple (hasta 7 días) y descarga el ZIP." },
        {
          text: "Sube aquí “Apple Music - Play History Daily Tracks.csv” (está dentro de Apple Music Activity).",
        },
      ],
    },
  ],
  film: [
    {
      id: "trakt",
      name: "Trakt",
      mode: "api",
      kind: "username",
      description: "Películas y series vistas, en vivo por tu username público.",
      placeholder: "Tu usuario de Trakt",
      steps: [
        {
          text: "Crea tu cuenta (o entra) en",
          href: "https://trakt.tv/",
          linkLabel: "trakt.tv",
        },
        {
          text: "Tu perfil debe ser público:",
          href: "https://trakt.tv/settings",
          linkLabel: "ajustes de Trakt",
        },
        { text: "Escribe tu username y pulsa Conectar; no pedimos tu contraseña." },
      ],
    },
    {
      id: "letterboxd",
      name: "Letterboxd",
      mode: "import",
      kind: "import",
      description: "Sube tu export CSV (gratis para cualquier cuenta).",
      accept: ".csv,text/csv",
      steps: [
        {
          text: "En letterboxd.com abre Settings → Data:",
          href: "https://letterboxd.com/settings/data/",
          linkLabel: "letterboxd.com/settings/data",
        },
        { text: "Pulsa “Export your data”: descarga un ZIP con varios CSV." },
        {
          text: "Descomprímelo y sube aquí diary.csv; si quieres, añade después watched.csv y ratings.csv (se combinan).",
        },
      ],
    },
    {
      id: "imdb",
      name: "IMDb",
      mode: "import",
      kind: "import",
      description: "Sube el CSV de tus puntuaciones (export de escritorio).",
      accept: ".csv,text/csv",
      steps: [
        {
          text: "En la web de escritorio de IMDb abre “Your Ratings”:",
          href: "https://www.imdb.com/list/ratings",
          linkLabel: "imdb.com/list/ratings",
        },
        { text: "Pulsa Export (menú ⋮); IMDb prepara el archivo." },
        {
          text: "Descárgalo desde “Your exports” cuando esté listo y súbelo aquí:",
          href: "https://www.imdb.com/exports/",
          linkLabel: "imdb.com/exports",
        },
      ],
    },
    {
      id: "tmdb",
      name: "TMDB",
      mode: "api",
      kind: "soon",
      description: "Tus puntuaciones y watchlist de TMDB.",
      soonNote:
        "Próximamente: conexión con aprobación en themoviedb.org (solo trae puntuaciones y watchlist).",
      steps: [],
    },
  ],
  anime: [
    {
      id: "anilist",
      name: "AniList",
      mode: "api",
      kind: "username",
      description: "Listas de anime y manga, en vivo por tu username público.",
      placeholder: "Tu usuario de AniList",
      steps: [
        {
          text: "Crea tu cuenta (o entra) en",
          href: "https://anilist.co/",
          linkLabel: "anilist.co",
        },
        { text: "Escribe tu username y pulsa Conectar; no pedimos tu contraseña." },
      ],
    },
    {
      id: "mal",
      name: "MyAnimeList",
      mode: "api",
      kind: "username",
      description: "Tus listas de MAL, leídas por tu username público.",
      placeholder: "Tu usuario de MyAnimeList",
      steps: [
        {
          text: "Tus listas deben ser públicas (“Anime/Manga List” en Public):",
          href: "https://myanimelist.net/editprofile.php?go=listpreferences",
          linkLabel: "preferencias de lista de MAL",
        },
        { text: "Escribe tu username y pulsa Conectar; no pedimos tu contraseña." },
      ],
    },
    {
      id: "kitsu",
      name: "Kitsu",
      mode: "api",
      kind: "username",
      description: "Tu biblioteca de Kitsu, leída por tu username público.",
      placeholder: "Tu usuario de Kitsu",
      steps: [
        {
          text: "Crea tu cuenta (o entra) en",
          href: "https://kitsu.app/",
          linkLabel: "kitsu.app",
        },
        { text: "Escribe tu username y pulsa Conectar; no pedimos tu contraseña." },
      ],
    },
  ],
  books: [
    {
      id: "goodreads",
      name: "Goodreads",
      mode: "import",
      kind: "import",
      description: "Sube el export CSV de tu biblioteca (Goodreads no tiene API).",
      accept: ".csv,text/csv",
      steps: [
        {
          text: "En Goodreads abre My Books → Import and export:",
          href: "https://www.goodreads.com/review/import",
          linkLabel: "goodreads.com/review/import",
        },
        { text: "Pulsa “Export Library” y espera el enlace de descarga." },
        { text: "Descarga el CSV y súbelo aquí; detectamos el formato solos." },
      ],
    },
    {
      id: "storygraph",
      name: "StoryGraph",
      mode: "import",
      kind: "import",
      description: "Sube el export CSV de tu biblioteca de StoryGraph.",
      accept: ".csv,text/csv",
      steps: [
        {
          text: "En StoryGraph abre Manage Account:",
          href: "https://app.thestorygraph.com/manage-account",
          linkLabel: "app.thestorygraph.com/manage-account",
        },
        {
          text: "Baja a “Manage Your Data” y pulsa “Export StoryGraph Library”.",
        },
        { text: "Descarga el CSV generado y súbelo aquí." },
      ],
    },
    {
      id: "hardcover",
      name: "Hardcover",
      mode: "api",
      kind: "token",
      description: "Conexión en vivo con el token de API de tu cuenta.",
      placeholder: "Pega tu token de Hardcover",
      steps: [
        {
          text: "Entra en hardcover.app y abre Settings → Hardcover API:",
          href: "https://hardcover.app/account/api",
          linkLabel: "hardcover.app/account/api",
        },
        {
          text: "Copia el token (caduca cada 1 de enero; entonces genera otro y reconecta).",
        },
        { text: "Pégalo aquí y pulsa Conectar; lo guardamos cifrado." },
      ],
    },
    {
      id: "openlibrary",
      name: "Open Library",
      mode: "api",
      kind: "username",
      description: "Tu reading log público, sin key ni contraseña.",
      placeholder: "Tu usuario de Open Library",
      steps: [
        {
          text: "Tu reading log debe ser público: Settings → Privacy en",
          href: "https://openlibrary.org/account/privacy",
          linkLabel: "openlibrary.org/account/privacy",
        },
        { text: "Escribe tu username y pulsa Conectar; no pedimos tu contraseña." },
      ],
    },
  ],
};

// Nombre visible de un proveedor por su id de backend.
export function providerName(id: string | null | undefined): string | null {
  if (!id) return null;
  for (const providers of Object.values(CATEGORY_PROVIDERS)) {
    const match = providers.find((provider) => provider.id === id);
    if (match) return match.name;
  }
  return id;
}

export function providersFor(slug: string): CategoryProvider[] {
  return CATEGORY_PROVIDERS[slug] ?? [];
}
