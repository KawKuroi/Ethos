import { notFound } from "next/navigation";
import { CATEGORY_DETAIL, categoryBySlug } from "@/components/app/category/data";
import { CategoryDetail } from "@/components/app/category/category-detail";

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
  return <CategoryDetail category={category} />;
}
