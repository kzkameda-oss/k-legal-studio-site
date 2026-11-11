import { getCollection } from 'astro:content';

// 公開する解説記事（draft を除く）を新しい順で返す。
export async function getArticles() {
  const all = await getCollection('articles', ({ data }) => !data.draft);
  return all.sort((a, b) => b.data.published.localeCompare(a.data.published));
}

// 「2026-11-11」→「2026年11月11日」
export function jaDate(iso: string) {
  const [y, m, d] = iso.split('-').map(Number);
  return `${y}年${m}月${d}日`;
}
