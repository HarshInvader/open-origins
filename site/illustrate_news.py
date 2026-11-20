#!/usr/bin/env python3
"""Draw one illustration per news item, in the site's own visual language.

Each picture extends the home-page hero (a stromatolite cut through layered rock): limestone paper, a band of
layered rock along the bottom, sea or sky above, one or two objects for the paper's subject and one thin teal
accent mark. No text, no copied figures, nothing photographic. These are illustrations, labelled as such on the site.

Run from the repo root:  .venv/bin/python -I site/illustrate_news.py
Writes site/assets/news/<id>.webp and site/assets/library/<topic>.webp at 900x600 (drawn at 2x, then reduced).
Alt text lives in site/assets/news/alt.json and site/assets/library/alt.json. Needs Pillow; build.py does not.
"""
import json, math, random
from pathlib import Path
from PIL import Image, ImageDraw

SITE = Path(__file__).resolve().parent
OUT = SITE / "assets" / "news"
W, H = 1800, 1200  # drawn at 2x

PAPER = (241, 238, 230); SURF = (249, 247, 241); STONE = (226, 217, 198); SEA = (218, 231, 228); ICE = (230, 238, 240)
BA = (203, 148, 113); BB = (224, 211, 186); BC = (187, 170, 144); GRAIN = (156, 141, 118)
INK = (28, 27, 23); MUTED = (87, 84, 73); TEAL = (29, 102, 112); RUST = (164, 81, 43); LINE = (191, 183, 166)


def strata(d, top, rng, n=6):
    """Layered rock along the bottom: wavy bands like the hero's cut face."""
    cols = [BB, BA, BC, BB, BC, BA, BB, BC]
    ys = [top + i * (H - top) / n for i in range(n + 1)]
    ph = [rng.uniform(0, 6.28) for _ in range(n + 1)]
    def y_at(k, x):
        return ys[k] + 10 * math.sin(x / 210 + ph[k]) + 5 * math.sin(x / 77 + ph[k] * 2)
    for k in range(n):
        top_pts = [(x, y_at(k, x)) for x in range(0, W + 30, 30)]
        bot_pts = [(x, y_at(k + 1, x) if k + 1 < n else H) for x in range(W, -30, -30)]
        d.polygon(top_pts + bot_pts, fill=cols[k % len(cols)])
        d.line(top_pts, fill=(120, 90, 60), width=2)
    for _ in range(140):  # grains
        x, y = rng.uniform(0, W), rng.uniform(top + 20, H)
        r = rng.uniform(2, 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=GRAIN)


def surface(d, top, color=SEA, sky=PAPER):
    d.rectangle((0, 0, W, H), fill=sky)
    d.rectangle((0, top, W, H), fill=color)
    pts = [(x, top + 6 * math.sin(x / 90)) for x in range(0, W + 20, 20)]
    d.line(pts, fill=TEAL, width=3)


def base(seed, water=0.38, rock=0.72, color=SEA):
    rng = random.Random(seed)
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    surface(d, int(H * water), color)
    strata(d, int(H * rock), rng)
    return im, d, rng


def circ(d, x, y, r, fill=None, outline=INK, width=6):
    d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=width)


def poly(n, x, y, r, rot=-math.pi / 2):
    return [(x + r * math.cos(rot + 2 * math.pi * i / n), y + r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def hairpin(d, x, y, s=1.0, col=INK, w=10):
    """The site's mark: two strands joined by a loop."""
    d.line([(x - 40 * s, y + 220 * s), (x - 40 * s, y)], fill=col, width=w)
    d.line([(x + 40 * s, y + 220 * s), (x + 40 * s, y)], fill=col, width=w)
    d.arc((x - 75 * s, y - 120 * s, x + 75 * s, y + 30 * s), 125, 415, fill=col, width=w)
    for k in range(1, 6):
        yy = y + k * 36 * s
        d.line([(x - 40 * s, yy), (x + 40 * s, yy)], fill=MUTED, width=max(2, w // 3))


def beads(d, pts, r=16, fill=TEAL, outline=INK):
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=INK, width=5)
    for x, y in pts:
        circ(d, x, y, r, fill=fill, outline=outline, width=4)


def accent(d, pts):
    """The one thin teal accent mark."""
    d.line(pts, fill=TEAL, width=5, joint="curve")


# ------------------------------------------------------------------ one function per news item
def assembly(seed):
    im, d, rng = base(seed)
    x0 = 330
    for i in range(6):  # a chain of repeated blocks
        x = x0 + i * 190
        d.rounded_rectangle((x, 300, x + 150, 450), 16, fill=SURF if i % 2 else STONE, outline=INK, width=6)
        d.polygon(poly(5, x + 75, 375, 42), outline=INK, width=5)
        if i < 5:
            d.line([(x + 150, 375), (x + 190, 375)], fill=INK, width=6)
    accent(d, [(x0 - 20, 510), (x0 - 20, 540), (x0 + 360, 540), (x0 + 360, 510)])  # bracket the repeat
    return im


def protocell(seed):
    im, d, rng = base(seed)
    for x, y, r in [(620, 420, 170), (1000, 360, 120), (1260, 520, 90)]:
        circ(d, x, y, r, fill=SURF, outline=INK, width=6)
        circ(d, x, y, r - 22, outline=MUTED, width=4)
    d.arc((1380, 230, 1640, 470), 200, 340, fill=INK, width=6)  # a bilayer sheet curling closed
    d.arc((1402, 252, 1618, 448), 200, 340, fill=MUTED, width=4)
    accent(d, [(620 - 60, 420), (620 + 60, 420)])
    return im


def ryugu(seed):
    im, d, rng = base(seed, water=0.62, rock=0.8, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.62)), fill=PAPER)
    pts = [(900 + (260 + rng.uniform(-30, 30)) * math.cos(a), 360 + (190 + rng.uniform(-25, 25)) * math.sin(a)) for a in [i * 2 * math.pi / 22 for i in range(22)]]
    d.polygon(pts, fill=BC, outline=INK, width=6)
    for _ in range(9):
        x, y, r = 900 + rng.uniform(-170, 170), 360 + rng.uniform(-110, 110), rng.uniform(14, 30)
        circ(d, x, y, r, outline=MUTED, width=4)
    for i in range(5):  # five ring-shaped bases
        x = 560 + i * 170
        d.polygon(poly(6 if i % 2 == 0 else 5, x, 820, 40), fill=SURF, outline=INK, width=5)
    accent(d, [(500, 900), (1300, 900)])
    return im


def ribozyme_ice(seed):
    im, d, rng = base(seed, color=ICE)
    for _ in range(14):
        x, y = rng.uniform(80, W - 80), rng.uniform(500, 820)
        d.polygon(poly(6, x, y, rng.uniform(26, 60), rng.uniform(0, 1)), fill=SURF, outline=LINE, width=3)
    hairpin(d, 760, 330, 1.25)
    beads(d, [(980 + i * 70, 640) for i in range(7)], r=15, fill=SURF)
    accent(d, [(980, 690), (1330, 690)])
    return im


def bennu_sugars(seed):
    im, d, rng = base(seed, water=0.62, rock=0.8, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.62)), fill=PAPER)
    pts = [(900 + 330 * math.cos(a) * (1 + 0.08 * math.sin(3 * a)), 400 + 230 * math.sin(a)) for a in [i * 2 * math.pi / 30 for i in range(30)]]
    d.polygon(pts, fill=BB, outline=INK, width=6)
    for (x, y, r) in [(780, 360, 55), (980, 330, 45), (900, 480, 50), (1080, 450, 38)]:
        d.polygon(poly(5, x, y, r), fill=SURF, outline=INK, width=5)
    d.polygon(poly(5, 780, 360, 55), outline=TEAL, width=7)
    return im


def thioester(seed):
    im, d, rng = base(seed)
    for i in range(6):  # an RNA ladder
        y = 260 + i * 70
        d.line([(640, y), (900, y)], fill=MUTED, width=5)
    d.line([(640, 230), (640, 650)], fill=INK, width=10)
    d.line([(900, 230), (900, 650)], fill=INK, width=10)
    d.polygon([(1180, 300), (1240, 360), (1180, 420), (1120, 360)], fill=RUST, outline=INK, width=5)
    accent(d, [(1110, 360), (940, 260)])
    return im


def k218b(seed):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    strata(d, int(H * 0.8), rng)
    circ(d, 620, 380, 220, fill=SURF, outline=INK, width=6)  # star
    circ(d, 760, 420, 70, fill=BC, outline=INK, width=6)  # planet in transit
    d.line([(1050, 560), (1650, 560)], fill=INK, width=4)
    pts = [(1050 + i * 20, 470 + 12 * math.sin(i * 1.7) + rng.uniform(-6, 6)) for i in range(31)]
    d.line(pts, fill=MUTED, width=4)
    accent(d, [(1050, 470), (1650, 470)])  # a flat line
    return im


def vent_carbon(seed):
    im, d, rng = base(seed, water=0.12, rock=0.78)
    d.polygon([(780, 940), (860, 330), (960, 330), (1040, 940)], fill=BA, outline=INK, width=6)
    for k in range(5):
        y = 420 + k * 100
        d.line([(860 - k * 16, y), (960 + k * 16, y)], fill=(120, 80, 55), width=3)
    for i, (x, y) in enumerate([(1150, 300), (1260, 380), (1190, 470), (1320, 250)]):
        circ(d, x, y, 22, fill=SURF, outline=INK, width=5)
        circ(d, x + 34, y, 14, fill=SURF, outline=INK, width=4)
    accent(d, [(910, 310), (920, 250), (900, 190), (915, 130)])
    return im


def wetdry(seed):
    im, d, rng = base(seed, water=0.55, rock=0.75)
    d.rectangle((0, 0, W, int(H * 0.55)), fill=PAPER)
    circ(d, 1450, 230, 80, outline=RUST, width=6)
    for k in range(3):
        y = int(H * 0.55) - 30 - k * 34
        d.line([(200, y), (1600, y)], fill=TEAL if k == 0 else LINE, width=4 if k == 0 else 3)
    beads(d, [(500 + i * 85, 760 + 20 * math.sin(i)) for i in range(9)], r=17)
    return im


def trinucleotides(seed):
    im, d, rng = base(seed, color=ICE)
    for col, n in enumerate([1, 2, 4]):
        for j in range(n):
            x, y = 380 + col * 440, 240 + j * 110
            pts = [(x + i * 50, y) for i in range(6)]
            beads(d, pts, r=13, fill=SURF)
    accent(d, [(640, 300), (760, 300)])
    d.line([(1080, 300), (1200, 300)], fill=MUTED, width=4)
    return im


def bennu_capsule(seed):
    im, d, rng = base(seed, water=0.62, rock=0.8, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.62)), fill=PAPER)
    d.chord((620, 380, 1180, 760), 180, 360, fill=SURF, outline=INK, width=6)
    d.rectangle((620, 570, 1180, 620), fill=BC, outline=INK, width=6)
    hx, hy, ang = 1180, 570, math.radians(105)  # lid: a shallow cap hinged at the right rim, swung open
    cap = [(620 + 560 * t, 570 - 90 * math.sin(math.pi * t)) for t in [k / 24 for k in range(25)]]
    rot = [(hx + (x - hx) * math.cos(ang) - (y - hy) * math.sin(ang), hy + (x - hx) * math.sin(ang) + (y - hy) * math.cos(ang)) for x, y in cap]
    d.polygon(rot, fill=BC, outline=INK, width=6)
    for _ in range(26):
        x, y, r = rng.uniform(700, 1100), rng.uniform(470, 560), rng.uniform(8, 18)
        circ(d, x, y, r, fill=GRAIN, outline=None, width=0)
    accent(d, [(860, 420), (860, 340)])
    return im


def tree(d, x, top, bottom, spread, rng):
    d.line([(x, top + 140), (x, bottom)], fill=INK, width=10)
    for a in (-1, -0.45, 0.45, 1):
        d.line([(x, top + 160), (x + a * spread, top)], fill=INK, width=7)
    return [(x + a * spread, top) for a in (-1, -0.45, 0.45, 1)]


def luca_nature(seed):
    im, d, rng = base(seed, water=0.66, rock=0.74, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.66)), fill=PAPER)
    tree(d, 900, 180, int(H * 0.66), 420, rng)
    for k in (-1, 1):
        d.line([(900, int(H * 0.66)), (900 + k * 220, 1080)], fill=INK, width=6)
    circ(d, 900, int(H * 0.66), 22, fill=TEAL, outline=INK, width=5)
    return im


def heatflow(seed):
    im, d, rng = base(seed, water=0.2, rock=0.3)
    d.polygon([(820, 360), (980, 360), (930, 1150), (870, 1150)], fill=SEA, outline=INK, width=6)
    for i in range(14):  # beads gathering toward the cold end of the crack
        y = 1100 - (i ** 1.4) * 22
        y = max(400, y)
        circ(d, 900 + rng.uniform(-25, 25), y if i < 8 else 400 + rng.uniform(0, 80), 12, fill=TEAL, outline=INK, width=3)
    d.line([(1080, 1100), (1080, 420)], fill=RUST, width=5)
    accent(d, [(720, 400), (720, 1100)])
    return im


def rna_evolution(seed):
    im, d, rng = base(seed)
    for i, s in enumerate([0.65, 0.85, 1.05]):
        hairpin(d, 520 + i * 380, 330 + (1 - s) * 120, s, col=INK if i == 2 else MUTED, w=9)
    accent(d, [(640, 600), (1300, 600)])
    return im


def heteropoly(seed):
    im, d, rng = base(seed)
    cx, cy = 900, 400
    outer = poly(6, cx, cy, 220, 0)
    inner = poly(6, cx, cy, 110, math.pi / 6)
    d.polygon(outer, fill=SURF, outline=INK, width=6)
    for a, b in zip(outer, inner):
        d.line([a, b], fill=MUTED, width=4)
    d.polygon(inner, outline=INK, width=5)
    for p in outer:
        circ(d, p[0], p[1], 16, fill=STONE, outline=INK, width=4)
    accent(d, [(cx - 220, cy + 290), (cx + 220, cy + 290)])
    return im


def joyce_lineage(seed):
    im, d, rng = base(seed)
    for i, n in enumerate([3, 5, 8, 11]):
        y = 230 + i * 110
        beads(d, [(420 + k * 80, y) for k in range(n)], r=14, fill=SURF)
    accent(d, [(420, 640), (1220, 640)])
    return im


def luca_habitat(seed):
    im, d, rng = base(seed, water=0.1, rock=0.8)
    d.polygon([(1100, 960), (1170, 480), (1250, 480), (1320, 960)], fill=BA, outline=INK, width=6)
    tree(d, 640, 260, 860, 220, rng)
    accent(d, [(1210, 460), (1220, 400), (1200, 340)])
    return im


def pyrimidine(seed):
    im, d, rng = base(seed)
    d.polygon(poly(5, 900, 470, 120), fill=SURF, outline=MUTED, width=6)
    d.line([(820, 390), (980, 550)], fill=RUST, width=7)
    d.line([(980, 390), (820, 550)], fill=RUST, width=7)
    d.arc((500, 200, 1300, 900), 200, 340, fill=TEAL, width=6)  # the path goes around the free sugar
    circ(d, 530, 470, 18, fill=INK, outline=INK)
    circ(d, 1270, 470, 18, fill=TEAL, outline=INK, width=4)
    return im


def miller(seed):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    strata(d, int(H * 0.82), rng)
    circ(d, 900, 520, 250, fill=SEA, outline=INK, width=6)
    d.rectangle((860, 130, 940, 280), fill=PAPER, outline=INK, width=6)
    d.line([(820, 450), (870, 520), (920, 480), (980, 560)], fill=RUST, width=7)  # spark
    circ(d, 800, 450, 14, fill=INK); circ(d, 1000, 560, 14, fill=INK)
    accent(d, [(720, 660), (1080, 660)])
    return im


# ---- items added 2026-11-19 (July to November 2026 backfill)
def flagellum(seed):
    im, d, rng = base(seed)
    d.rounded_rectangle((420, 300, 860, 500), 100, fill=SURF, outline=INK, width=6)
    for k, r in enumerate((34, 24)):
        circ(d, 860, 400, r, outline=INK if k == 0 else MUTED, width=5)
    pts = [(860 + i * 14, 400 + 50 * math.sin(i / 6.5)) for i in range(60)]
    d.line(pts, fill=INK, width=7, joint="curve")
    accent(d, [(860, 560), (1680, 560)])
    return im


def mirror_stop(seed):
    im, d, rng = base(seed)
    d.line([(380, 300), (1420, 300)], fill=INK, width=10)  # template
    for i in range(10):
        x = 420 + i * 100
        d.line([(x, 300), (x, 380)], fill=MUTED, width=4)
    d.line([(380, 380), (1080, 380)], fill=INK, width=10)  # primer
    d.polygon(poly(5, 1120, 400, 44, math.pi / 2), fill=RUST, outline=INK, width=5)  # the mirror-image letter, flipped
    circ(d, 1260, 460, 26, fill=SURF, outline=MUTED, width=4)  # the next letter, left waiting
    accent(d, [(1180, 330), (1180, 470)])
    return im


def comets(seed):
    im, d, rng = base(seed, water=0.6, rock=0.78, color=SEA)
    d.rectangle((0, 0, W, int(H * 0.6)), fill=PAPER)
    d.polygon([(1180, int(H * 0.6) + 4), (1260, int(H * 0.6) - 40), (1420, int(H * 0.6) - 46), (1500, int(H * 0.6) + 4)], fill=BB, outline=INK, width=5)
    for i in range(7):
        x, y = 420 + i * 46, 210 + i * 30
        d.line([(x - 220, y - 110), (x, y)], fill=LINE, width=3)
    circ(d, 720, 400, 40, fill=STONE, outline=INK, width=6)
    for k, (dx, dy, r) in enumerate([(80, 40, 16), (110, 90, 12), (60, 100, 10), (140, 60, 9)]):
        circ(d, 720 + dx, 400 + dy, r, fill=STONE, outline=INK, width=4)
    accent(d, [(760, 430), (900, 530), (1040, 640)])
    return im


def fidelity(seed):
    im, d, rng = base(seed)
    hairpin(d, 420, 260, 1.05)
    pts = [(620 + i * 64, 420 + 26 * math.sin(i / 2.2)) for i in range(16)]
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=INK, width=5)
    for i, (x, y) in enumerate(pts):
        circ(d, x, y, 15, fill=RUST if i == 11 else SURF, outline=INK, width=4)
    accent(d, [(620, 520), (1580, 520)])
    return im


def side_reactions(seed):
    im, d, rng = base(seed)
    cx, cy, R = 760, 400, 170
    nodes = poly(4, cx, cy, R, -math.pi / 4)
    d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=INK, width=6)
    for x, y in nodes:
        circ(d, x, y, 30, fill=SURF, outline=INK, width=5)
    x0, y0 = nodes[0]
    d.rounded_rectangle((1260, 230, 1380, 350), 14, fill=STONE, outline=INK, width=6)  # the side product
    d.line([(x0 + 30, y0 - 10), (1255, 280)], fill=MUTED, width=5)
    accent(d, [(1260, 330), (1120, 400), (x0 + 34, y0 + 18)])  # the way back into the cycle
    return im


def microfossils(seed):
    im, d, rng = base(seed, water=0.3, rock=0.45)
    for _ in range(9):
        x, y, r = rng.uniform(150, 1650), rng.uniform(640, 1100), rng.uniform(22, 40)
        circ(d, x, y, r, fill=SURF, outline=INK, width=5)
    for k in range(3):
        x, y = 380 + k * 520, 800 + k * 60
        d.line([(x + i * 26, y + 14 * math.sin(i / 1.6)) for i in range(12)], fill=INK, width=8, joint="curve")
    d.ellipse((1180, 680, 1340, 740), fill=SURF, outline=INK, width=5)
    accent(d, [(240, 600), (1560, 600)])
    return im


def impact_window(seed):
    im, d, rng = base(seed, water=0.62, rock=0.7, color=SEA)
    d.rectangle((0, 0, W, int(H * 0.62)), fill=PAPER)
    for x, y, r in [(380, 160, 34), (620, 260, 22), (1500, 190, 40)]:
        circ(d, x, y, r, fill=BC, outline=INK, width=5)
        d.line([(x - r * 2.6, y - r * 2.2), (x - r, y - r * 0.8)], fill=LINE, width=4)
    for x in (300, 820, 1380):
        d.arc((x - 120, int(H * 0.7) - 40, x + 120, int(H * 0.7) + 80), 0, 180, fill=INK, width=6)
    hairpin(d, 1020, 470, 0.7, w=8)
    accent(d, [(900, 760), (1150, 760)])
    return im


def vents_rethought(seed):
    im, d, rng = base(seed, water=0.1, rock=0.8)
    d.polygon([(800, 960), (850, 600), (930, 600), (980, 960)], fill=BA, outline=INK, width=6)
    d.polygon([(1180, 960), (1210, 760), (1270, 760), (1300, 960)], fill=BA, outline=INK, width=6)
    for k in range(4):  # a weak, nearly flat gradient
        y = 380 + k * 60
        d.line([(200, y), (1600, y + 6)], fill=LINE, width=3)
    accent(d, [(890, 580), (900, 520), (885, 470)])
    return im


def polymerase_hand(seed):
    im, d, rng = base(seed)
    d.line([(560, 420), (1360, 420)], fill=INK, width=10)  # primer-template duplex
    d.line([(560, 480), (1180, 480)], fill=INK, width=10)
    for i in range(10):
        x = 600 + i * 64
        d.line([(x, 420), (x, 480)], fill=MUTED, width=4)
    d.arc((880, 200, 1440, 700), 290, 70, fill=INK, width=12)  # the palm and fingers wrapping around
    d.arc((940, 260, 1380, 640), 290, 70, fill=MUTED, width=5)
    circ(d, 1230, 480, 20, fill=SURF, outline=INK, width=5)  # the incoming letter
    accent(d, [(1180, 540), (1280, 540)])
    return im


def methanogen_root(seed):
    im, d, rng = base(seed, water=0.66, rock=0.74, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.66)), fill=PAPER)
    tips = tree(d, 900, 200, int(H * 0.66), 440, rng)
    for x, y in tips:
        circ(d, x, y, 14, fill=SURF, outline=INK, width=4)
    for k in range(5):  # methane bubbles rising from the base
        circ(d, 960 + 26 * math.sin(k), int(H * 0.66) - 80 - k * 70, 12 + k * 2, outline=MUTED, width=4)
    circ(d, 900, int(H * 0.66), 22, fill=TEAL, outline=INK, width=5)
    return im


def spectrum(seed):
    im, d, rng = base(seed, water=0.78, rock=0.8, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.78)), fill=PAPER)
    d.line([(240, 820), (1560, 820)], fill=INK, width=5)
    for i in range(30):
        x = 280 + i * 42
        h = 40 + 320 * abs(math.sin(i * 1.3)) * rng.uniform(0.3, 1) * (1 - i / 45)
        d.line([(x, 820), (x, 820 - h)], fill=MUTED if i % 5 else INK, width=6)
    accent(d, [(280, 400), (700, 470), (1100, 600), (1540, 700)])
    return im


def incomplete_kit(seed):
    im, d, rng = base(seed)
    missing = {(1, 2), (2, 4), (0, 5), (2, 1)}
    for r in range(3):
        for c in range(7):
            x, y = 420 + c * 140, 220 + r * 120
            if (r, c) in missing:
                d.polygon([(x + 50, y), (x + 100, y + 45), (x + 50, y + 90), (x, y + 45)], fill=RUST, outline=INK, width=5)
            else:
                d.rounded_rectangle((x, y, x + 100, y + 90), 12, fill=SURF, outline=INK, width=5)
    accent(d, [(420, 600), (1380, 600)])
    return im


def phosphite_lake(seed):
    im, d, rng = base(seed, water=0.6, rock=0.66, color=SEA)
    d.rectangle((0, 0, W, int(H * 0.6)), fill=PAPER)
    d.polygon([(260, int(H * 0.6) + 6), (560, 200), (680, 200), (980, int(H * 0.6) + 6)], fill=BC, outline=INK, width=6)
    d.polygon([(560, 200), (600, 240), (640, 220), (680, 200)], fill=BA, outline=INK, width=5)
    for k in range(6):
        x, y = 1100 + (k % 3) * 150, 780 + (k // 3) * 60
        d.polygon([(x, y - 30), (x + 32, y + 22), (x - 32, y + 22)], fill=SURF, outline=INK, width=4)
    accent(d, [(1040, int(H * 0.6) - 30), (1560, int(H * 0.6) - 30)])
    return im


def interstellar_sugar(seed):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    strata(d, int(H * 0.8), rng)
    for _ in range(40):
        x, y, r = rng.gauss(1100, 260), rng.gauss(380, 110), rng.uniform(30, 90)
        d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=SEA)
    beads(d, [(960, 420), (1040, 360), (1120, 420), (1200, 360)], r=20, fill=SURF)
    d.chord((260, 700, 520, 900), 180, 360, fill=SURF, outline=INK, width=6)  # a radio dish on the rock
    d.line([(390, 800), (390, int(H * 0.8))], fill=INK, width=8)
    accent(d, [(470, 720), (960, 430)])
    return im


def noisy_genomes(seed):
    im, d, rng = base(seed, water=0.66, rock=0.74, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.66)), fill=PAPER)
    tips = tree(d, 900, 260, int(H * 0.66), 420, rng)
    for tx, ty in tips:
        for k in range(5):
            y = ty - 40 - k * 32
            if rng.random() < 0.25:
                circ(d, tx, y, 10, outline=LINE, width=3)
            else:
                circ(d, tx, y, 10, fill=MUTED, outline=INK, width=3)
    circ(d, 900, int(H * 0.66), 22, fill=TEAL, outline=INK, width=5)
    return im


# ---- library topic pictures (site/assets/library/<topic>.webp); shown cropped to the middle band
def t_rna(seed):
    im, d, rng = base(seed, water=0.3, rock=0.72, color=ICE)
    hairpin(d, 700, 420, 0.95)
    beads(d, [(900 + i * 70, 600 + 20 * math.sin(i)) for i in range(8)], r=15, fill=SURF)
    accent(d, [(900, 660), (1390, 660)])
    return im


def t_blocks(seed):
    im, d, rng = base(seed, water=0.3, rock=0.72)
    for i, (n, x) in enumerate([(5, 560), (6, 800), (5, 1040), (6, 1280)]):
        d.polygon(poly(n, x, 600, 70), fill=SURF if i % 2 else STONE, outline=INK, width=6)
    accent(d, [(500, 710), (1340, 710)])
    return im


def t_space(seed):
    im, d, rng = base(seed, water=0.72, rock=0.78, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.72)), fill=PAPER)
    pts = [(900 + (230 + rng.uniform(-25, 25)) * math.cos(a), 560 + (150 + rng.uniform(-20, 20)) * math.sin(a)) for a in [i * 2 * math.pi / 22 for i in range(22)]]
    d.polygon(pts, fill=BC, outline=INK, width=6)
    for _ in range(7):
        circ(d, 900 + rng.uniform(-150, 150), 560 + rng.uniform(-80, 80), rng.uniform(12, 26), outline=MUTED, width=4)
    accent(d, [(560, 380), (700, 440)])
    return im


def t_vents(seed):
    im, d, rng = base(seed, water=0.1, rock=0.78)
    d.polygon([(800, 960), (860, 440), (960, 440), (1020, 960)], fill=BA, outline=INK, width=6)
    for x, y, r in [(1140, 560, 60), (1290, 640, 42)]:
        circ(d, x, y, r, fill=SURF, outline=INK, width=6)
    accent(d, [(910, 420), (920, 360), (900, 300)])
    return im


def t_life(seed):
    im, d, rng = base(seed, water=0.3, rock=0.72)
    for i in range(5):
        x = 470 + i * 190
        d.rounded_rectangle((x, 530, x + 150, 680), 16, fill=SURF if i % 2 else STONE, outline=INK, width=6)
        if i < 4:
            d.line([(x + 150, 605), (x + 190, 605)], fill=INK, width=6)
    accent(d, [(450, 720), (1390, 720)])
    return im


def t_luca(seed):
    im, d, rng = base(seed, water=0.72, rock=0.78, color=STONE)
    d.rectangle((0, 0, W, int(H * 0.72)), fill=PAPER)
    tree(d, 900, 360, int(H * 0.72), 420, rng)
    circ(d, 900, int(H * 0.72), 22, fill=TEAL, outline=INK, width=5)
    return im


TOPIC_DRAW = {"rna-world": t_rna, "building-blocks": t_blocks, "from-space": t_space, "vents-and-first-cells": t_vents,
              "telling-life-apart": t_life, "luca-and-the-tree-of-life": t_luca}


def vent_wall(seed):
    im, d, rng = base(seed, water=0.1, rock=0.82)
    d.rectangle((840, 200, 960, 960), fill=BA, outline=INK, width=6)  # the mineral wall
    for k in range(9):
        y = 240 + k * 80
        d.line([(840, y), (960, y + 20)], fill=(120, 80, 55), width=3)
    for i, y in enumerate((300, 420, 540, 660)):  # electrons: a quick straight run through the wall
        d.line([(560, y), (1240, y)], fill=INK, width=5)
        d.polygon([(1240, y - 14), (1268, y), (1240, y + 14)], fill=INK)
    for x, y in [(520, 760), (600, 820), (680, 780), (760, 840)]:  # ions: queued on one side
        circ(d, x, y, 26, fill=SURF, outline=INK, width=5)
    circ(d, 900, 800, 26, fill=SURF, outline=MUTED, width=4)  # one ion stuck inside the wall
    accent(d, [(490, 900), (500, 910), (780, 910), (790, 900)])  # bracket the queue
    return im



DRAW = {
    "vent-walls-pass-electrons-not-ions": vent_wall,
    "assembly-theory-collapses-to-dictionary-compression": assembly,
    "de-novo-protocell-membranes-without-a-template": protocell,
    "all-five-nucleobases-in-ryugu": ryugu,
    "a-small-polymerase-ribozyme-that-can-synthesize": ribozyme_ice,
    "sugars-including-ribose-in-bennu-samples-furukaw": bennu_sugars,
    "prebiotic-aminoacylation-of-rna-by-thioesters-si": thioester,
    "joint-reanalysis-of-k2-18b-jwst-spectra-luque-et": k218b,
    "carbon-reduction-under-vent-conditions": vent_carbon,
    "wet-dry-cycling-polymerizes-cyclic-nucleotides": wetdry,
    "trinucleotides-enable-exponential-rna-replication": trinucleotides,
    "amino-acids-and-nucleobases-in-asteroid-bennu-sa": bennu_capsule,
    "the-nature-of-the-last-universal-common-ancestor": luca_nature,
    "heat-flows-enrich-prebiotic-building-blocks": heatflow,
    "rna-catalyzed-evolution-of-catalytic-rna": rna_evolution,
    "molecular-assembly-indices-of-mineral-heteropoly": heteropoly,
    "joyce-polymerase-ribozyme-lineage": joyce_lineage,
    "the-physiology-and-habitat-of-luca": luca_habitat,
    "activated-pyrimidine-ribonucleotides": pyrimidine,
    "miller-1953-amino-acids-from-a-spark": miller,
    "first-bacterium-had-a-full-flagellum": flagellum,
    "a-mirror-image-letter-stops-rna-copying": mirror_stop,
    "comets-probably-did-not-deliver-cyanide": comets,
    "polymerase-ribozyme-copies-at-94-percent": fidelity,
    "side-reactions-need-not-doom-cycles": side_reactions,
    "lifeless-protocells-pass-microfossil-tests": microfossils,
    "impact-model-dates-the-rna-world-window": impact_window,
    "rethinking-alkaline-vents": vents_rethought,
    "first-structures-of-polymerase-ribozymes": polymerase_hand,
    "archaeal-ancestor-was-a-methanogen": methanogen_root,
    "assembly-index-from-flight-mass-spectra": spectrum,
    "luca-enzyme-set-was-incomplete": incomplete_kit,
    "volcanic-rocks-supply-phosphite": phosphite_lake,
    "first-sugar-in-interstellar-space": interstellar_sugar,
    "noisy-genome-training-reads-ancestral-traits": noisy_genomes,
}


def main():
    """Draws pictures that do not exist yet (pass --all to redraw every one).

    Seeds come from a hash of the id, so a picture does not change when items are added above it.
    The 19 pictures made before 2026-11-19 used the item's position instead; they are left as drawn.
    """
    import sys, zlib
    redraw = "--all" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    items = json.loads((SITE / "news.json").read_text())["items"]
    made, total = 0, 0
    for n in items:
        fn = DRAW.get(n["id"])
        p = OUT / f"{n['id']}.webp"
        if not fn:
            print("no drawing for", n["id"])
            continue
        if p.exists() and not redraw:
            continue
        im = fn(zlib.crc32(n["id"].encode())).resize((W // 2, H // 2), Image.LANCZOS)
        im.save(p, "WEBP", quality=80, method=6)
        made += 1
    lib = SITE / "assets" / "library"
    lib.mkdir(parents=True, exist_ok=True)
    for slug, fn in TOPIC_DRAW.items():
        fn(zlib.crc32(slug.encode())).resize((W // 2, H // 2), Image.LANCZOS).save(lib / f"{slug}.webp", "WEBP", quality=80, method=6)
    total = sum(f.stat().st_size for f in list(OUT.glob("*.webp")) + list(lib.glob("*.webp")))
    print(f"{made} news pictures drawn, {len(TOPIC_DRAW)} topic pictures; {total / 1024:.0f} KB in all news and library pictures")

if __name__ == "__main__":
    main()
