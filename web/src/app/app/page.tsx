import type { Metadata } from "next";
import { Overview } from "@/components/app/overview/overview";

export const metadata: Metadata = { title: "Inicio" };

export default function OverviewPage() {
  return <Overview />;
}
