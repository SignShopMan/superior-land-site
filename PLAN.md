# Superior Land & Site Services: website build plan

**Stack:** Astro 7 · Tailwind CSS v4 · TypeScript · GitHub repo + GitHub Pages (Actions deploy)
**Goal:** A refined, fast site that wins **commercial, municipal and 3+ acre residential** bids in West-Central Ohio.

> **Repositioned 2026-10-16 (owner feedback):** no small residential work. Only commercial, municipal, and residential properties of 3+ acres (roughly $500–600k homes). The owner isn't a fan of orange + green and wants something more refined for larger markets. The brand moved to v0.2 "Iron & Copper", then **v0.3: heritage shield logo + charcoal / Superior orange** (see `brand/logo-concepts/`). Reference sites: biggreens.com, landmanagementresources.com.

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
  brand-guide.html                      # visual brand guide v0.2 "Iron & Copper" (open in browser)
  tokens.css                            # Tailwind v4 @theme tokens: paste into global.css
PLAN.md
```

Photo coverage by category: brush-clearing 18 · grading-seeding 18 · commercial-site 15 · ponds 14 · driveways 12 · culverts-bridges 4 · drainage 3 · forestry-mulching 3 · fleet 3 · demolition 2 · land-clearing 1.

> The photos came from the page's public view without logging in. Facebook put up a login wall after about 93 photos, around June 18, 2026. Older photos, and any in albums, would need a logged-in export. The easiest way is to ask the owner to run *Download Your Information → Photos* from the page.

---

## 1. Open questions for the owner (answer before Phase 3 copy)

1. **Legal name / DBA.** The FB page is "Superior Bobcat Services LLC." Is "Superior Land & Site Services" a DBA or a rename? This affects schema markup, the footer and the Google Business Profile.
2. **Service area.** Which counties? The 937-539 exchange is Bellefontaine / Logan County, so the site currently says "West-Central Ohio."
3. ~~Services to lead with~~ Answered: commercial, municipal, 3+ acre residential. Confirm the 7-service lineup in brand guide §07.
4. **Domain.** Owned: `superiorlandsite.com` (DNS at SiteGround). Pages custom domain set in repo settings (Actions deploys ignore `public/CNAME`).
5. **Quote form destination.** Which email or phone should receive leads? Do they want text notifications?
6. **Proof points.** Years in business, insured/licensed, equipment list, Google reviews link, owner name and photo.
7. **Logo.** The chrome badge is retired in v0.2. A designer should finalize the simplified chevron mark and wordmark (see brand guide §02).
8. **Proof for B2B buyers.** Past commercial and municipal clients (names usable?), insurance / certificate of insurance on request, prequalifications, ODOT or other certifications, crew size.
9. **Logo + palette sign-off.** Heritage shield system (C3 badge + C2 treeline mark) with charcoal + Superior orange is now live on the site. Next: a designer produces final art.

---

## 2. Information architecture

```
/                         Home
/services/                Services overview
  /services/commercial-site-work/
  /services/municipal-right-of-way/
  /services/land-clearing/          (incl. forestry mulching)
  /services/ponds/
  /services/grading-stabilization/
  /services/drainage-culverts/
  /services/access-roads-drives/
/projects/                Project gallery (filterable by service)
  /projects/[slug]/       Before/after case studies (start with 4–6)
/service-area/            Map + town list
  /service-area/[town]/   Town pages (phase 2 SEO, only with real local content)
/about/                   Owner, equipment, insurance
/contact/                 Bid request form (project type, size, timeline) + phone
/404
```

**Global chrome.** Sticky iron header with the wordmark, nav and a copper **Request a Bid** button. On mobile, a **sticky bottom bar** with *Call* and *Request a Bid*. Footer with NAP (name, address, phone), service list, towns and a Facebook link.

---

## 3. Home page (as built, v0.2)

1. **Hero.** Commercial drone photo with an iron gradient. H1: *"Site work for commercial, municipal & acreage projects."* CTAs: **Request a Bid** and View Projects.
2. **Who we work with.** Three numbered audiences: contractors & developers, municipalities & townships, estates & acreage (3+ ac).
3. **Services.** Seven cards plus a "bigger scope?" bid card.
4. **Projects.** Four featured case studies, large format.
5. **How we work + fleet.** Site walk → written bid → execution → close-out, plus the equipment list.
6. **CTA band.** Dark contour-pattern band.
7. *Later:* client logos or references, testimonials, county map.

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
| **1. Brand** | v0.2 "Iron & Copper": palette, type, UI rules, logo direction, photo rules (`brand/`) | ✅ v0.2, awaiting owner sign-off |
| | Logo vector redraw (SVG, flat, knockout, icon) | ⬜ needs designer/owner |
| **2. Scaffold** | Astro 7 + Tailwind v4 + tokens, layout, all page templates, 8 services, 4 draft projects, Pages workflow | ✅ live on GitHub Pages |
| **3. Core pages** | Repositioned: Home, Services (×7), bid form, About (draft copy; needs owner facts) | 🟡 |
| **4. Proof** | 8 draft case studies (commercial, municipal, acreage); need owner details and more drone shots | 🟡 |
| **5. SEO/launch** | JSON-LD, sitemap, meta/OG images, analytics, domain + HTTPS, GBP link-up | ⬜ |
| **6. Post-launch** | Town pages, review widget, CRO audit against `~/.claude/cro-audit-rubric.md`, monthly project posts | ⬜ |

**Next step:** owner signs off on the v0.2 look, then answers §1 (name, counties, B2B proof points, domain).
