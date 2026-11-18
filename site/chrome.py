"""Site chrome shared by the Open Citizen Science projects, modelled on Open Indus.

The same file sits in open-mind/site and open-origins/site; keep them identical. It draws:
- the wordmark: the project name in single-stroke capitals on a 100-unit cap height (the same letter system as the Open
  Indus wordmark, with a round O), so it needs no font and scales cleanly;
- the header navigation: two grouped menus (Research, Resources) whose items carry a small line icon and a one-line
  description, then a filled call-to-action pill;
- the frieze: a band of the project's own signs under the home hero, the way Open Indus runs a band of Indus signs.
Stdlib only; the same input gives the same output on every build.
"""
import html

E = html.escape

# Single-stroke capitals, (width, path), in a box 100 units tall. Letters are set 37 units apart; a space is 88.
LETTERS = {
    "O": (62, "M31 0C12 0 2 22 2 50S12 100 31 100 60 78 60 50 50 0 31 0Z"),
    "P": (46, "M0 100V0H22C40 0 46 12 46 26C46 40 40 52 22 52H0"),
    "E": (42, "M42 0H0V100H42M0 50H34"),
    "N": (50, "M0 100V0L50 100V0"),
    "M": (62, "M0 100V0L31 64L62 0V100"),
    "I": (0, "M0 0V100"),
    "D": (52, "M0 0V100H8C38 92 52 70 52 50C52 30 38 8 8 0H0"),
    "R": (48, "M0 100V0H22C40 0 46 12 46 26C46 40 40 52 22 52H0M20 52L48 100"),
    "G": (60, "M57 16C51 5 42 0 31 0C12 0 2 22 2 50S12 100 31 100C49 100 59 88 59 68V56H34"),
    "S": (46, "M45 14C40 5 32 0 23 0C10 0 2 8 2 23C2 52 46 44 46 74C46 91 36 100 22 100C12 100 4 95 0 86"),
}
GAP, SPACE = 37, 88


def wordmark_inner(text):
    """Return (paths, width) for `text` in the 100-unit letter space."""
    x, parts = 0, []
    for ch in text.upper():
        if ch == " ":
            x += SPACE - GAP
            continue
        w, d = LETTERS[ch]
        parts.append(f'<path transform="translate({x} 0)" d="{d}"/>')
        x += w + GAP
    return "".join(parts), x - GAP


def wordmark_svg(text, inline=True, color="currentColor", width=10.5):
    """Inline: a header wordmark that takes the text colour. File: a standalone SVG for downloads."""
    inner, w = wordmark_inner(text)
    pad = 9
    vb = f"{-pad} {-pad} {w + 2 * pad} {100 + 2 * pad}"
    attrs = (f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"')
    if inline:
        return f'<svg class="wordmark" viewBox="{vb}" aria-hidden="true" focusable="false" {attrs}>{inner}</svg>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{(w + 2 * pad) / 2:.0f}" height="{(100 + 2 * pad) / 2:.0f}" '
            f'role="img" aria-label="{E(text)} wordmark" {attrs}><title>{E(text)}</title>{inner}</svg>\n')


def lockup_svg(text, mark_paths, color="#1C1B17", mark_color=None):
    """Mark and wordmark side by side, as one downloadable SVG."""
    inner, w = wordmark_inner(text)
    mark_color = mark_color or color
    total = 150 + w
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -14 {total + 20} 128" width="{(total + 20) / 2:.0f}" height="64" '
            f'role="img" aria-label="{E(text)}"><title>{E(text)}</title>'
            f'<g transform="translate(-6 -14) scale(4)" fill="none" stroke="{mark_color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{mark_paths}</g>'
            f'<g transform="translate(150 0)" fill="none" stroke="{color}" stroke-width="10.5" stroke-linecap="round" stroke-linejoin="round">{inner}</g></svg>\n')


# ---------------------------------------------------------------- navigation
ARROW = ('<svg class="ext-ic" viewBox="0 0 12 12" width="11" height="11" aria-hidden="true" focusable="false" fill="none" '
         'stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3.5 8.5L8.5 3.5M4.5 3.5H8.5V7.5"/></svg>')
CARET = ('<svg class="caret" viewBox="0 0 12 12" width="10" height="10" aria-hidden="true" focusable="false"><path d="M2.5 4.5 6 8l3.5-3.5" '
         'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
_I = lambda d: f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{d}</svg>'
ICONS = {
    "find": _I('<path d="M5 4h10l4 4v12H5z"/><path d="M9 12l2 2 4-4"/>'),
    "theory": _I('<circle cx="6" cy="7" r="2.2"/><circle cx="18" cy="7" r="2.2"/><circle cx="12" cy="18" r="2.2"/><path d="M8 8.2l2.8 7.6M16 8.2l-2.8 7.6M8.2 7h7.6"/>'),
    "map": _I('<path d="M4 6l5-2 6 2 5-2v14l-5 2-6-2-5 2z"/><path d="M9 4v14M15 6v14"/>'),
    "approach": _I('<circle cx="11" cy="11" r="6"/><path d="M15.5 15.5L20 20"/>'),
    "news": _I('<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M8 10h8M8 14h8M8 18h5"/>'),
    "tracker": _I('<path d="M5 19V13M12 19V6M19 19v-9"/>'),
    "data": _I('<ellipse cx="12" cy="6" rx="7" ry="2.5"/><path d="M5 6v12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V6M5 12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5"/>'),
    "logo": _I('<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 15l3-6 2 4 1.5-2L17 15"/>'),
    "files": _I('<path d="M4 7h6l2 2h8v10H4z"/>'),
    "code": _I('<path d="M9 8l-4 4 4 4M15 8l4 4-4 4"/>'),
    "family": _I('<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c2.5 2.4 3.6 5 3.6 8s-1.1 5.6-3.6 8c-2.5-2.4-3.6-5-3.6-8s1.1-5.6 3.6-8z"/>'),
}


def nav_items(groups, current, cta=("contribute.html", "Donate tokens")):
    """groups: [(label, [(href, title, line, icon), ...]), ...]. External links (http) get a small arrow."""
    out = []
    for gi, (label, items) in enumerate(groups):
        here = any(h == current for h, *_ in items)
        links = []
        for href, title, line, icon in items:
            ext = href.startswith("http") or href.startswith("../")
            cur = ' aria-current="page"' if href == current else ""
            links.append(f'<a href="{E(href)}"{cur}><i>{ICONS[icon]}</i><span><b>{E(title)}{ARROW if ext else ""}</b>'
                         f'<small>{E(line)}</small></span></a>')
        out.append(f'<li class="dd{" here" if here else ""}"><button type="button" aria-expanded="false" aria-controls="dd{gi}">'
                   f'{E(label)}{CARET}</button><div class="ddm" id="dd{gi}">{"".join(links)}</div></li>')
    href, label = cta
    cur = ' aria-current="page"' if current == href else ""
    out.append(f'<li class="nav-cta"><a href="{href}"{cur}>{E(label)}</a></li>')
    return "".join(out)


DD_JS = """
  // Grouped menus (Research, Resources): open on hover (CSS) or a tap; one open at a time; Escape or a tap elsewhere closes.
  var dds = [].slice.call(document.querySelectorAll('.site-nav .dd'));
  function ddClose(d) { d.classList.remove('open'); d.querySelector('button').setAttribute('aria-expanded', 'false'); }
  dds.forEach(function (d) {
    var b = d.querySelector('button');
    b.addEventListener('click', function (e) {
      e.stopPropagation(); var on = !d.classList.contains('open'); dds.forEach(ddClose);
      if (on) { d.classList.add('open'); b.setAttribute('aria-expanded', 'true'); }
    });
  });
  document.addEventListener('click', function (e) { dds.forEach(function (d) { if (!d.contains(e.target)) ddClose(d); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') dds.forEach(ddClose); });
"""


# ---------------------------------------------------------------- frieze
def frieze(signs, label, step=64, repeat=3):
    """A band of the project's signs, each drawn in a 48-unit box. Repeated so it fills wide screens."""
    seq = list(signs) * repeat
    w = step * len(seq)
    cells = "".join(f'<g transform="translate({i * step + (step - 48) / 2:.0f} 8)">{d}</g>' for i, d in enumerate(seq))
    return (f'<div class="band" role="img" aria-label="{E(label)}"><div class="band-in">'
            f'<svg viewBox="0 0 {w} 64" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round">{cells}</svg></div></div>')
