"use client";

import { connectListenBrainz } from "@/lib/api";
import { ConnectUsernameForm } from "./connect-username";

// Alta de la fuente de música: ListenBrainz se lee por username público (D37).
// Envoltorio del formulario genérico de conexión por username.
export function ConnectListenBrainzForm({
  className,
  onConnected,
}: {
  className?: string;
  onConnected: () => void;
}) {
  return (
    <ConnectUsernameForm
      className={className}
      placeholder="Tu usuario de ListenBrainz"
      ariaLabel="Nombre de usuario de ListenBrainz"
      errorText="No se pudo conectar. Revisa tu nombre de usuario de ListenBrainz e inténtalo de nuevo."
      connect={connectListenBrainz}
      onConnected={onConnected}
    />
  );
}
