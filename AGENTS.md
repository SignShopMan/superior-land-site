## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)

## Project conventions

- Internal links must go through `url()` from `src/lib/url.ts` (GitHub Pages may serve under `/<repo>/`).
- Brand tokens live in `src/styles/global.css` `@theme` (source: `brand/tokens.css`). Orange buttons use ink text, never white (contrast).
- Business facts belong in `src/data/site.ts`; anything marked TODO is unconfirmed — don't present it as fact in new copy.
- Always render photos with `astro:assets` `<Image>` and pass `width` equal to the largest `widths` entry.
