"""Outline the wordmark text from the body typeface (Open Indus Text, Instrument Sans base, OFL) into SVG paths.

Run when the name or the logo style changes:  .venv/bin/python site/make_logo.py
Writes site/logo_paths.json: for each word, a path in font units (cap height ~700, baseline at y=0, y down) and its width.
build.py reads that file with the stdlib only, so the build needs no font tools.
"""
import json, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

SITE = Path(__file__).resolve().parent
WORDS = json.loads(sys.argv[1]) if len(sys.argv) > 1 else None  # [[text, weight, tracking], ...]


def outline(text, weight, track):
    f = TTFont(SITE / "font-src" / f"OpenIndusText-{weight}.ttf")
    gs, cmap, hm = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    pen = SVGPathPen(gs)
    x = 0
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        x += hm[g][0] + track
    return {"d": pen.getCommands(), "w": round(x - track)}


out = {f"{t}|{w}": outline(t, w, k) for t, w, k in WORDS}
(SITE / "logo_paths.json").write_text(json.dumps(out))
print("wrote", list(out))
