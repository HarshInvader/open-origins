#!/usr/bin/env python3
"""Draw one illustration per news item, in the site's own visual language.

Each picture extends the home-page hero (a stromatolite cut through layered rock): limestone paper, a band of
layered rock along the bottom, sea or sky above, one or two objects for the paper's subject and one thin teal
accent mark. No text, no copied figures, nothing photographic. These are illustrations, labelled as such on the site.

Run from the repo root:  .venv/bin/python -I site/illustrate_news.py
Writes site/assets/news/<id>.webp at 900x600 (drawn at 2x, then reduced). Needs Pillow; build.py does not.
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


DRAW = {
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
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = json.loads((SITE / "news.json").read_text())["items"]
    total = 0
    for i, n in enumerate(items):
        fn = DRAW.get(n["id"])
        if not fn:
            print("no drawing for", n["id"])
            continue
        im = fn(1000 + i).resize((W // 2, H // 2), Image.LANCZOS)
        p = OUT / f"{n['id']}.webp"
        im.save(p, "WEBP", quality=80, method=6)
        total += p.stat().st_size
    print(f"{len(items)} pictures, {total / 1024:.0f} KB in total")


if __name__ == "__main__":
    main()
