# Superior logo files

Generated from the master `brand/2026-superior-new-logo.svg` by `brand/tools/build_logos.py`.
The master holds the finished **logo**, **mark** and **wordmark** in **light** and **dark**
treatments. The script cuts each one out, turns knockouts into real transparency, and derives
everything else. Don't hand-edit these files: change the master and re-run the script.

All files are transparent SVG with every shape outlined, so no fonts are needed.
Illustrator opens them directly; use File > Save As to make EPS or PDF for a sign shop.
`png/` has 1200px previews.

## Which file to use

| | Light background | Dark background (web dark mode, black or charcoal trucks) | Any color (green truck, photos) | One-color vinyl, embroidery, stamps |
|---|---|---|---|---|
| **Logo** (primary) | `superior-logo-light.svg` | `superior-logo-dark.svg` | `superior-logo-plate.svg` | `superior-logo-black.svg` / `-white.svg` |
| **Mark** | `superior-mark-light.svg` | `superior-mark-dark.svg` | `superior-mark-plate.svg` | `superior-mark-black.svg` / `-white.svg` |
| **Wordmark** | `superior-wordmark-light.svg` | `superior-wordmark-dark.svg` | (use the logo plate) | `-black.svg` / `-white.svg` |
| **Horizontal lockup** | `superior-lockup-horizontal-light.svg` | `-dark.svg` | (use the logo plate) | `-black.svg` / `-white.svg` |
| **Stacked lockup** | `superior-lockup-stacked-light.svg` | `-dark.svg` | (use the logo plate) | `-black.svg` / `-white.svg` |

- **Logo:** truck doors, job-site signs, the site footer and hero, social avatar. Minimum 140px or 1.25" wide.
- **Mark:** hard hats, embroidered hats, equipment decals, favicon, anywhere the logo would be under 140px.
- **Wordmark:** the website header, and anywhere the shield won't fit or would repeat (next to the logo on the same truck, in a document footer). The dark wordmark keeps SUPERIOR orange with a white descriptor, matching the dark logo (the build derives it from the light wordmark; the master's all-white dark wordmark panel isn't used).
- **Horizontal lockup** (mark + wordmark side by side): letterhead, bid covers, email signature, trailer sides. Minimum 56px or 0.6" tall.
- **Stacked lockup** (mark over wordmark): square spaces: social avatars, shirt backs, yard signs.
- **Plate:** the light version on a white die-cut plate. Use it on truck doors when the paint isn't white, and over photos.
- **Clear space:** the height of the "L" in LAND on every side.

The two lockups are composed by the script from the master's mark and wordmark (mark at 1.3x
the wordmark's height beside it, or half its width above it). Everything else is the master's
art, unchanged.

## Colors

| | Hex | Use |
|---|---|---|
| Superior orange | `#E5641E` | SUPERIOR. Have the sign shop match it to the nearest Pantone and vinyl. |
| Forest | `#243006` | Tree and field, light treatment |
| Forest light | `#5F7B32` | Tree and field, dark treatment (forest is invisible on charcoal: 1.1:1) |
| Black | `#000000` | Frame, rule, descriptor, light treatment |
| White | `#FFFFFF` | Frame, rule, descriptor, blades, dark treatment |
| Charcoal | `#1E2326` | The dark background the dark treatment is designed on |

## Type
- SUPERIOR: Termina Bold, arched. LAND & SITE SERVICES: Termina Demi.
- Both are Adobe Fonts, outlined in the master and in every file here.

## Rebuilding
```bash
python brand/tools/build_logos.py   # needs svgpathtools, numpy, resvg_py
```
It also writes `public/favicon.svg`, `public/apple-touch-icon.png`, the share image `public/og-image.png`, and the two site logos in
`src/assets/brand/` (header wordmark, footer logo). If you rearrange the master's artboard, update the `LAYOUT` table at the
top of the script: it maps each panel of the 2x3 grid to an artwork and treatment.
