import type { Metadata } from "next";
import { ConnectAi } from "@/components/app/connect/connect";

export const metadata: Metadata = { title: "Conectar IA" };

export default function ConnectAiPage() {
  return <ConnectAi />;
}
