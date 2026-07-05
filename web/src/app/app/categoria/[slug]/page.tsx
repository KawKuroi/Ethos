import { notFound } from "next/navigation";
import { CATEGORY_DETAIL, categoryBySlug } from "@/components/app/category/data";
import { CategoryDetail } from "@/components/app/category/category-detail";
import { GamesDetail } from "@/components/app/category/games-detail";
import { MusicDetail } from "@/components/app/category/music-detail";

export function generateStaticParams() {
  return Object.keys(CATEGORY_DETAIL).map((slug) => ({ slug }));
}

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const category = categoryBySlug(slug);
  if (!category) notFound();
  // Juegos y Música usan datos reales del backend; el resto, en desarrollo.
  if (slug === "games") return <GamesDetail />;
  if (slug === "music") return <MusicDetail />;
  return <CategoryDetail category={category} />;
}
