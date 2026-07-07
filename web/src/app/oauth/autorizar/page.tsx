import { Suspense } from "react";
import { OAuthConsent } from "@/components/oauth/consent";

export const metadata = { title: "Autorizar acceso" };

// useSearchParams exige un límite de Suspense al prerenderizar.
export default function OAuthAuthorizePage() {
  return (
    <Suspense fallback={null}>
      <OAuthConsent />
    </Suspense>
  );
}
