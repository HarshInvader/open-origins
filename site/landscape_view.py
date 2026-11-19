"""Landscape snapshot block for the news page: who is working on what, and roughly how many.

Renders news.json "landscape" (written by open-citizen-science/tools/paperwatch/landscape.py; do not edit the numbers
by hand). Same file in open-mind, open-origins and indus-decipher; each site styles the .ls-* classes in its own CSS.
Inline SVG and CSS only.
"""
import datetime as _dt
import html

E = html.escape


def _rough(n):
    if n < 20:
        return str(n)
    if n < 1000:
        return str(int(round(n, -1)))
    return f"{int(round(n, -2)):,}"


def _date(s):
    d = _dt.date.fromisoformat(s)
    return f"{d.day} {d.strftime('%B %Y')}"


def _spark(t):
    ys, cs = t["years"], t["counts"]
    top = max(cs) or 1
    w, h, pad = 120, 34, 3
    xs = [pad + i * (w - 2 * pad) / (len(cs) - 1) for i in range(len(cs))]
    yy = [h - pad - c / top * (h - 2 * pad) for c in cs]
    full = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs[:-1], yy[:-1]))
    area = f"{xs[0]:.1f},{h - pad} " + full + f" {xs[-2]:.1f},{h - pad}"
    label = ", ".join(f"{y}: {c}" for y, c in zip(ys, cs))
    return (f'<svg class="ls-spark" viewBox="0 0 {w} {h}" role="img" aria-label="Papers per year, {E(label)} ({ys[-1]} so far)">'
            f'<title>Papers per year: {E(label)} ({ys[-1]} is the year so far)</title>'
            f'<polygon class="ls-sa" points="{area}"/><polyline class="ls-sl" points="{full}"/>'
            f'<polyline class="ls-sp" points="{xs[-2]:.1f},{yy[-2]:.1f} {xs[-1]:.1f},{yy[-1]:.1f}"/>'
            f'<circle class="ls-sd" cx="{xs[-2]:.1f}" cy="{yy[-2]:.1f}" r="2.4"/><circle class="ls-so" cx="{xs[-1]:.1f}" cy="{yy[-1]:.1f}" r="2.2"/></svg>'
            f'<span class="ls-years"><span>{ys[0]}</span><span>{ys[-1]}</span></span>')


def render(L, lib, lib_href="library.html#", tag="section"):
    """L: the landscape dict. lib: {library id: short label like 'Selte et al. 2026'}."""
    if not L or not L.get("directions"):
        return ""
    ds = L["directions"]
    top = max(d["authors"] for d in ds) or 1
    rows = []
    for i, d in enumerate(ds, 1):
        pct = max(2.0, 100 * d["authors"] / top)
        word = d["trend"]["word"]
        g = d["trend"]["growth"]
        tw = E(word) + (f'<span>{g * 100:+.0f}% a year, 2021–{d["trend"]["years"][-2]}</span>' if word in ("rising", "falling", "steady") else "")
        num = (f'<p class="ls-num"><b>~{_rough(d["authors"])}</b> authors <span>· ~{_rough(d["works"])} papers · '
               f'~{_rough(d["institutions"])} institutions</span></p>')
        groups = " · ".join(f'{E(g["name"])} <span class="ls-inst">({E(g["inst"])})</span>' for g in d.get("groups", []))
        refs = ", ".join(f'<a href="{lib_href}{E(x)}">{E(lib[x])}</a>' for x in d.get("now_ids", []) if x in lib)
        more = []
        if groups:
            more.append(f'<p><span class="ls-k">Leading groups</span>{groups}</p>')
        if d.get("now"):
            more.append(f'<p><span class="ls-k">Now</span>{E(d["now"])}{(" Read: " + refs + ".") if refs else ""}</p>')
        if d.get("us"):
            more.append(f'<p><span class="ls-k">Us</span>{E(d["us"])}</p>')
        q = d["query"]
        more.append(f'<details class="ls-q"><summary>Query</summary><p><code>{E(q["search"])}</code></p>'
                    f'<p>Filter: <code>{E(q["filter"])}</code>, published {E(q["window"][0])} to {E(q["window"][1])}. '
                    f'<a href="{E(q["url"])}" rel="nofollow">Check the count on OpenAlex</a> (the <code>meta.count</code> field).</p></details>')
        rows.append(
            f'<li class="ls-row" id="ls-{E(d["id"])}"><div class="ls-name"><h3><span class="ls-rank">{i}</span>{E(d["name"])}</h3><p class="ls-bet">{E(d["bet"])}</p></div>'
            f'<div class="ls-size"><div class="ls-bar" aria-hidden="true"><span style="width:{pct:.1f}%"></span></div>{num}</div>'
            f'<div class="ls-trend">{_spark(d["trend"])}<p class="ls-tw ls-{E(word.split()[0])}">{tw}</p></div>'
            f'<div class="ls-more">{"".join(more)}</div></li>')
    return (f'<{tag} class="landscape" aria-labelledby="landscape-h">'
            f'<p class="ls-kicker">The field now: who is working on what</p>'
            f'<h2 id="landscape-h">{E(L["headline"])}</h2>'
            f'<p class="ls-meta">Past 12 months, updated {E(_date(L["updated"]))}. Bars show distinct authors; lines show papers per year '
            f'(the dashed end is this year so far). These are estimates from keyword matches, not a census.</p>'
            f'<details class="ls-how"><summary>How we counted</summary><p>{E(L["method"])}</p></details>'
            f'<ol class="ls-list">{"".join(rows)}</ol></{tag}>')
