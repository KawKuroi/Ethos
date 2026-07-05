import type { Metadata } from "next";
import { Help } from "@/components/app/help/help";

export const metadata: Metadata = { title: "Ayuda" };

export default function HelpPage() {
  return <Help />;
}
