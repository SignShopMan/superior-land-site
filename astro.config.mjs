// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

// SITE_URL / BASE_PATH are set by the GitHub Pages workflow.
// With a custom domain, BASE_PATH stays "/". On <user>.github.io/<repo> it becomes "/<repo>".
const site = process.env.SITE_URL ?? 'https://superiorlandandsite.com';
const base = process.env.BASE_PATH ?? '/';

// https://astro.build/config
export default defineConfig({
  site,
  base,
  trailingSlash: 'ignore',
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [sitemap()],
});
