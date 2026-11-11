import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// 業務案内（services）。src/content/services/*.md を1件1ページとして扱う。
const services = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/services' }),
  schema: z.object({
    title: z.string(),
    // 検索結果に出る題名（地域名入り）。無ければ title＋「（奈良市）」付きの事務所名になる。
    seoTitle: z.string().optional(),
    catch: z.string(),
    summary: z.string(),
    order: z.number(),
    keywords: z.array(z.string()).default([]),
    featured: z.boolean().default(false),
    // よくあるご質問。本文の後ろに表示し、検索エンジン向けの補助情報（FAQPage）にも出す。
    faq: z.array(z.object({ q: z.string(), a: z.string() })).default([]),
    // 内容を確認した時点（例：2026年11月）。ページ末尾に「〜時点の法令・手引きに基づく」と表示する。
    updated: z.string().optional(),
  }),
});

const isoDate = z.union([z.string(), z.date()]).transform((v) =>
  typeof v === 'string' ? v : v.toISOString().slice(0, 10),
);

// 解説記事（articles）。src/content/articles/*.md を1件1ページとして扱う（/articles/{ファイル名}/）。
const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articles' }),
  schema: z.object({
    title: z.string(),
    // 検索結果に出る題名。無ければ title＋事務所名。
    seoTitle: z.string().optional(),
    // 一覧と検索結果の説明文（120字前後）
    description: z.string(),
    // 公開日・更新日（YYYY-MM-DD。YAML が日付として読んでも文字列に戻す）
    published: isoDate,
    updated: isoDate.optional(),
    // 内容を確認した時点（例：2026年11月）。記事末尾に「〜時点の法令・資料に基づく」と表示する。
    basis: z.string(),
    // 関連する業務ページ（services のファイル名）。業務ページの「関連する解説記事」にも出る。
    related: z.array(z.string()).default([]),
    faq: z.array(z.object({ q: z.string(), a: z.string() })).default([]),
    // true の記事はビルドに含めない（下書き置き場として使う）
    draft: z.boolean().default(false),
  }),
});

export const collections = { services, articles };
