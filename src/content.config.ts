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

export const collections = { services };
