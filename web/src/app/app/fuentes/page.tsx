import type { Metadata } from "next";
import { Sources } from "@/components/app/sources/sources";

export const metadata: Metadata = { title: "Fuentes" };

export default function SourcesPage() {
  return <Sources />;
}
