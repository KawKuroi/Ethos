import { notFound } from "next/navigation";
import { CATEGORY_DETAIL, categoryBySlug } from "@/components/app/category/data";
import { CategoryDetail } from "@/components/app/category/category-detail";
import { CategoryPager } from "@/components/app/category/category-pager";
import { AnimeDetail } from "@/components/app/category/anime-detail";
import { BooksDetail } from "@/components/app/category/books-detail";
import { FilmDetail } from "@/components/app/category/film-detail";
import { GamesDetail } from "@/components/app/category/games-detail";
import { MusicDetail } from "@/components/app/category/music-detail";

export function generateStaticParams() {
  return Object.keys(CATEGORY_DETAIL).map((slug) => ({ slug }));
}

// Título de pestaña = nombre de la categoría ("Juegos", "Música", …).
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const category = categoryBySlug(slug);
  return { title: category?.name ?? "Categoría" };
}

// Cada categoría activa tiene su detalle con datos reales del backend; el
// componente genérico queda para categorías futuras "en desarrollo".
const DETAILS: Record<string, () => React.ReactElement> = {
  games: GamesDetail,
  music: MusicDetail,
  film: FilmDetail,
  anime: AnimeDetail,
  books: BooksDetail,
};

export default async function CategoryPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const category = categoryBySlug(slug);
  if (!category) notFound();
  const Detail = DETAILS[slug];
  return (
    <>
      {Detail ? <Detail /> : <CategoryDetail category={category} />}
      <CategoryPager slug={slug} />
    </>
  );
}
