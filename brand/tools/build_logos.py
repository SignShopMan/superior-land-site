"""
Build every Superior logo file from the master Illustrator export.

    python brand/tools/build_logos.py

Source:  brand/2026-superior-new-logo.svg, one artboard holding six finished artworks in a
         2x3 grid, each on its own background panel:

                     left (x < 1800)        right (x >= 1800)
         row 0       mark, dark             mark, light
         row 1       logo, light            logo, dark
         row 2       wordmark, dark         wordmark, light

Output:  brand/logo/*.svg (+ PNG previews in brand/logo/png/), public/favicon.svg,
         public/apple-touch-icon.png, and the two site logos in src/assets/brand/.

What it does
- Cuts each artwork out of its panel and drops the panel. Anything painted in the panel's
  own color (white on a light panel, charcoal on a dark one) is a knockout, so it becomes
  real transparency (an SVG mask) and every file works on any background.
- Keeps the master's colors exactly for the light and dark versions, and derives 1-color
  black and white versions plus "plate" versions (full color on a white sticker plate) for
  colored truck doors and photos.
- Composes horizontal and stacked lockups from the master's mark and wordmark.

Requires: svgpathtools, numpy, resvg_py (PNG previews only).
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from svgpathtools import parse_path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "brand/2026-superior-new-logo.svg"
OUT = ROOT / "brand/logo"

WHITE = "#ffffff"
BLACK = "#000000"
CHARCOAL = "#1e2326"
PANEL_W, ROW_BOTTOMS = 1800, (1020, 2040)
LAYOUT = {  # (row, col) -> (artwork, treatment)
    (0, 0): ("mark", "dark"),
    (0, 1): ("mark", "light"),
    (1, 0): ("logo", "light"),
    (1, 1): ("logo", "dark"),
    (2, 0): ("wordmark", "dark"),
    (2, 1): ("wordmark", "light"),
}
PAD = 34  # plate margin, master units
MARGIN = 40  # breathing room around each artwork in its viewBox


# --------------------------------------------------------------------------- geometry

def xf(d: str, k: float = 1.0, tx: float = 0.0, ty: float = 0.0) -> str:
    """Bake scale + translate into path data, so masks never need transforms."""
    if k == 1.0 and tx == 0.0 and ty == 0.0:
        return d
    p = parse_path(d)
    if k != 1.0:
        p = p.scaled(k, k, origin=0j)
    return p.translated(complex(tx, ty)).d()


def hull_d(ds: list[str], samples: int = 40) -> str:
    """Convex hull of a set of paths: the silhouette of a die-cut sticker plate."""
    pts = []
    for d in ds:
        for seg in parse_path(d):
            for t in np.linspace(0, 1, samples):
                p = seg.point(t)
                pts.append((p.real, p.imag))
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in hull) + "Z"


# --------------------------------------------------------------------------- compositor

class Art:
    """Ordered layers. Paint layers keep their master color (recolorable per output);
    'ko' layers knock out every paint layer drawn before them."""

    def __init__(self):
        self.layers: list[dict] = []

    def paint(self, d, color, stroke=None):
        self.layers.append(dict(kind="paint", d=d, color=color, stroke=stroke))

    def ko(self, d, stroke=None):
        self.layers.append(dict(kind="ko", d=d, color=None, stroke=stroke))

    def extend(self, other: "Art", k=1.0, tx=0.0, ty=0.0):
        for L in other.layers:
            stroke = None if L["stroke"] is None else L["stroke"] * k
            self.layers.append({**L, "d": xf(L["d"], k, tx, ty), "stroke": stroke})
        return self

    def paint_paths(self):
        return [L["d"] for L in self.layers if L["kind"] == "paint"]

    def bbox(self):
        boxes = [parse_path(d).bbox() for d in self.paint_paths()]
        return (min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes))

    def render(self, recolor, viewbox, under: str = "") -> str:
        """recolor: master hex -> output hex."""
        x0, y0, w, h = viewbox
        body, masks = [], []
        for i, L in enumerate(self.layers):
            if L["kind"] != "paint":
                continue
            color = recolor(L["color"])
            a = f' fill="{color}"'
            if L["stroke"]:
                a += f' stroke="{color}" stroke-width="{L["stroke"]:.2f}" stroke-miterlimit="10"'
            kos = [K for K in self.layers[i + 1:] if K["kind"] == "ko"]
            if kos:
                cut = "".join(
                    f'<path d="{K["d"]}"' + (f' stroke="#000" stroke-width="{K["stroke"]:.2f}"' if K["stroke"] else "") + "/>"
                    for K in kos
                )
                masks.append(
                    f'<mask id="m{i}" maskUnits="userSpaceOnUse" x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}">'
                    f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#fff"/><g fill="#000">{cut}</g></mask>'
                )
                a += f' mask="url(#m{i})"'
            body.append(f'<path d="{L["d"]}"{a}/>')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}">'
            f"<defs>{''.join(masks)}</defs>{under}{''.join(body)}</svg>"
        )


def viewbox_for(art: Art, margin=MARGIN):
    x0, x1, y0, y1 = art.bbox()
    return (x0 - margin, y0 - margin, x1 - x0 + 2 * margin, y1 - y0 + 2 * margin)


def plate(art: Art, pad=PAD) -> str:
    """White sticker plate: convex hull of the artwork, grown by pad with round corners."""
    return (
        f'<path d="{hull_d(art.paint_paths())}" fill="{WHITE}" stroke="{WHITE}" '
        f'stroke-width="{2 * pad}" stroke-linejoin="round"/>'
    )


# --------------------------------------------------------------------------- master

def load_master() -> dict[tuple[str, str], Art]:
    src = MASTER.read_text()
    styles = {}
    for cls, body in re.findall(r"\.(st\d+)\s*{([^}]*)}", src):
        fill = re.search(r"fill:\s*(#[0-9a-fA-F]{3,6})", body)
        width = re.search(r"stroke-width:\s*([\d.]+)", body)
        styles[cls] = dict(fill=(fill.group(1) if fill else BLACK), stroke=(float(width.group(1)) if width else None))

    def norm(hexcolor):
        h = hexcolor.lower()
        return "#" + "".join(c * 2 for c in h[1:]) if len(h) == 4 else h

    arts: dict[tuple[str, str], Art] = defaultdict(Art)
    body = src.split("</defs>", 1)[1]
    for tag, attrs in re.findall(r"<(path|rect)\b([^>]*?)/?>", body):
        if tag == "rect":
            continue  # the six background panels
        cls = re.search(r'class="(\w+)"', attrs)
        st = styles.get(cls.group(1), {}) if cls else {}
        fill = norm(st.get("fill", BLACK))
        d = re.search(r' d="([^"]*)"', attrs).group(1)
        try:
            x0, x1, y0, y1 = parse_path(d).bbox()
        except ValueError:
            continue  # empty stray paths ("M x,y" with no segments)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        row = 0 if cy < ROW_BOTTOMS[0] else (1 if cy < ROW_BOTTOMS[1] else 2)
        col = 0 if cx < PANEL_W else 1
        artwork, treatment = LAYOUT[(row, col)]
        panel = WHITE if treatment == "light" else CHARCOAL
        art = arts[(artwork, treatment)]
        if fill == panel:
            art.ko(d)  # painted in the panel's own color = a knockout
        else:
            art.paint(d, fill, st.get("stroke"))
    return dict(arts)


# --------------------------------------------------------------------------- lockups

def normalize(art: Art) -> tuple[Art, float, float]:
    """Move an artwork so its bbox starts at 0,0. Returns (art, width, height)."""
    x0, x1, y0, y1 = art.bbox()
    return Art().extend(art, 1.0, -x0, -y0), x1 - x0, y1 - y0


def horizontal(mark: Art, word: Art) -> Art:
    m, mw, mh = normalize(mark)
    w, ww, wh = normalize(word)
    k = 1.3 * wh / mh  # mark a little taller than the wordmark
    gap = 0.3 * wh
    out = Art().extend(m, k, 0, 0)
    return out.extend(w, 1.0, mw * k + gap, (mh * k - wh) / 2)


def stacked(mark: Art, word: Art) -> Art:
    m, mw, mh = normalize(mark)
    w, ww, wh = normalize(word)
    k = 0.5 * ww / mw  # mark half the wordmark's width
    gap = 0.3 * wh
    out = Art().extend(m, k, (ww - mw * k) / 2, 0)
    return out.extend(w, 1.0, 0, mh * k + gap)


# --------------------------------------------------------------------------- output

def main():
    import resvg_py

    arts = load_master()
    for name, compose in (("lockup-horizontal", horizontal), ("lockup-stacked", stacked)):
        for t in ("light", "dark"):
            arts[(name, t)] = compose(arts[("mark", t)], arts[("wordmark", t)])

    same = lambda c: c
    files = {}
    for name in ("logo", "mark", "wordmark", "lockup-horizontal", "lockup-stacked"):
        light, dark = arts[(name, "light")], arts[(name, "dark")]
        vb = viewbox_for(light)
        files[f"superior-{name}-light.svg"] = light.render(same, vb)
        files[f"superior-{name}-dark.svg"] = dark.render(same, viewbox_for(dark))
        files[f"superior-{name}-black.svg"] = light.render(lambda c: BLACK, vb)
        files[f"superior-{name}-white.svg"] = light.render(lambda c: WHITE, vb)
        if name in ("logo", "mark"):
            files[f"superior-{name}-plate.svg"] = light.render(same, viewbox_for(light, MARGIN + PAD), plate(light))

    OUT.mkdir(exist_ok=True)
    (OUT / "png").mkdir(exist_ok=True)
    for old in list(OUT.glob("superior-*.svg")) + list((OUT / "png").glob("superior-*.png")):
        old.unlink()
    for fname, svg in files.items():
        (OUT / fname).write_text(svg)
        (OUT / "png" / fname.replace(".svg", ".png")).write_bytes(bytes(resvg_py.svg_to_bytes(svg_string=svg, width=1200)))

    # Favicon: the plated mark, squared up (reads on light and dark browser chrome)
    mark = arts[("mark", "light")]
    x0, y0, w, h = viewbox_for(mark, MARGIN + PAD)
    side = max(w, h)
    fav = mark.render(same, (x0 - (side - w) / 2, y0 - (side - h) / 2, side, side), plate(mark))
    (ROOT / "public/favicon.svg").write_text(fav)
    touch = fav.replace("<defs>", f'<rect x="-9999" y="-9999" width="99999" height="99999" fill="{CHARCOAL}"/><defs>', 1)
    (ROOT / "public/apple-touch-icon.png").write_bytes(bytes(resvg_py.svg_to_bytes(svg_string=touch, width=180)))

    assets = ROOT / "src/assets/brand"
    assets.mkdir(parents=True, exist_ok=True)
    for old in assets.glob("superior-*.svg"):
        old.unlink()
    for name in ("superior-lockup-horizontal-dark.svg", "superior-logo-dark.svg"):
        (assets / name).write_text(files[name])
    print(f"wrote {len(files)} SVGs + PNG previews to {OUT.relative_to(ROOT)}, plus favicon and site assets")


if __name__ == "__main__":
    main()
