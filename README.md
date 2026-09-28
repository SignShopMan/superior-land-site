# Superior Land & Site Services — website

Astro 7 + Tailwind CSS v4 static site, deployed to GitHub Pages.

## Develop

```bash
npm install
npm run dev        # http://localhost:4321
npm run check      # type-check .astro/.ts
npm run build      # → dist/
npm run format     # prettier (astro + tailwind class sorting)
```

Copy `.env.example` → `.env` and set `PUBLIC_WEB3FORMS_KEY` to make the quote form deliver.

## Where things live

| Path | What |
|---|---|
| `src/data/site.ts` | Phone, region, hours, trust chips, nav. **TODOs = unconfirmed facts** |
| `src/content/services/*.md` | One file per service page (frontmatter drives cards, FAQs, JSON-LD) |
| `src/content/projects/*.md` | Case studies with before/after photos |
| `src/assets/photos/` | Curated, SEO-named photos (optimized at build by `<Image>`) |
| `src/styles/global.css` | Tailwind import + brand tokens (`@theme`) |
| `src/lib/url.ts` | `url()` helper — use for every internal link so the GH Pages base path works |
| `brand/` | Brand guide (`brand-guide.html`) and token source |
| `assets-source/` | Raw Facebook photo dump + manifest (git-ignored, 44 MB) |
| `PLAN.md` | Build plan, open questions, phases |

## Adding a project

1. Drop photos in `src/assets/photos/` named like `service-detail-town-oh.jpg`.
2. Create `src/content/projects/<slug>.md` — copy an existing one; `service` must match a file in `src/content/services/`.

## Deploy

Push to `main` → `.github/workflows/deploy.yml` builds and publishes to Pages.
One-time setup: repo **Settings → Pages → Source: GitHub Actions**, and add the `PUBLIC_WEB3FORMS_KEY` repo secret.
For a custom domain, set it in Settings → Pages (base path then becomes `/` automatically).
