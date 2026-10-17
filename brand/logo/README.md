# Superior logo files

Generated from the master `brand/2026-superior-new-logo.svg` by `brand/tools/build_logos.py`.
Don't hand-edit these: change the master and re-run the script.

All files are transparent SVG with every letter and shape outlined, so no fonts are needed.
Illustrator opens them directly; use File > Save As to make EPS or PDF for a sign shop.
`png/` has 1200px previews.

## Which file to use

| | Light background | Dark background (web dark mode, black or charcoal trucks) | Any color (green truck, photos) | One-color vinyl, embroidery, stamps |
|---|---|---|---|---|
| **Badge** (primary) | `superior-badge-color.svg` | `superior-badge-reverse.svg` | `superior-badge-plate.svg` | `superior-badge-black.svg` / `-white.svg` |
| **Mark** (compact) | `superior-mark-color.svg` | `superior-mark-reverse.svg` | `superior-mark-plate.svg` | `superior-mark-black.svg` / `-white.svg` |
| **Lockup** (horizontal) | `superior-lockup-color.svg` | `superior-lockup-reverse.svg` | (use the badge plate) | `superior-lockup-black.svg` / `-white.svg` |

- **Badge:** truck doors, job-site signs, the site footer and hero, social avatar. Minimum 140px or 1.25" wide.
- **Mark:** hard hats, embroidered hats, equipment decals, favicon, anywhere under 140px. The mark shows the full four-tier tree on the grade line, with the field and blades below.
- **Lockup:** site header, letterhead, bid covers, email signature, trailer sides. Minimum 36px or 0.4" tall.
- **Plate:** full color on a white sticker plate with a contour edge. This is the truck-door file when the paint isn't white, and the safe choice over photos.
- **Clear space:** the height of the "L" in LAND on every side.

## Colors

| | Hex | Use |
|---|---|---|
| Superior orange | `#E5641E` | SUPERIOR wordmark. Have the sign shop match it to the nearest Pantone and vinyl. |
| Forest | `#243006` | Tree and field on light backgrounds |
| Forest light | `#5F7B32` | Tree and field on dark backgrounds (forest is invisible on charcoal: 1.1:1) |
| Black | `#000000` | Frame, rule, descriptor on light backgrounds |
| Bone | `#F4F2EE` | Frame, rule, descriptor and blades on dark backgrounds |

## Type
- SUPERIOR: Termina Bold (arched in the badge, straight in the lockup)
- LAND & SITE SERVICES: Termina Demi
- Both are Adobe Fonts. They're outlined in every file here, so nobody downstream needs them installed.

## Rebuilding
```bash
python brand/tools/build_logos.py   # needs fonttools, uharfbuzz, svgpathtools, resvg_py
```
The script reads Termina from your local Adobe Fonts sync. It also writes `public/favicon.svg`, `public/apple-touch-icon.png`, and the two site logos in `src/assets/brand/`.
