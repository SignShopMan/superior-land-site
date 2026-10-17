"""
Build every Superior logo variant from the master Illustrator export.

    python brand/tools/build_logos.py

Source:  brand/2026-superior-new-logo.svg (Illustrator, 3600x1872), simplified master:
         frame pre-cut around the tree and letters, no halo shapes.
         brand/tools/mark-source.svg: the earlier, unsimplified master. The compact mark needs
         parts the simplified master no longer has (the full four-tier tree, the frame's
         complete inner edge, the untrimmed field).
Output:  brand/logo/*.svg  (+ PNG previews in brand/logo/png/)

What it does
- Turns the master's white blades into real transparency with an SVG mask, so every file
  works on any background.
- Drops the hidden duplicate black SUPERIOR letters left in the master.
- Uses the master's outlined "LAND & SITE SERVICES"; if the master ever has it as live text
  again, outlines it from Termina Demi (Adobe Fonts, synced locally).
- Builds the compact mark (the badge's tree on the grade line, field + blades below), the
  horizontal and stacked lockups, and a wordmark-only version, all from the master's type.

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
MARK_SOURCE = ROOT / "brand/tools/mark-source.svg"
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

def _desc(src):
    text = re.search(r'translate\(([\d.]+) ([\d.]+)\)"><tspan[^>]*>([^<]+)<', src)
    size = float(re.search(r"font-size:\s*([\d.]+)px", src).group(1))
    return (float(text.group(1)), float(text.group(2)), text.group(3).replace("&amp;", "&"), size)


def load_master():
    """Simplified master: parts identified by fill class and position, not by order."""
    src = MASTER.read_text()
    body = src.split("</defs>", 1)[1]
    parts = []
    for attrs in re.findall(r"<path([^>]*)/>", body):
        cls = re.search(r'class="(\w+)"', attrs)
        d = re.search(r' d="([^"]+)"', attrs).group(1)
        parts.append((cls.group(1) if cls else "black", d, parse_path(d).bbox()))
    styles = dict(re.findall(r"\.(st\d+)\s*{[^}]*?fill:\s*(#[0-9a-fA-F]{3,6})", src))
    by_fill = lambda hexes: [(d, bb) for c, d, bb in parts if styles.get(c, "#000000").lower() in hexes]
    green = by_fill({"#243006"})
    orange = by_fill({"#e5641e"})
    white = by_fill({"#fff", "#ffffff"})
    black = by_fill({"#000000"})
    letter_boxes = {tuple(round(v) for v in bb) for _, bb in orange}
    black = [(d, bb) for d, bb in black if tuple(round(v) for v in bb) not in letter_boxes]  # stray duplicates
    frame = [d for d, bb in black if bb[3] - bb[2] > 200]
    glyphs = [d for d, bb in black if bb[3] - bb[2] <= 200]  # outlined LAND & SITE SERVICES
    return dict(
        field=next(d for d, bb in green if bb[2] > 1000),
        tree=next(d for d, bb in green if bb[3] < 1000),
        blades=white[0][0],
        frame=frame,
        letters=[d for d, _ in orange],
        desc=" ".join(glyphs) if glyphs else _desc(src),  # outlined paths, or live text to outline
    )


def load_mark_source():
    """Earlier, unsimplified master (by element order) for the compact mark's parts."""
    src = MARK_SOURCE.read_text()
    paths = [re.search(r' d="([^"]+)"', a).group(1) for a in re.findall(r"<path([^>]*)/>", src)]
    return dict(field=paths[1], frame=paths[2], tree_halo=paths[3], tree=paths[4], blades=paths[5])


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

    def ko(self, d, clip=None, stroke=None, halo=None):
        """halo=W knocks out the shape plus a W/2 margin around it (the gap around the tree)."""
        self.layers.append(dict(kind="ko", d=d, role=None, evenodd=False, clip=clip, stroke=stroke, halo=halo))

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
            halo = None if L.get("halo") is None else L["halo"] * k
            out.layers.append({**L, "d": xf(L["d"], k, tx, ty), "clip": clip, "stroke": stroke, "halo": halo})
        return out

    def render(self, scheme: dict, viewbox, under: str = "") -> str:
        x0, y0, w, h = viewbox
        clips: dict = {}

        def attrs(L, color="#000"):
            a = ' fill-rule="evenodd"' if L["evenodd"] else ""
            if L["stroke"]:
                a += f' fill="none" stroke="{color}" stroke-width="{L["stroke"]:.2f}" stroke-linejoin="round"'
            if L.get("halo"):
                a += f' stroke="{color}" stroke-width="{L["halo"]:.2f}" stroke-linejoin="round"'
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


def build_badge(m, ms):
    a = Art()
    if isinstance(m["desc"], str):
        desc_d = m["desc"]
    else:
        dx, dy, text, size = m["desc"]
        desc_d, _ = text_to_path(text, "demi", size, dx, dy)
    a.paint(m["field"], "field")
    for d in m["frame"]:
        a.paint(d, "frame", evenodd=True)
    a.ko(m["blades"])
    a.paint(m["blades"], "blade")
    a.paint(m["tree"], "tree")
    for d in m["letters"]:
        a.paint(d, "word")
    a.paint(desc_d, "desc")
    plate = plate_under([
        ([outer_edge(ms["frame"]), m["tree"], *m["frame"]], PAD),
        (m["letters"], 70),  # follow the letterforms closely
    ])
    return a, (240, 0, 3150, 1740), plate


# ---- compact mark: the badge's tree standing on the grade line, field + blades hung below
RULE_Y = 760.0  # grade line: the badge's tree, enlarged, stands on it
SHIFT = 1260.12 - RULE_Y  # lift the badge's below-the-rule parts up to meet it
CX = 1802.9  # shield centerline
SX = 0.64  # narrow the shield so the mark is compact (tree and blades keep their proportions)
FRAME_T = 64.0  # frame thickness, measured from the master
TREE_GAP = 61.0  # white gap between the tree and the frame, measured from the master
RULE_T = 26.83  # rule thickness in the master
TIP = complex(1790.17, 84.26)  # tree tip in the master
TREE_BASE = 496.0  # flat base of the badge's tree


def _mark_geometry(ms):
    inner = parse_path(ms["frame"]).continuous_subpaths()[1]
    # Narrow the shield, then grow it by half the frame thickness so a centered stroke
    # lands where the master's frame sits (keeps the frame an even weight all the way round).
    narrowed = inner.scaled(SX, 1, origin=complex(CX, 0))
    x0, x1, y0, y1 = narrowed.bbox()
    cy = (y0 + y1) / 2
    grow = complex(1 + FRAME_T / (x1 - x0), 1 + FRAME_T / (y1 - y0))
    mid = narrowed.scaled(grow.real, grow.imag, origin=complex(CX, cy))
    import numpy as np
    xs = [seg.point(t).real for seg in mid for t in np.linspace(0, 1, 400) if abs(seg.point(t).imag - RULE_Y) < 3]
    return mid, (min(xs) - FRAME_T / 2, max(xs) + FRAME_T / 2)  # rule caps the frame sides


def build_mark(m, ms):
    """m = simplified master (the badge's tree), ms = mark source (frame edge, untrimmed field)."""
    a = Art()
    mid, (rx0, rx1) = _mark_geometry(ms)
    mid_d = mid.d()
    lift = lambda d: xf(d, ty=-SHIFT)
    narrow = lambda d: parse_path(d).scaled(SX, 1, origin=complex(CX, 0)).d()
    # Grow the badge's tree from its tip until its base stands just above the grade line.
    # The small gap keeps tree, rule and field from fusing into one shape in the 1-color files.
    f = (RULE_Y - 18 - TIP.imag) / (TREE_BASE - TIP.imag)
    tree = parse_path(m["tree"]).scaled(f, f, origin=TIP).d()
    below = (1287 - SHIFT, 2000)
    field_d = lift(narrow(ms["field"]))
    a.paint(field_d, "field", clip=below)
    a.paint(lift(mid_d), "frame", clip=below, stroke=FRAME_T)
    a.paint(mid_d, "frame", clip=(-100, RULE_Y + 20), stroke=FRAME_T)
    a.ko(tree, halo=2 * TREE_GAP, clip=(-100, RULE_Y))
    a.paint(tree, "tree")
    a.paint(rect_d(rx0, RULE_Y, rx1 - rx0, RULE_T), "rule")
    # The narrowed V is steeper: scale the blades from their root and clip them to the field,
    # so they can never nick the frame or poke above the rule.
    blades = parse_path(ms["blades"]).scaled(0.85, 0.85, origin=complex(CX, 1591)).translated(complex(0, -SHIFT)).d()
    a.ko(blades, clip=field_d)
    a.paint(blades, "blade", clip=field_d)
    bottom = mid.bbox()[3] + FRAME_T / 2 - SHIFT
    w = (rx1 - rx0) + 2 * 90
    vb = (CX - w / 2, TIP.imag - 70, w, bottom - TIP.imag + 140)
    plate = (
        f'<clipPath id="ptop"><rect x="0" y="-200" width="3600" height="{RULE_Y + 230}"/></clipPath>'
        f'<clipPath id="pbot"><rect x="0" y="{RULE_Y}" width="3600" height="900"/></clipPath>'
        + plate_under([([mid_d], FRAME_T / 2 + PAD), ([tree], TREE_GAP + PAD)], "ptop")
        + plate_under([([lift(mid_d)], FRAME_T / 2 + PAD)], "pbot")
        + f'<rect x="{rx0 - PAD:.1f}" y="{RULE_Y - PAD}" width="{rx1 - rx0 + 2 * PAD:.1f}" height="{RULE_T + 2 * PAD:.1f}" rx="{PAD}" fill="{WHITE}"/>'
    )
    return a, vb, plate


# ---- lockups: all type comes straight from the master (arched SUPERIOR, outlined descriptor, rule)

def wordmark_parts(m):
    if isinstance(m["desc"], str):
        desc_d = m["desc"]
    else:
        dx, dy, text, size = m["desc"]
        desc_d, _ = text_to_path(text, "demi", size, dx, dy)
    rule = (614.9, 1260.12, 2376.0, RULE_T)
    boxes = [parse_path(d).bbox() for d in m["letters"]]
    box = (min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), rule[1] + rule[3])
    return m["letters"], desc_d, rule, box  # box = (x0, x1, y0, y1)


def add_wordmark(a: Art, m, k=1.0, tx=0.0, ty=0.0):
    letters, desc_d, rule, _ = wordmark_parts(m)
    for d in letters:
        a.paint(xf(d, k, tx, ty), "word")
    a.paint(xf(desc_d, k, tx, ty), "desc")
    x, y, w, h = rule
    a.paint(rect_d(x * k + tx, y * k + ty, w * k, h * k), "rule")


def build_wordmark(m):
    a = Art()
    add_wordmark(a, m)
    x0, x1, y0, y1 = wordmark_parts(m)[3]
    return a, (x0 - 60, y0 - 60, x1 - x0 + 120, y1 - y0 + 120)


def build_lockup_horizontal(m, ms):
    """Mark at left, a touch taller than the wordmark beside it; centered on each other."""
    mark, (mx, my, mw, mh), _ = build_mark(m, ms)
    x0, x1, y0, y1 = wordmark_parts(m)[3]
    word_h = y1 - y0
    k = 1.45 * word_h / mh  # the mark needs extra height to balance the heavy arched wordmark
    a = mark.transformed(k, -mx * k, -my * k)
    gap = 120
    tx = mw * k + gap - x0
    ty = (mh * k - word_h) / 2 - y0
    add_wordmark(a, m, 1.0, tx, ty)
    return a, (-30, -30, mw * k + gap + (x1 - x0) + 60, mh * k + 60)


def build_lockup_stacked(m, ms):
    """Mark centered over the wordmark: square-ish spaces, social avatars, shirts."""
    mark, (mx, my, mw, mh), _ = build_mark(m, ms)
    x0, x1, y0, y1 = wordmark_parts(m)[3]
    word_w, word_h = x1 - x0, y1 - y0
    k = 0.62 * word_w / mw
    a = mark.transformed(k, (word_w - mw * k) / 2 - mx * k, -my * k)
    gap = 110
    add_wordmark(a, m, 1.0, -x0, mh * k + gap - y0)
    return a, (-40, -40, word_w + 80, mh * k + gap + word_h + 80)


# --------------------------------------------------------------------------- output

def main():
    import resvg_py

    m = load_master()
    ms = load_mark_source()
    OUT.mkdir(exist_ok=True)
    (OUT / "png").mkdir(exist_ok=True)
    files = {}

    badge, bvb, bplate = build_badge(m, ms)
    mark, mvb, mplate = build_mark(m, ms)
    horizontal, hvb = build_lockup_horizontal(m, ms)
    stacked, svb = build_lockup_stacked(m, ms)
    wordmark, wvb = build_wordmark(m)

    for name, scheme in SCHEMES.items():
        files[f"superior-badge-{name}.svg"] = badge.render(scheme, bvb)
        files[f"superior-mark-{name}.svg"] = mark.render(scheme, mvb)
        files[f"superior-lockup-horizontal-{name}.svg"] = horizontal.render(scheme, hvb)
        files[f"superior-lockup-stacked-{name}.svg"] = stacked.render(scheme, svb)
        files[f"superior-wordmark-{name}.svg"] = wordmark.render(scheme, wvb)
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
    for old in assets.glob("superior-*.svg"):
        old.unlink()
    for name in ("superior-lockup-horizontal-reverse.svg", "superior-badge-reverse.svg"):
        (assets / name).write_text(files[name])
    print(f"wrote {len(files)} SVGs + PNG previews to {OUT.relative_to(ROOT)}, plus favicon and site assets")


if __name__ == "__main__":
    main()
