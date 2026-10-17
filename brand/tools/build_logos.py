"""
Build every Superior logo variant from the master Illustrator export.

    python brand/tools/build_logos.py

Source:  brand/2026-superior-new-logo.svg (Illustrator, 3600x1872)
Output:  brand/logo/*.svg  (+ PNG previews in brand/logo/png/)

What it does
- Converts the master's white "knockout" shapes (tree halo, letter halos, text band,
  blades) into real transparency with SVG masks, so every file works on any background.
- Drops the hidden duplicate black SUPERIOR letters left in the master.
- Outlines the live "LAND & SITE SERVICES" text from Termina Demi (Adobe Fonts, synced
  locally), so no file depends on the font being installed.
- Builds the compact mark (full tree on the grade line over the field) and a horizontal
  lockup (mark + straight Termina Bold wordmark).

Requires: fonttools, uharfbuzz, svgpathtools, resvg_py (for PNG previews only).
"""

from __future__ import annotations

import re
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from svgpathtools import parse_path

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "brand/2026-superior-new-logo.svg"
OUT = ROOT / "brand/logo"
ADOBE = Path.home() / "Library/Application Support/Adobe/CoreSync/plugins/livetype/.w"
FONTS = {"demi": ADOBE / ".28986.otf", "bold": ADOBE / ".28991.otf"}

ORANGE = "#E5641E"
FOREST = "#243006"
FOREST_LIGHT = "#5F7B32"  # forest lifted for dark backgrounds: 3.3:1 on charcoal
BONE = "#F4F2EE"
BLACK = "#000000"
WHITE = "#FFFFFF"
CHARCOAL = "#1E2326"

SCHEMES = {
    # blade=None leaves the blades as true transparency; reverse paints them bone so they stay light
    "color": dict(frame=BLACK, field=FOREST, tree=FOREST, rule=BLACK, word=ORANGE, desc=BLACK, blade=None),
    "reverse": dict(frame=BONE, field=FOREST_LIGHT, tree=FOREST_LIGHT, rule=BONE, word=ORANGE, desc=BONE, blade=BONE),
    "black": dict(frame=BLACK, field=BLACK, tree=BLACK, rule=BLACK, word=BLACK, desc=BLACK, blade=None),
    "white": dict(frame=WHITE, field=WHITE, tree=WHITE, rule=WHITE, word=WHITE, desc=WHITE, blade=None),
}


# --------------------------------------------------------------------------- master parts

def load_master():
    src = MASTER.read_text()
    paths = [re.search(r' d="([^"]+)"', a).group(1) for a in re.findall(r"<path([^>]*)/>", src)]
    rects = re.findall(r'<rect[^>]*x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', src)
    band, rule = [tuple(map(float, r)) for r in rects]
    text = re.search(r'translate\(([\d.]+) ([\d.]+)\)"><tspan[^>]*>([^<]+)<', src)
    size = float(re.search(r"font-size:\s*([\d.]+)px", src).group(1))
    return dict(
        plate=paths[0],
        field=paths[1],
        frame=paths[2],
        tree_halo=paths[3],
        tree=paths[4],
        blades=paths[5],
        letters_hidden=paths[6:14],  # duplicate black letters: dropped
        letter_halos=paths[14:22],
        letters=paths[22:30],
        band=band,
        rule=rule,
        desc=(float(text.group(1)), float(text.group(2)), text.group(3).replace("&amp;", "&"), size),
    )


def text_to_path(text: str, font: str, size: float, x: float, y: float, tracking: float = 0.0):
    """Shape with HarfBuzz (kerning included) and return (svg path d, advance width)."""
    blob = hb.Blob.from_file_path(str(FONTS[font]))
    hbfont = hb.Font(hb.Face(blob))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})
    tt = TTFont(FONTS[font])
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    scale = size / tt["head"].unitsPerEm
    pen = SVGPathPen(gs)
    cursor = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gx = x + (cursor + pos.x_offset) * scale
        gs[order[info.codepoint]].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, y)))
        cursor += pos.x_advance + tracking / scale
    return pen.getCommands(), cursor * scale - tracking


def rect_d(x, y, w, h):
    return f"M{x:.2f},{y:.2f}h{w:.2f}v{h:.2f}h{-w:.2f}Z"


# --------------------------------------------------------------------------- compositor

def xf(d: str, k: float = 1.0, tx: float = 0.0, ty: float = 0.0) -> str:
    """Bake scale + translate into path data (masks and clips then need no transforms)."""
    if k == 1.0 and tx == 0.0 and ty == 0.0:
        return d
    p = parse_path(d)
    if k != 1.0:
        p = p.scaled(k, k, origin=0j)
    return p.translated(complex(tx, ty)).d()


class Art:
    """Ordered layers in final coordinates. 'paint' layers draw in a role color; 'ko' layers knock
    out every paint layer below them. clip = (ymin, ymax) band the layer is restricted to."""

    def __init__(self):
        self.layers: list[dict] = []

    def paint(self, d, role, evenodd=False, clip=None, stroke=None):
        self.layers.append(dict(kind="paint", d=d, role=role, evenodd=evenodd, clip=clip, stroke=stroke))

    def ko(self, d, clip=None, stroke=None):
        self.layers.append(dict(kind="ko", d=d, role=None, evenodd=False, clip=clip, stroke=stroke))

    def transformed(self, k, tx, ty) -> "Art":
        out = Art()
        for L in self.layers:
            c = L["clip"]
            if c is None:
                clip = None
            elif isinstance(c, str):
                clip = xf(c, k, tx, ty)
            else:
                clip = (c[0] * k + ty, c[1] * k + ty)
            stroke = None if L["stroke"] is None else L["stroke"] * k
            out.layers.append({**L, "d": xf(L["d"], k, tx, ty), "clip": clip, "stroke": stroke})
        return out

    def render(self, scheme: dict, viewbox, under: str = "") -> str:
        x0, y0, w, h = viewbox
        clips: dict = {}

        def attrs(L, color="#000"):
            a = ' fill-rule="evenodd"' if L["evenodd"] else ""
            if L["stroke"]:
                a += f' fill="none" stroke="{color}" stroke-width="{L["stroke"]:.2f}" stroke-linejoin="round"'
            if L["clip"]:
                cid = clips.setdefault(L["clip"], f"c{len(clips)}")
                a += f' clip-path="url(#{cid})"'
            return a

        body, masks = [], []
        for i, L in enumerate(self.layers):
            if L["kind"] != "paint" or scheme[L["role"]] is None:
                continue
            kos = [K for K in self.layers[i + 1 :] if K["kind"] == "ko"]
            color = scheme[L["role"]]
            a = attrs(L, color)
            if kos:
                cut = "".join(f'<path d="{K["d"]}"{attrs(K)}/>' for K in kos)
                masks.append(
                    f'<mask id="m{i}" maskUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{w}" height="{h}">'
                    f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fff"/><g fill="#000">{cut}</g></mask>'
                )
                a += f' mask="url(#m{i})"'
            fill = "" if L["stroke"] else f' fill="{color}"'
            body.append(f'<path d="{L["d"]}"{fill}{a}/>')
        clipdefs = "".join(
            f'<clipPath id="{cid}"><path d="{c}"/></clipPath>'
            if isinstance(c, str)
            else f'<clipPath id="{cid}"><rect x="{x0}" y="{c[0]:.2f}" width="{w}" height="{c[1] - c[0]:.2f}"/></clipPath>'
            for c, cid in clips.items()
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}">'
            f"<defs>{clipdefs}{''.join(masks)}</defs>{under}{''.join(body)}</svg>"
        )





# --------------------------------------------------------------------------- the three marks

PAD = 42  # sticker-plate margin, in master units


def plate_under(groups: list[tuple[list[str], float]], clip: str = "") -> str:
    """White sticker plate behind the logo for colored or dark surfaces (truck doors).
    groups = [(shapes, pad)]: each shape is filled and grown outward by its pad."""
    out = []
    for shapes, pad in groups:
        inner = "".join(f'<path d="{d}"/>' for d in shapes)
        out.append(f'<g fill="{WHITE}" stroke="{WHITE}" stroke-width="{pad * 2:.0f}" stroke-linejoin="round">{inner}</g>')
    body = "".join(out)
    return f'<g clip-path="url(#{clip})">{body}</g>' if clip else body


def outer_edge(frame_d: str) -> str:
    return frame_d.split("Z")[0] + "Z"  # first subpath = outside edge of the frame


def build_badge(m):
    a = Art()
    dx, dy, text, size = m["desc"]
    desc_d, _ = text_to_path(text, "demi", size, dx, dy)
    a.paint(m["field"], "field")
    a.paint(m["frame"], "frame", evenodd=True)
    a.ko(m["tree_halo"])
    a.paint(m["tree"], "tree")
    a.ko(rect_d(*m["band"]))
    a.paint(rect_d(*m["rule"]), "rule")
    a.ko(m["blades"])
    a.paint(m["blades"], "blade")
    for d in m["letter_halos"]:
        a.ko(d)
    for d in m["letters"]:
        a.paint(d, "word")
    a.paint(desc_d, "desc")
    plate = plate_under([
        ([outer_edge(m["frame"]), m["tree_halo"], rect_d(*m["rule"])], PAD),
        (m["letters"], 70),  # follow the letterforms, not their (much larger) halos
    ])
    return a, (240, 0, 3150, 1740), plate


# ---- compact mark: full tree standing on the grade line, field + blades hung below
RULE_Y = 880.0  # where the tree's trunk lands
SHIFT = 1260.12 - RULE_Y  # lift the badge's below-the-rule parts up to meet it
CX = 1802.9  # shield centerline
SX = 0.70  # narrow the shield so the mark is compact (tree and blades stay full size)
FRAME_T = 64.0  # frame thickness, measured from the master


def _mark_geometry(m):
    inner = parse_path(m["frame"]).continuous_subpaths()[1]
    # Narrow the shield, then grow it by half the frame thickness so a centered stroke
    # lands where the master's frame sits (keeps the frame an even weight all the way round).
    narrowed = inner.scaled(SX, 1, origin=complex(CX, 0))
    x0, x1, y0, y1 = narrowed.bbox()
    cy = (y0 + y1) / 2
    grow = complex(1 + FRAME_T / (x1 - x0), 1 + FRAME_T / (y1 - y0))
    mid = narrowed.scaled(grow.real, grow.imag, origin=complex(CX, cy))
    # outer edge of the frame at the rule, for the rule length and the plate
    import numpy as np
    xs = [seg.point(t).real for seg in mid for t in np.linspace(0, 1, 300) if abs(seg.point(t).imag - RULE_Y) < 3]
    rule_x0 = min(xs) - FRAME_T / 2  # rule caps the frame sides edge to edge
    rule_x1 = max(xs) + FRAME_T / 2
    return mid, (rule_x0, rule_x1)


def build_mark(m):
    a = Art()
    mid, (rx0, rx1) = _mark_geometry(m)
    mid_d = mid.d()
    lift = lambda d: xf(d, ty=-SHIFT)
    narrow = lambda d: parse_path(d).scaled(SX, 1, origin=complex(CX, 0)).d()
    below = (1287 - SHIFT, 2000)
    a.paint(lift(narrow(m["field"])), "field", clip=below)
    a.paint(lift(mid_d), "frame", clip=below, stroke=FRAME_T)
    a.paint(mid_d, "frame", clip=(-100, RULE_Y + 20), stroke=FRAME_T)
    a.ko(m["tree_halo"], clip=(-100, RULE_Y))
    a.paint(m["tree"], "tree", clip=(-100, RULE_Y))
    a.paint(rect_d(rx0, RULE_Y, rx1 - rx0, 26.83), "rule")
    # The narrowed V is steeper: scale the blades from their root and clip them to the field,
    # so they can never nick the frame or poke above the rule.
    field_d = lift(narrow(m["field"]))
    blades = parse_path(m["blades"]).scaled(0.85, 0.85, origin=complex(CX, 1591)).translated(complex(0, -SHIFT)).d()
    a.ko(blades, clip=field_d)
    a.paint(blades, "blade", clip=field_d)
    w = (rx1 - rx0) + 2 * 90
    vb = (CX - w / 2, 0, w, 1340)
    plate = (
        f'<clipPath id="ptop"><rect x="0" y="-200" width="3600" height="{RULE_Y + 230}"/></clipPath>'
        f'<clipPath id="pbot"><rect x="0" y="{RULE_Y}" width="3600" height="900"/></clipPath>'
        + plate_under([([mid_d], FRAME_T / 2 + PAD), ([m["tree_halo"]], PAD)], "ptop")
        + plate_under([([lift(mid_d)], FRAME_T / 2 + PAD)], "pbot")
        + f'<rect x="{rx0 - PAD:.1f}" y="{RULE_Y - PAD}" width="{rx1 - rx0 + 2 * PAD:.1f}" height="{26.83 + 2 * PAD:.1f}" rx="{PAD}" fill="{WHITE}"/>'
    )
    return a, vb, plate


def cap_height(font: str) -> float:
    return TTFont(FONTS[font])["OS/2"].sCapHeight / 1000


def build_lockup(m):
    """Mark at left with its grade line continuing into the wordmark's rule:
    SUPERIOR (Termina Bold) above the line, LAND & SITE SERVICES (Termina Demi) below."""
    mark, (mx, my, mw, mh), _ = build_mark(m)
    word_cap = 300.0
    above = word_cap + 40  # cap height + gap to the rule
    tree_tip = 26.0
    k = above / (RULE_Y - tree_tip)  # tree tip lines up with the top of the caps
    a = mark.transformed(k, -mx * k, -(tree_tip - 0) * k)
    rule_y = (RULE_Y - tree_tip) * k
    rule_h = 26.83 * k
    tx = mw * k + 60
    word_size = word_cap / cap_height("bold")
    word_d, word_w = text_to_path("SUPERIOR", "bold", word_size, tx, rule_y - 40)
    a.paint(word_d, "word")
    a.paint(rect_d(tx, rule_y, word_w, rule_h), "rule")
    desc = "LAND & SITE SERVICES"
    n = len(desc) - 1
    _, unit_w = text_to_path(desc, "demi", 1.0, 0, 0)
    track = 0.08  # em
    desc_size = word_w / (unit_w + track * n)
    desc_d, _ = text_to_path(desc, "demi", desc_size, tx, rule_y + rule_h + 34 + desc_size * cap_height("demi"), track * desc_size)
    a.paint(desc_d, "desc")
    bottom = max(rule_y + rule_h + 34 + desc_size * cap_height("demi"), (mh - tree_tip) * k)
    return a, (-12, -12, tx + word_w + 24, bottom + 24)


# --------------------------------------------------------------------------- output

def main():
    import resvg_py

    m = load_master()
    OUT.mkdir(exist_ok=True)
    (OUT / "png").mkdir(exist_ok=True)
    files = {}

    badge, bvb, bplate = build_badge(m)
    mark, mvb, mplate = build_mark(m)
    lockup, lvb = build_lockup(m)

    for name, scheme in SCHEMES.items():
        files[f"superior-badge-{name}.svg"] = badge.render(scheme, bvb)
        files[f"superior-mark-{name}.svg"] = mark.render(scheme, mvb)
        files[f"superior-lockup-{name}.svg"] = lockup.render(scheme, lvb)
    # Plated: full color on a white sticker plate, for dark backgrounds and colored truck doors
    files["superior-badge-plate.svg"] = badge.render(SCHEMES["color"], bvb, bplate)
    files["superior-mark-plate.svg"] = mark.render(SCHEMES["color"], mvb, mplate)

    for fname, svg in files.items():
        (OUT / fname).write_text(svg)
        png = resvg_py.svg_to_bytes(svg_string=svg, width=1200)
        (OUT / "png" / fname.replace(".svg", ".png")).write_bytes(bytes(png))
    # Site assets: square favicon from the plated mark (reads on light and dark browser chrome)
    x0, y0, w, h = mvb
    side = max(w, h)
    fav = files["superior-mark-plate.svg"].replace(
        f'viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}"',
        f'viewBox="{x0 - (side - w) / 2:.0f} {y0 - (side - h) / 2:.0f} {side:.0f} {side:.0f}"',
    )
    (ROOT / "public/favicon.svg").write_text(fav)
    touch = resvg_py.svg_to_bytes(svg_string=fav.replace("<defs>", f'<rect x="-9999" y="-9999" width="99999" height="99999" fill="{CHARCOAL}"/><defs>', 1), width=180)
    (ROOT / "public/apple-touch-icon.png").write_bytes(bytes(touch))
    assets = ROOT / "src/assets/brand"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("superior-lockup-reverse.svg", "superior-badge-reverse.svg"):
        (assets / name).write_text(files[name])
    print(f"wrote {len(files)} SVGs + PNG previews to {OUT.relative_to(ROOT)}, plus favicon and site assets")


if __name__ == "__main__":
    main()
