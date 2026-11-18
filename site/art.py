"""Open Origins brand art. Read by site/build.py (stdlib only, same output on every build).

The look is deep time in rock: pale limestone paper, deep-sea teal for links, and iron-oxide rust used only in motifs
(banded iron formations, iron-sulfur vents). The mark is an RNA hairpin: one strand folded back on itself, the
molecule that may once have both carried information and copied it. The hero is a stromatolite cut in half:
layers laid down by mats of microbes, among the oldest widely accepted signs of life.
"""
import math, random

NAME_MARK = "an RNA hairpin"
MARK = ('<path d="M12 29V15M20 29V15"/><path d="M12 15a6 6 0 1 1 8 0"/>'
        '<path d="M12 19.5h8M12 24h8"/>')

W, H = 560, 300
HEADS = [(110, 74, 1.0), (285, 92, 1.25), (452, 70, 0.95)]  # centre x, half-width, growth rate of each dome


def _layer_y(x, k, wob):
    """Height of lamina k at x: domes that grow taller with each layer, over a gently uneven base."""
    y = 262 - k * 6.8 + wob(x) * (1 + k * 0.05)
    lift = 0.0
    for cx, hw, g in HEADS:
        w = hw * (0.55 + k * 0.022)
        d = (x - cx) / w
        if abs(d) < 1:
            lift = max(lift, g * k * 1.6 * (1 - d * d) ** 1.4)
    return y - lift


def _wob(rng):
    parts = [(rng.uniform(40, 160), rng.uniform(0, 6.283), rng.uniform(0.3, 1.0)) for _ in range(4)]
    return lambda x: sum(a * math.sin(6.283 * x / p + ph) for p, ph, a in parts)


def hero():
    rng = random.Random(11)
    n = 27
    lines = []
    for k in range(n):
        wob = _wob(random.Random(k * 7 + 3))
        lines.append([(x, _layer_y(x, k, wob)) for x in range(0, W + 1, 4)])
    bands = []
    for k in range(n - 1):
        lo, hi = lines[k], lines[k + 1]
        d = "M" + " L".join(f"{x},{y:.1f}" for x, y in lo) + " L" + " L".join(f"{x},{y:.1f}" for x, y in reversed(hi)) + "Z"
        cls = "ba" if k % 3 == 0 else ("bb" if k % 3 == 1 else "bc")
        bands.append(f'<path d="{d}" class="{cls}"/>')
    edges = "".join('<path d="M' + " L".join(f"{x},{y:.1f}" for x, y in l) + '" class="lam"/>' for l in lines[::2])
    grains = "".join(f'<circle cx="{rng.uniform(4, W - 4):.0f}" cy="{rng.uniform(270, 294):.0f}" r="{rng.uniform(0.7, 1.6):.1f}" class="gr"/>'
                     for _ in range(70))
    top = lines[-1]
    water = "M0,0 H560 V" + f"{top[-1][1]:.1f} " + " L".join(f"{x},{y:.1f}" for x, y in reversed(top)) + "Z"
    return f'''<figure class="hero-art"><svg viewBox="0 0 {W} {H}" role="img" aria-label="Illustration of a stromatolite cut in half: domed layers of rock, each laid down on top of the last by a mat of microbes">
<defs><clipPath id="slab"><rect x="0" y="0" width="{W}" height="{H}" rx="10"/></clipPath></defs>
<g clip-path="url(#slab)"><rect width="{W}" height="{H}" class="sed"/>
<path d="{water}" class="sea"/>
{"".join(bands)}{edges}<rect x="0" y="262" width="{W}" height="40" class="sed"/>{grains}</g>
<text x="14" y="26" class="tl">younger</text><text x="14" y="252" class="tl">older</text>
<path d="M30 40V230" class="ar"/><path d="M26 44l4-6 4 6" class="ar"/>
</svg>
<figcaption>Illustration. A stromatolite cut in half: each layer was laid down on the last by a mat of microbes. Rocks like this in Western Australia, about 3.4 billion years old, are among the oldest widely accepted signs of life. How the first cells arose before them is the open question.</figcaption></figure>'''
