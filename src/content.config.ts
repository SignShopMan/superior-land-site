import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const services = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/services' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      /** Short label for cards and menus */
      short: z.string(),
      order: z.number(),
      summary: z.string(),
      metaTitle: z.string().optional(),
      hero: image(),
      heroAlt: z.string(),
      benefits: z.array(z.string()).default([]),
      faqs: z.array(z.object({ q: z.string(), a: z.string() })).default([]),
    }),
});

const projects = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projects' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      service: reference('services'),
      town: z.string().optional(),
      completed: z.coerce.date().optional(),
      featured: z.boolean().default(false),
      summary: z.string(),
      cover: image(),
      coverAlt: z.string(),
      before: z.array(z.object({ src: image(), alt: z.string() })).default([]),
      after: z.array(z.object({ src: image(), alt: z.string() })).default([]),
    }),
});

export const collections = { services, projects };
