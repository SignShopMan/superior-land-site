# Superior Land & Site Services: website build plan

**Stack:** Astro 5 · Tailwind CSS v4 · TypeScript · GitHub repo + GitHub Pages (Actions deploy)
**Goal:** A fast, local-SEO site that turns "I need a driveway / land cleared / pond dug" searches in the 937 into calls and quote requests.

---

## 0. What's in the folder now

```
assets-source/
  brand/logo-sketch.jpg                 # new logo concept (source of brand colors)
  brand/logo-america250-variant.jpg     # seasonal red/white/blue "250" badge (from FB)
  photos/hero-fleet.jpg                 # FB cover: truck + gooseneck + CTL + Deere 60G
  photos/fb-001…fb-093-<fbid>.jpg       # 93 full-res photos from the FB photo stream
  photos/manifest.tsv                   # file · category · drone · hero_candidate · size · FB alt text
brand/
  brand-guide.html                      # visual brand guide v0.1 (open in browser)
  tokens.css                            # Tailwind v4 @theme tokens: paste into global.css
PLAN.md
```

Photo coverage by category: brush-clearing 18 · grading-seeding 18 · commercial-site 15 · ponds 14 · driveways 12 · culverts-bridges 4 · drainage 3 · forestry-mulching 3 · fleet 3 · demolition 2 · land-clearing 1.

> The photos came from the page's public view without logging in. Facebook put up a login wall after about 93 photos, around June 18, 2026. Older photos, and any in albums, would need a logged-in export. The easiest way is to ask the owner to run *Download Your Information → Photos* from the page.

---

## 1. Open questions for the owner (answer before Phase 3 copy)

1. **Legal name / DBA.** The FB page is "Superior Bobcat Services LLC." Is "Superior Land & Site Services" a DBA or a rename? This affects schema markup, the footer and the Google Business Profile.
2. **Service area.** Which towns and counties? The 937 area code suggests the Dayton / Miami Valley / Darke–Miami–Shelby area. We need a list to build town pages.
3. **Services to lead with**, and any to drop (e.g. snow removal, demo).
4. **Domain.** Is one owned already? Options: `superiorlandandsite.com`, `superiorlandsite.com`, `superiorsiteservices.com`.
5. **Quote form destination.** Which email or phone should receive leads? Do they want text notifications?
6. **Proof points.** Years in business, insured/licensed, equipment list, Google reviews link, owner name and photo.
7. **Logo vector.** Who redraws it? It needs an SVG with the clipped "R" fixed, plus a version without the phone number (see brand guide §02).

---

## 2. Information architecture

```
/                         Home
/services/                Services overview
  /services/driveways/
  /services/land-clearing/          (incl. forestry mulching)
  /services/brush-clearing/         (roadside, fence-line, ROW)
  /services/grading-seeding/
  /services/ponds/
  /services/drainage-culverts/
  /services/commercial-site-prep/
  /services/demolition/             (optional; confirm)
/projects/                Project gallery (filterable by service)
  /projects/[slug]/       Before/after case studies (start with 4–6)
/service-area/            Map + town list
  /service-area/[town]/   Town pages (phase 2 SEO, only with real local content)
/about/                   Owner, equipment, insurance
/contact/                 Quote form + click-to-call + hours
/404
```

**Global chrome.** Sticky header with the wordmark, nav and an orange **Get a Free Quote** button. On mobile, a **sticky bottom bar** with *Call* and *Quote*. Footer with NAP (name, address, phone), service list, towns and a Facebook link.

---

## 3. Home page wireframe (conversion-first)

1. **Hero.** Drone or fleet photo under a Blackout scrim. H1: *"Driveways, Land Clearing & Site Work in [Region], Ohio."* Subhead gives a proof line. Primary CTA **Get a Free Quote**, secondary **Call 937-539-3002**, with trust chips (Free estimates · Fully insured · Owner on every job).
2. **Service grid.** Eight cards, each with a photo, a one-line benefit and a link.
3. **Before/after slider.** One flagship job, such as a driveway regrade or pond.
4. **How it works.** Three steps: call or send photos → on-site quote → we clear, grade and finish.
5. **Recent projects strip.** Six photos, linked to /projects.
6. **Reviews.** Embedded Google reviews. Add these once the GBP is live. For now, hand-picked FB recommendations.
7. **Service area map.** Plus the town list.
8. **Final CTA band.** Skewed orange and green stripe, with the quote form inline.

---

## 4. Project setup (Phase 1)

```bash
npm create astro@latest . -- --template minimal --typescript strict --install --git
npx astro add tailwind       # Tailwind v4 via @tailwindcss/vite
npx astro add sitemap
npm i -D @astrojs/check prettier prettier-plugin-astro prettier-plugin-tailwindcss
npm i @fontsource/barlow @fontsource/barlow-condensed
```

- `src/styles/global.css` → `@import "tailwindcss";` then paste `brand/tokens.css`.
- Self-host fonts through Fontsource (Barlow 400/500/600/700; Barlow Condensed 800/900 italic).
- `astro.config.mjs`: `site`, `base` (only if we use the `username.github.io/repo` URL), plus the sitemap and image service.
- Move the chosen photos to `src/assets/photos/<category>/` and rename them for SEO (`gravel-driveway-regrade-piqua-oh.jpg`). Render them with `<Image>` / `<Picture>` to get AVIF/WebP and responsive `srcset`. The raw set is 44 MB, so **don't** put it in `public/`.
- Add `assets-source/` to the repo with Git LFS, or keep it out of the repo (`.gitignore`) and archive it separately. **Recommended:** keep it out and only commit the curated `src/assets`.

### Directory layout
```
src/
  assets/photos/…            curated, renamed
  assets/brand/logo.svg      once vectorized
  components/
    Header.astro  Footer.astro  MobileCallBar.astro
    Hero.astro  ServiceCard.astro  BeforeAfter.astro
    ProjectGallery.astro  QuoteForm.astro  CTABand.astro
    TrustChips.astro  ReviewList.astro  ServiceAreaMap.astro
  content/
    services/*.md            content collection (title, summary, hero, faqs, related)
    projects/*.md            content collection (service, town, date, before[], after[])
    towns/*.md               (phase 2)
  content.config.ts          zod schemas
  layouts/Base.astro         SEO head, JSON-LD, fonts
  pages/…                    per IA above
  data/site.ts               NAP, hours, phone, social, service-area list
```

---

## 5. Content collections

- **services**: `title`, `slug`, `summary`, `heroImage`, `benefits[]`, `process[]`, `faqs[]` (shown as an FAQ section and output as `FAQPage` JSON-LD), `relatedProjects[]`.
- **projects**: `title`, `service` (ref), `town`, `completed`, `before[]`, `after[]`, `drone?`, `story` (3–5 sentences). There are ready-made groupings in the FB set:
  - Pond build + seeding (fb-055…063, drone)
  - Pond restoration (fb-086…090)
  - Commercial stone / site work (fb-040…045, fb-076…078)
  - Culvert / footbridge replacement (fb-064…067)
  - Downspout drainage (fb-009…011)
  - Forestry mulching lot clear (fb-046…048)
  - Roadside brush clearing (fb-015…030, fb-072…075)
  - New gravel drive to pole barn (fb-006…007)

---

## 6. Lead capture (GitHub Pages is static)

- **Primary:** `tel:` links everywhere, plus the sticky mobile call bar.
- **Quote form:** name, phone, town, service (select), message, optional photo upload. Post it to a static-friendly form backend:
  - **Web3Forms** (free, email only, no upload) or **Formspree** (uploads on paid plan) or **Basin**.
  - Add a honeypot and Cloudflare Turnstile for spam.
- Thank-you page `/thanks/` for conversion tracking.
- **Analytics:** GA4 or Plausible. Track events for `click_call`, `form_submit` and `click_directions`.

---

## 7. Local SEO

- `LocalBusiness` → `HomeAndConstructionBusiness` JSON-LD with NAP, `areaServed` (list of towns), `sameAs` (FB), `openingHours` and `geo`.
- Per-service `Service` schema and per-FAQ `FAQPage`.
- Title pattern: `Gravel Driveway Installation & Repair | Superior Land & Site | [Town], OH`.
- Keep the Google Business Profile's NAP consistent with the site. Add GBP categories: *Excavating contractor*, *Land clearing service*, *Grading contractor*.
- Descriptive alt text on every image, e.g. "Deere 60G excavator clearing a roadside fence line near [town]".
- Performance budget: LCP < 2.0s on 4G, total JS < 30 KB (the only JS is the before/after slider and the mobile menu).

---

## 8. GitHub + deploy

1. `git init` → create the repo `superior-land-site` (private until launch) → push `main`.
2. Add `.github/workflows/deploy.yml` using `withastro/action@v3` + `actions/deploy-pages@v4`.
3. Settings → Pages → Source: **GitHub Actions**.
4. Custom domain: add `public/CNAME`. DNS gets A records to GitHub Pages IPs and `www` CNAME → `<user>.github.io`. Enforce HTTPS.
5. Branch protection on `main`. PR previews are optional (Pages has no native previews; use Cloudflare Pages or Netlify if previews matter).

---

## 9. Phases & checklist

| Phase | Deliverable | Status |
|---|---|---|
| **1. Brand** | Palette, type, UI rules, photo inventory (`brand/`) | ✅ v0.1 draft |
| | Logo vector redraw (SVG, flat, knockout, icon) | ⬜ needs designer/owner |
| **2. Scaffold** | Astro 7 + Tailwind v4 + tokens, layout, all page templates, 8 services, 4 draft projects, Pages workflow | ✅ local; repo not created/pushed yet |
| **3. Core pages** | Home, Services (×8), Contact + form, About (draft copy in place; needs owner facts) | 🟡 |
| **4. Proof** | Projects collection with 6–8 case studies, before/after, gallery filter | ⬜ |
| **5. SEO/launch** | JSON-LD, sitemap, meta/OG images, analytics, domain + HTTPS, GBP link-up | ⬜ |
| **6. Post-launch** | Town pages, review widget, CRO audit against `~/.claude/cro-audit-rubric.md`, monthly project posts | ⬜ |

**Next step:** answer the §1 questions (at least the name, service area and domain), then scaffold Phase 2.
