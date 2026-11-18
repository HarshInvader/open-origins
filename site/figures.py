"""Open Origins figures. Read by site/build.py (standard library only, same output on every build).

Every figure makes one point, and its title states it. Numbers are read from the repo's result files at build
time, never typed in by hand; each function names its source in a comment. Colours come from CSS variables
(site/brand.css), so every figure follows the light and dark themes. Figures that must reflow on a phone are
HTML; small fixed drawings are inline SVG sized close to 1:1 at phone width.
"""
import html
import math

e = html.escape

# ---------------------------------------------------------------- shared encodings
# Pathway-map step and hand-off glyphs. Shapes differ, so colour is never the only cue.
YIELD_WORD = {"demonstrated": "Yield from the setting's own inputs", "demonstrated_purified": "Yield only from purified inputs",
              "missing": "No published step", "unread": "Published, full text not read"}
VERDICT_WORD = {"continuous": "Passes", "unverified": "Passes, not fully checkable", "broken": "Breaks the rule",
                "blocked_by_missing_step": "Leads to or from a missing step"}
STAGE_SHORT = {"S1": "Small sugars", "S2": "Nucleotides", "S3": "RNA chains", "S4": "Template copying", "S5": "Sustained replication"}
# Plain names for each encoded step, paraphrased from map.json step names (experiments/pathway_map/map.json).
STEP_SHORT = {
    "C1": "Sugars from cyanide, trapped", "C2": "2-thiooxazole", "C3": "Pentose thiones", "C4": "Aminooxazolines",
    "C5": "Anhydrocytidine", "C6": "Cytidine cyclic phosphate", "C7": "Uridine by UV light", "C8": "Short RNA chains",
    "C9": "Template copying", "C10": "Sustained replication",
    "V1": "Formate and acetate", "V2": "Small sugars", "V3": "Nucleotides", "V4": "RNA chains", "V5": "Template copying",
    "V6": "Sustained replication",
    "P0": "Nucleotides", "P1": "Cyclic nucleotides", "P2": "Short RNA chains", "P3": "Template copying", "P4": "Sustained replication",
    "I1": "Triplet building blocks", "I2": "A 45-letter ribozyme", "I3": "QT45 copies itself", "I4": "Short RNAs multiply",
    "I5": "Sustained replication",
}
ROUTE_SHORT = {"cyanosulfidic": "Cyanosulfidic", "alkaline_vent": "Alkaline vent", "warm_pond": "Warm pond", "ice_rna": "Ice and RNA"}
ROUTE_ORDER = ["cyanosulfidic", "alkaline_vent", "warm_pond", "ice_rna"]


def node_glyph(status, size=18):
    """Step glyph: solid disc = yield from own inputs; ring = purified inputs only; dashed = missing; dotted with ? = unread."""
    r = size / 2 - 2
    c = size / 2
    if status == "demonstrated":
        g = f'<circle cx="{c}" cy="{c}" r="{r}" class="g-yes"/>'
    elif status == "demonstrated_purified":
        g = f'<circle cx="{c}" cy="{c}" r="{r - 0.6}" class="g-pur"/><circle cx="{c}" cy="{c}" r="{r * 0.36:.1f}" class="g-pdot"/>'
    elif status == "unread":
        g = (f'<circle cx="{c}" cy="{c}" r="{r - 0.4}" class="g-unread"/>'
             f'<text x="{c}" y="{c + 3.6}" text-anchor="middle" class="g-q">?</text>')
    else:
        g = f'<circle cx="{c}" cy="{c}" r="{r - 0.4}" class="g-miss"/>'
    return f'<svg class="ng" viewBox="0 0 {size} {size}" width="{size}" height="{size}" aria-hidden="true" focusable="false">{g}</svg>'


def link_glyph(verdict, horizontal=True, length=26):
    """Hand-off glyph: a cross on the line = breaks the rule; dashed line = blocked by a missing step; line with an open
    dot = passes but not fully checkable; plain solid line = passes."""
    w, h = (length, 14) if horizontal else (14, length)
    if horizontal:
        a, b, m = (1, 7), (w - 1, 7), (w / 2, 7)
    else:
        a, b, m = (7, 1), (7, h - 1), (7, h / 2)
    line = f'M{a[0]} {a[1]}L{b[0]} {b[1]}'
    if verdict == "broken":
        x, y = m
        g = (f'<path d="{line}" class="l-broken"/>'
             f'<path d="M{x - 4} {y - 4}L{x + 4} {y + 4}M{x + 4} {y - 4}L{x - 4} {y + 4}" class="l-x"/>')
    elif verdict == "blocked_by_missing_step":
        g = f'<path d="{line}" class="l-blocked"/>'
    elif verdict == "unverified":
        g = f'<path d="{line}" class="l-unv"/><circle cx="{m[0]}" cy="{m[1]}" r="3.2" class="l-dot"/>'
    else:
        g = f'<path d="{line}" class="l-ok"/>'
    return (f'<svg class="lg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" preserveAspectRatio="none" aria-hidden="true" '
            f'focusable="false">{g}</svg>')


def first_break(route):
    """The first hand-off, in route order, that does not pass: broken or blocked (experiments/pathway_map/RESULTS.md)."""
    for h in route["handoffs"]:
        if h["verdict"] in ("broken", "blocked_by_missing_step"):
            return h["id"]
    return None


def routes_in_order(m):
    by = {r["id"]: r for r in m["routes"]}
    return [by[k] for k in ROUTE_ORDER if k in by]


def map_totals(m):
    """Totals over the four routes from experiments/pathway_map/map.json. Hand-offs exclude the entry ones (22 in v1)."""
    steps = [s for r in m["routes"] for s in r["steps"]]
    hand = [h for r in m["routes"] for h in r["handoffs"] if not h["id"].startswith("entry")]
    count = lambda xs, k, v: sum(1 for x in xs if x[k] == v)
    return {
        "steps": len(steps), "yes": count(steps, "yield_status", "demonstrated"),
        "pur": count(steps, "yield_status", "demonstrated_purified"), "miss": count(steps, "yield_status", "missing"),
        "unread": count(steps, "yield_status", "unread"), "hand": len(hand),
        "cont": count(hand, "verdict", "continuous"), "unv": count(hand, "verdict", "unverified"),
        "broken": count(hand, "verdict", "broken"), "blocked": count(hand, "verdict", "blocked_by_missing_step"),
        "gaps": len(m["gaps"]),
    }


def fig(inner, title, caption, cls="", fid=""):
    """A figure whose visible title states its one claim."""
    idattr = f' id="{fid}"' if fid else ""
    return (f'<figure class="fig {cls}"{idattr}><p class="fig-t">{e(title)}</p>{inner}'
            f'<figcaption>{caption}</figcaption></figure>')


# ---------------------------------------------------------------- home 01: single steps, never joined
def fig_steps_vs_joins(m):
    """Unit chart. Source: experiments/pathway_map/map.json (26 steps, 22 hand-offs between steps)."""
    t = map_totals(m)
    steps = sorted((s for r in m["routes"] for s in r["steps"]), key=lambda s: ("demonstrated", "demonstrated_purified", "unread", "missing").index(s["yield_status"]))
    hand = [h for r in m["routes"] for h in r["handoffs"] if not h["id"].startswith("entry")]
    hand.sort(key=lambda h: ("continuous", "unverified", "broken", "blocked_by_missing_step").index(h["verdict"]))
    s_cells = "".join(node_glyph(s["yield_status"], 20) for s in steps)
    h_cells = "".join(f'<span class="ucell">{link_glyph(h["verdict"], True, 22)}</span>' for h in hand)
    n_yield = t["yes"] + t["pur"]
    inner = f'''<div class="units">
<div class="urow"><p class="ul"><b>{n_yield} of {t["steps"]}</b> steps have a published yield</p><div class="ucells">{s_cells}</div></div>
<div class="urow"><p class="ul"><b>{t["cont"]} of {t["hand"]}</b> joins between steps pass cleanly</p><div class="ucells joins">{h_cells}</div></div>
</div>
<ul class="key" aria-label="Key">
<li>{node_glyph("demonstrated", 14)} Yield from own inputs ({t["yes"]})</li><li>{node_glyph("demonstrated_purified", 14)} Purified inputs only ({t["pur"]})</li>
<li>{node_glyph("missing", 14)} No published step ({t["miss"] + t["unread"]})</li>
<li>{link_glyph("broken", True, 20)} Breaks the rule ({t["broken"]})</li><li>{link_glyph("blocked_by_missing_step", True, 20)} Missing step ({t["blocked"]})</li>
<li>{link_glyph("unverified", True, 20)} Passes, unchecked ({t["unv"]})</li></ul>'''
    return fig(inner, "Single steps work. The joins between them do not.",
               "Real data. Four proposed routes, written step by step from the papers and scored with our sealed rule. "
               "<span class=src>Source: experiments/pathway_map/map.json</span>", "units-fig")


# ---------------------------------------------------------------- ladder (home, tracker)
def fig_ladder(ladder):
    """L0-L4 rising rungs. Source: site/content.json ladder (statuses from the literature, docs/fable_plan.md)."""
    cls = {"largely met": "done", "partly met": "part", "not met": "open"}
    rungs = "".join(f'<li class="rung r{i + 1} {cls.get(s.lower(), "open")}"><b>{e(n)}</b><span>{e(s)}</span></li>'
                    for i, (lv, n, d, s) in enumerate(ladder))
    inner = (f'<ol class="ladder" aria-label="Five levels, lowest first">{rungs}</ol>'
             '<ul class="ladder-key" aria-label="Key"><li><i class="k done"></i>Largely met</li><li><i class="k part"></i>Partly met</li>'
             '<li><i class="k open"></i>Not met</li></ul>')
    return fig(inner, "Building blocks are largely solved. Self-copying is not.",
               "From the published literature, as of November 2026. Each rung needs the one below it.", "ladder-fig")


# ---------------------------------------------------------------- pathway map: compact (home) and full (map page)
def fig_map_compact(m):
    """One row per route. Source: experiments/pathway_map/map.json."""
    rows, positions = [], []
    for r in routes_in_order(m):
        fb = first_break(r)
        cells = ['<span class="cm-start" title="The setting\'s raw materials"></span>']
        hand = {h["to_step"] if "to_step" in h else h["id"].split("->")[1]: h for h in r["handoffs"]}
        for s in r["steps"]:
            h = hand.get(s["id"])
            if h:
                first = " first" if h["id"] == fb else ""
                cells.append(f'<span class="cm-l{first}" title="{e(h["id"])}: {e(VERDICT_WORD[h["verdict"]])}">{link_glyph(h["verdict"], True, 24)}</span>')
            cells.append(f'<span class="cm-n" title="{e(s["id"])} {e(STEP_SHORT.get(s["id"], ""))}: {e(YIELD_WORD[s["yield_status"]])}">{node_glyph(s["yield_status"], 18)}</span>')
        pos = [h["id"] for h in r["handoffs"]].index(fb)
        positions.append(pos)
        where = "before its first step" if pos == 0 else f"after step {pos}"
        rows.append(f'<li><p class="cm-name"><b>{e(ROUTE_SHORT[r["id"]])}</b> <span>breaks {e(where)}</span></p>'
                    f'<div class="cm-row">{"".join(cells)}</div></li>')
    inner = (f'<ol class="cmap">{"".join(rows)}</ol>'
             f'<ul class="key" aria-label="Key"><li>{node_glyph("demonstrated", 14)} Yield from own inputs</li>'
             f'<li>{node_glyph("demonstrated_purified", 14)} Purified inputs only</li><li>{node_glyph("missing", 14)} No published step</li>'
             f'<li>{link_glyph("broken", True, 20)} Breaks the rule</li><li>{link_glyph("blocked_by_missing_step", True, 20)} Missing step</li>'
             f'<li><span class="ring-key"></span> First break</li></ul>')
    title = "Every route breaks at or just after its first step" if max(positions) <= 1 else "Every route breaks before it reaches replication"
    return fig(inner, title,
               "Real data. Each row runs from the setting's raw materials (left) toward a self-copying molecule (right). "
               "<span class=src>Source: experiments/pathway_map/map.json</span>", "cmap-fig")


def fig_map_full(m):
    """The signature figure: four route columns aligned by stage. Source: experiments/pathway_map/map.json."""
    stages = list(m["stages"])
    head = '<div class="pm-corner"></div>' + "".join(
        f'<p class="pm-stage" style="grid-row:{i + 2}"><b>{e(s)}</b>{e(STAGE_SHORT[s])}</p>' for i, s in enumerate(stages))
    cols = []
    for r in routes_in_order(m):
        fb = first_break(r)
        sm = r["summary"]
        into = {h["id"].split("->")[1]: h for h in r["handoffs"]}
        groups = []
        started = False
        for st in stages:
            items = []
            for s in (x for x in r["steps"] if x["stage"] == st):
                h = into.get(s["id"])
                if not started:
                    items.append('<p class="pm-entry">Raw materials of the setting</p>')
                    started = True
                if h:
                    first = h["id"] == fb
                    codes = ", ".join(f'{c} {m["check_names"][c].lower()}' for c in h["flags"] if c.startswith("F"))
                    lab = codes if h["verdict"] == "broken" else VERDICT_WORD[h["verdict"]]
                    items.append(f'<div class="pm-h v-{h["verdict"]}{" first" if first else ""}">{link_glyph(h["verdict"], False, 26)}'
                                 f'<p>{"<b>First break.</b> " if first else ""}{e(lab)}</p></div>')
                src = s.get("source_url") or ""
                srcl = f' <a href="{e(src)}">Source</a>' if src else ""
                yt = s.get("yield_text") or ""
                body = f'<p class="pm-full">{e(s["name"])}</p>' + (f'<p class="pm-y">{e(yt)}</p>' if yt else "") + \
                       f'<p class="pm-y">{e(YIELD_WORD[s["yield_status"]])}.{srcl}</p>'
                items.append(f'<details class="pm-s y-{s["yield_status"]}" id="step-{e(s["id"])}"><summary>{node_glyph(s["yield_status"], 20)}'
                             f'<span><b>{e(STEP_SHORT.get(s["id"], s["id"]))}</b><small>{e(s["id"])} · {e(st)}</small></span></summary>'
                             f'<div class="pm-b">{body}</div></details>')
            if not items:
                items.append('<p class="pm-none">Not part of this route</p>' if not started else '<p class="pm-none">No step</p>')
            groups.append(f'<div class="pm-cell"><p class="pm-st">{e(st)} · {e(STAGE_SHORT[st])}</p>{"".join(items)}</div>')
        unexpl = sm["n_unexplained"]
        cols.append(f'<section class="pm-col" aria-label="{e(ROUTE_SHORT[r["id"]])} route"><header class="pm-head"><h3>{e(ROUTE_SHORT[r["id"]])}</h3>'
                    f'<p>{sm["n_steps"]} steps · {unexpl} of {sm["n_handoffs"]} hand-offs unexplained</p></header>{"".join(groups)}</section>')
    inner = f'<div class="pmap">{head}{"".join(cols)}</div>'
    return fig(inner, "No route runs from raw materials to a self-copying molecule",
               "Real data. Read each column top to bottom. Open a step for its full name, yield and source. "
               "Hand-offs are scored with the sealed compatibility rule (sha256 bfa572ed...). "
               "<span class=src>Source: experiments/pathway_map/map.json</span>", "pmap-fig")


def map_key():
    return (f'<ul class="key big" aria-label="Key"><li>{node_glyph("demonstrated", 16)} Yield published from the setting\'s own inputs</li>'
            f'<li>{node_glyph("demonstrated_purified", 16)} Yield published, but only from purified or bought inputs</li>'
            f'<li>{node_glyph("missing", 16)} No published step known to us</li><li>{node_glyph("unread", 16)} Published, but we could not open the full text</li>'
            f'<li>{link_glyph("broken", True, 22)} Hand-off breaks a hard rule</li><li>{link_glyph("blocked_by_missing_step", True, 22)} Hand-off leads to or from a missing step</li>'
            f'<li>{link_glyph("unverified", True, 22)} No rule broken, but some checks lack numbers</li></ul>')


def fig_gaps(m):
    """Stage-level gap ranking: bars to scale, out of 4 routes. Source: experiments/pathway_map/map.json gaps
    (routes_blocked_at_stage, routes_with_any_yield_at_stage), grouped as in experiments/pathway_map/RESULTS.md."""
    by = {}
    for g in m["gaps"]:
        st = g["stage"]
        d = by.setdefault(st, {"ranks": [], "blocked": g["routes_blocked_at_stage"], "yield": g["routes_with_any_yield_at_stage"]})
        d["ranks"].append(g["rank"])
    order = sorted(by, key=lambda s: min(by[s]["ranks"]))
    names = {"S5": "Sustained replication of a whole replicator", "S2": "Nucleotides from the setting's own raw materials",
             "S4": "Template copying", "S3": "RNA chains with purines, without bought nucleotides", "S1": "Free small sugars from one-carbon chemistry"}
    rows = []
    for st in order:
        d = by[st]
        lo, hi = min(d["ranks"]), max(d["ranks"])
        y = d["yield"]
        rows.append(f'<li><p class="gp-n"><span class="gp-r">{lo}-{hi}</span><b>{e(names[st])}</b> <span class="gp-s">{e(st)}</span></p>'
                    f'<div class="bar"><span class="bl">Routes blocked</span><span class="track"><span class="fill" style="width:{d["blocked"] / 4 * 100:.0f}%"></span></span><span class="bv">{d["blocked"]} of 4</span></div>'
                    f'<div class="bar"><span class="bl">Routes with any yield</span><span class="track"><span class="fill alt" style="width:{y / 4 * 100:.0f}%"></span></span><span class="bv">{y} of 4</span></div></li>')
    inner = f'<ol class="gaps">{"".join(rows)}</ol>'
    return fig(inner, "Sustained replication is the gap no route has touched",
               f"Real data. {len(m['gaps'])} gaps, ranked: first those no route has bridged even with purified inputs, then by routes blocked. "
               "Bars run from zero to all four routes. <span class=src>Source: experiments/pathway_map/map.json (gaps)</span>", "gaps-fig")


def handoff_table(m):
    rows = []
    for r in routes_in_order(m):
        for h in r["handoffs"]:
            codes = " ".join(h["flags"]) or "none"
            rows.append(f'<tr><th scope="row">{e(ROUTE_SHORT[r["id"]])}</th><td><code>{e(h["id"])}</code></td><td>{e(VERDICT_WORD[h["verdict"]])}</td>'
                        f'<td>{e(codes)}</td><td>{e(h.get("why") or "")}</td></tr>')
    return ('<div class="tablewrap"><table class="score"><thead><tr><th scope="col">Route</th><th scope="col">Hand-off</th><th scope="col">Verdict</th>'
            f'<th scope="col">Flags</th><th scope="col">Why</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


# ---------------------------------------------------------------- finding minis (260 x 150, shown 1:1)
def mini_planted(cases):
    """28 planted cases. Source: experiments/compat/planted_cases.csv and results.json (28/28: 16/16, 12/12)."""
    viol = [c for c in cases if c["expected"] != "{}"]
    twin = [c for c in cases if c["expected"] == "{}"]
    out = ['<svg class="mini" viewBox="0 0 260 150" role="img" aria-label="Twenty-eight planted test cases, all scored correctly: '
           f'{sum(c["ok"] == "True" for c in viol)} of {len(viol)} broken hand-offs flagged, {sum(c["ok"] == "True" for c in twin)} of {len(twin)} clean twins passed">']
    def grid(items, y0, mark):
        s = []
        for i, c in enumerate(items):
            x, y = 14 + (i % 8) * 18, y0 + (i // 8) * 18
            ok = c["ok"] == "True"
            s.append(f'<rect x="{x}" y="{y}" width="14" height="14" rx="3" class="{"m-cell" if ok else "m-cellbad"}"/>')
            if mark == "x":
                s.append(f'<path d="M{x + 4} {y + 4}l6 6m0-6l-6 6" class="m-x"/>')
            else:
                s.append(f'<path d="M{x + 3.5} {y + 7.5}l2.6 2.6 4.6-5.4" class="m-ok"/>')
        return "".join(s)
    out.append('<text x="14" y="16" class="m-t">Planted faults, flagged</text>')
    out.append(grid(viol, 24, "x"))
    out.append(f'<text x="168" y="44" class="m-n">{sum(c["ok"] == "True" for c in viol)}/{len(viol)}</text>')
    out.append('<text x="14" y="86" class="m-t">Clean twins, passed</text>')
    out.append(grid(twin, 94, "ok"))
    out.append(f'<text x="168" y="114" class="m-n">{sum(c["ok"] == "True" for c in twin)}/{len(twin)}</text>')
    out.append("</svg>")
    return "".join(out)


def mini_qt45(calc):
    """Population per cycle at the paper's decay rate and at a 1,000-day half-life.
    Source: experiments/qt45_numbers/results_calc.json (lambda_per_cycle_144d_any_fulllength = 0.429;
    sensitivity_half_life_days["1000"].lambda_cycle = 0.909)."""
    lam = calc["lambda_per_cycle_144d_any_fulllength"]
    lam1000 = calc["sensitivity_half_life_days"]["1000"]["lambda_cycle"]
    x0, x1, y0, y1, n = 34, 192, 128, 22, 5  # plot box; y0 = 0%, y1 = 100%
    X = lambda k: x0 + (x1 - x0) * k / n
    Y = lambda v: y0 - (y0 - y1) * v
    path = lambda l: "M" + " L".join(f"{X(k):.1f} {Y(l ** k):.1f}" for k in range(n + 1))
    dots = "".join(f'<circle cx="{X(k):.1f}" cy="{Y(lam ** k):.1f}" r="2.6" class="m-dot"/>' for k in range(n + 1))
    ticks = "".join(f'<text x="{X(k):.1f}" y="142" text-anchor="middle" class="m-s">{k}</text>' for k in range(n + 1))
    return f'''<svg class="mini" viewBox="0 0 260 150" role="img" aria-label="QT45 strand population over five copying cycles. At the published decay rate it falls to {lam:.0%} each cycle, near zero after five. Even if the RNA lasted 1,000 days it would still shrink, to {lam1000:.0%} per cycle. Break-even is 100%.">
<path d="M{x0} {y1}H{x1}" class="m-even"/><text x="{x1 + 4}" y="{y1 + 4}" class="m-s">break-even</text>
<path d="M{x0} {y0}H{x1}M{x0} {y0}V{y1 - 6}" class="m-axis"/>
<text x="{x0 - 5}" y="{y1 + 4}" text-anchor="end" class="m-s">100%</text><text x="{x0 - 5}" y="{y0 + 3}" text-anchor="end" class="m-s">0</text>
<path d="{path(lam1000)}" class="m-alt"/><text x="{x1 + 4}" y="{Y(lam1000 ** n) + 4:.1f}" class="m-s">t½ 1,000 d</text>
<path d="{path(lam)}" class="m-line"/>{dots}<text x="{X(1) + 6:.1f}" y="{Y(lam) - 6:.1f}" class="m-t">{lam:.0%} per cycle</text>
<text x="{x1 + 4}" y="{Y(lam ** n) + 2:.1f}" class="m-s">published</text>
{ticks}<text x="{x1 + 4}" y="142" class="m-s">cycles</text>
</svg>'''


def mini_handoffs(m):
    """Hand-off verdicts per route, entry included. Source: experiments/pathway_map/map.json."""
    out = ['<svg class="mini" viewBox="0 0 260 150" role="img" aria-label="Hand-offs per route: none passes cleanly in any of the four routes">']
    y = 18
    for r in routes_in_order(m):
        out.append(f'<text x="8" y="{y + 4}" class="m-t">{e(ROUTE_SHORT[r["id"]])}</text>')
        x = 104
        for h in r["handoffs"]:
            cx, cy = x + 6, y
            v = h["verdict"]
            if v == "broken":
                out.append(f'<path d="M{cx - 4} {cy - 4}l8 8m0-8l-8 8" class="m-x2"/>')
            elif v == "blocked_by_missing_step":
                out.append(f'<path d="M{cx - 6} {cy}h12" class="m-blk"/>')
            elif v == "unverified":
                out.append(f'<circle cx="{cx}" cy="{cy}" r="3.6" class="m-unv"/>')
            else:
                out.append(f'<path d="M{cx - 4} {cy}l3 3 5-6" class="m-ok"/>')
            x += 15
        y += 30
    out.append('<text x="8" y="140" class="m-s">each mark is one hand-off; none passes cleanly</text></svg>')
    return "".join(out)


# ---------------------------------------------------------------- QT45 full curve (findings, technical part)
# ---------------------------------------------------------------- deep time (findings: known)
def fig_deep_time():
    """Ages in million years ago. Source: experiments/findings_page/SOURCES.md (Wilde 2001; Bell 2015; Nutman 2016;
    Allwood 2006; Allwood 2018), as written in site/findings.json 'known'."""
    pts = [(4550, "Earth forms", "solid"), (4404, "Zircon: water present", "solid"), (4100, "Graphite in zircon", "disputed"),
           (3700, "Isua structures", "disputed"), (3480, "Dresser Formation", "solid"), (3430, "Strelley Pool stromatolites", "solid")]
    top, bot, a, b = 18, 262, 4600, 3400
    Y = lambda t: top + (a - t) / (a - b) * (bot - top)
    out = ['<svg class="dt" viewBox="0 0 340 280" role="img" aria-label="Timeline from 4,600 to 3,400 million years ago. Earth forms 4,550; zircon shows water by 4,404; '
           'graphite at 4,100 and Isua at 3,700 are disputed; accepted signs of life at Dresser 3,480 and Strelley Pool 3,430.">']
    out.append(f'<path d="M60 {top}V{bot}" class="d-axis"/>')
    for t in range(4600, 3399, -200):
        out.append(f'<path d="M56 {Y(t):.1f}h8" class="d-axis"/><text x="50" y="{Y(t) + 4:.1f}" text-anchor="end" class="d-s">{t:,}</text>')
    out.append(f'<rect x="58" y="{Y(3480):.1f}" width="4" height="{Y(3400) - Y(3480):.1f}" class="d-life"/>')
    last = -99
    for t, lab, kind in pts:
        y = Y(t)
        ly = max(y, last + 17)
        last = ly
        dot = f'<circle cx="60" cy="{y:.1f}" r="5" class="{"d-dot" if kind == "solid" else "d-disp"}"/>'
        lead = f'<path d="M66 {y:.1f}L80 {ly:.1f}H86" class="d-lead"/>' if abs(ly - y) > 1 else f'<path d="M66 {y:.1f}H86" class="d-lead"/>'
        txt = f'<text x="90" y="{ly + 4:.1f}" class="d-t">{t:,} · {e(lab)}{" (disputed)" if kind != "solid" else ""}</text>'
        out.append(dot + lead + txt)
    out.append(f'<text x="14" y="{top - 6}" class="d-s">million years ago</text></svg>')
    return fig("".join(out), "Signs of life are accepted from 3,480 million years ago, a billion years after Earth formed",
               "Real data from the papers cited in the text below. Open circles are claims still disputed.", "dt-fig")


def fig_bennu():
    """Bennu sample contents. Source: experiments/findings_page/SOURCES.md (Glavin 2025: 33 amino acids, 14 of the 20 used
    in proteins, all five nucleobases; Furukawa 2025: ribose found, deoxyribose not)."""
    rows = [("Amino acids used in proteins", 14, 20, "14 of 20"), ("Nucleobases of DNA and RNA", 5, 5, "5 of 5")]
    bars = "".join(f'<div class="bar"><span class="bl">{e(l)}</span><span class="track"><span class="fill" style="width:{v / n * 100:.0f}%"></span></span>'
                   f'<span class="bv">{e(t)}</span></div>' for l, v, n, t in rows)
    inner = (f'<div class="chart">{bars}</div><ul class="checks"><li><span class="ck yes" aria-hidden="true"></span>Ribose, the sugar of RNA, found</li>'
             '<li><span class="ck no" aria-hidden="true"></span>Deoxyribose, the sugar of DNA, not found</li>'
             '<li><span class="ck yes" aria-hidden="true"></span>33 amino acids in all</li></ul>')
    return fig(inner, "An asteroid sample holds most of life's building blocks",
               "Real data. Asteroid Bennu's returned sample (Glavin et al. 2025; Furukawa et al. 2025). Bars run from zero.", "bennu-fig")


def first_year(when):
    s = when.split(";")[0].strip()
    if not s[:4].isdigit():
        return None
    return int(s[:4])


def fig_tried(tried):
    """When each approach in findings.json 'tried' started, and how it went. Source: site/findings.json (sourced in
    experiments/findings_page/SOURCES.md). An entry with no checked first year sits on the 'earlier' stub."""
    order = ["part", "weak", "open", "wait"]
    word = {"part": "Works in part", "weak": "Weakened", "open": "Still open", "wait": "Can't test yet"}
    x0, x1, a, b = 52, 330, 1920, 2030
    X = lambda yr: x0 + (yr - a) / (b - a) * (x1 - x0)
    stacks = {}
    pts = []
    for t in tried:
        yr = first_year(t["when"])
        x = 22 if yr is None else X(yr)
        key = round(x / 9)
        k = stacks.get(key, 0)
        stacks[key] = k + 1
        pts.append((x, 104 - k * 11, t["status"], t["approach"], yr))
    def mark(x, y, st):
        if st == "part":
            return f'<circle cx="{x:.1f}" cy="{y}" r="4.4" class="t-part"/>'
        if st == "weak":
            return f'<circle cx="{x:.1f}" cy="{y}" r="4" class="t-weak"/><path d="M{x - 4:.1f} {y}a4 4 0 0 0 8 0z" class="t-weakf"/>'
        if st == "open":
            return f'<circle cx="{x:.1f}" cy="{y}" r="4" class="t-open"/>'
        return f'<circle cx="{x:.1f}" cy="{y}" r="4" class="t-wait"/>'
    out = [f'<svg class="tl" viewBox="0 0 340 134" role="img" aria-label="{len(tried)} approaches from the 1920s to 2026. '
           + "; ".join(f'{sum(1 for t in tried if t["status"] == k)} {word[k].lower()}' for k in order) + '. None joins the steps into one route.">']
    out.append(f'<path d="M{x0} 112H{x1}" class="d-axis"/><path d="M12 112H34" class="d-axis dash"/>')
    out.append('<text x="23" y="128" text-anchor="middle" class="d-s">earlier</text>')
    for yr in range(1920, 2031, 20):
        out.append(f'<path d="M{X(yr):.1f} 112v5" class="d-axis"/><text x="{X(yr):.1f}" y="128" text-anchor="middle" class="d-s">{yr}</text>')
    for x, y, st, name, yr in pts:
        out.append(f'<g><title>{e(name)}{", " + str(yr) if yr else ""}: {e(word[st])}</title>{mark(x, y, st)}</g>')
    out.append("</svg>")
    keys = "".join(f'<li><svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true">{mark(6, 6, k)}</svg>{e(word[k])} '
                   f'({sum(1 for t in tried if t["status"] == k)})</li>' for k in order)
    out.append(f'<ul class="key" aria-label="Key">{keys}</ul>')
    n_part = sum(1 for t in tried if t["status"] == "part")
    return fig("".join(out), f"A century of attempts: {n_part} of {len(tried)} work in part, none joins up",
               "Real data. One mark per approach listed below, placed at its first dated paper and stacked when years are close.", "tl-fig")


# ---------------------------------------------------------------- how we test (home, approach)
ICONS = {
    "seal": '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><path d="M12 14v2"/>',
    "plant": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.8" fill="currentColor"/>',
    "null": '<rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1" fill="currentColor"/><circle cx="15" cy="15" r="1" fill="currentColor"/><circle cx="15" cy="9" r="1" fill="currentColor"/><circle cx="9" cy="15" r="1" fill="currentColor"/>',
    "red": '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9.5 9.5l5 5M14.5 9.5l-5 5"/>',
    "pub": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 12h6M9 16h6"/>',
}


def icon(k):
    return f'<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false">{ICONS[k]}</svg>'


def fig_pipeline(n_sealed, n_planted):
    """The path every test takes. Counts: docs/prereg/HASHES.txt lines; experiments/compat/results.json n_cases."""
    steps = [("seal", "Seal", f"Hash the plan and pass mark first. {n_sealed} sealed so far."),
             ("plant", "Plant", f"The method must find a planted answer. The rule caught {n_planted} of {n_planted}."),
             ("null", "Null", "Compare with random data that keeps the real data's shape."),
             ("red", "Red team", "Someone who did not build it tries to break it."),
             ("pub", "Publish", "Write it up either way, negatives included.")]
    lis = "".join(f'<li>{icon(k)}<b>{e(t)}</b><span>{e(d)}</span></li>' for k, t, d in steps)
    return fig(f'<ol class="pipe">{lis}</ol>', "A claim counts only after five steps, in this order",
               "The path every claim takes, in order. A result counts only after the last step.", "pipe-fig")


# ---------------------------------------------------------------- data and papers (home)
def depth_of(s):
    s = s.lower()
    if "full text" in s and "not opened" not in s:
        return "full"
    if "abstract" in s:
        return "abstract"
    return "meta"


def fig_ledger(papers, files):
    """Paper ledger by how deeply each claim was checked. Source: docs/PAPERS.csv (checked_against column)."""
    groups = [("full", "Full text read"), ("abstract", "Abstract read"), ("meta", "Title and authors only")]
    rows = []
    for k, lab in groups:
        n = sum(1 for p in papers if depth_of(p["checked_against"]) == k)
        tiles = "".join(f'<i class="pt {k}"></i>' for _ in range(n))
        rows.append(f'<div class="lrow"><p class="ul"><b>{n}</b> {e(lab)}</p><div class="ptiles">{tiles}</div></div>')
    flist = "".join(f'<li><a href="{e(href)}" download>{e(name)}</a><span>{e(what)} · {e(size)}</span></li>' for name, href, what, size in files)
    inner = (f'<div class="ledger">{"".join(rows)}</div>')
    figure = fig(inner, f"All {len(papers)} papers resolve by DOI; claims are checked against the text where we could read it",
                 "Real data. One tile per paper. <span class=src>Source: docs/PAPERS.csv</span>", "ledger-fig")
    return figure, f'<ul class="dl">{flist}</ul>'


# ---------------------------------------------------------------- help (home, contribute)
def fig_board(tasks):
    """Live board counts. Source: board/board.db (read-only)."""
    cols = [("done", "Done"), ("claimed", "In progress"), ("open", "Open")]
    out = []
    for k, lab in cols:
        ts = [t for t in tasks if t["status"] == k]
        cards = "".join(f'<li class="bc {k}" title="#{t["id"]} {e(t["title"])}"><span>#{t["id"]}</span> {e(t["title"])}</li>' for t in ts)
        out.append(f'<div class="bcol"><p class="bh"><b>{len(ts)}</b> {e(lab)}</p><ol>{cards}</ol></div>')
    n_open = sum(1 for t in tasks if t["status"] == "open")
    return fig(f'<div class="board">{"".join(out)}</div>', f"{n_open} tasks are open for an agent to claim today",
               "Real data from the live task board, built into this page. <span class=src>Source: board/board.db</span>", "board-fig")


# ---------------------------------------------------------------- theories
SETTINGS = [
    ("pond", "Warm ponds on land", "Pools on volcanic land dry out and refill. Drying joins nucleotides into chains."),
    ("uv", "Sunlit streams and pools", "Cyanosulfidic chemistry: UV light on shallow water fed by minerals and cyanide."),
    ("ice", "Ice", "Freezing concentrates RNA in thin brine channels and slows its breakdown."),
    ("vent", "Vents on the sea floor", "Warm alkaline water meets acidic sea across mineral walls."),
]


def setting_svg(k):
    """Illustration only: where each scenario sets the chemistry. Same layered-rock language as the hero."""
    ground = ('<path d="M0 78 C40 74 80 80 120 76 S180 74 200 77 V120 H0Z" class="s-b1"/>'
              '<path d="M0 92 C50 88 90 95 140 90 S190 89 200 92 V120 H0Z" class="s-b2"/>'
              '<path d="M0 106 C40 103 100 109 150 104 S190 104 200 106 V120 H0Z" class="s-b3"/>')
    if k == "pond":
        body = ('<rect width="200" height="120" class="s-sky"/>' + ground +
                '<path d="M62 78 Q100 98 138 78 Z" class="s-water"/><path d="M58 76 Q100 104 142 76" class="s-tide"/>'
                '<circle cx="160" cy="26" r="11" class="s-sun"/>'
                '<path d="M80 84h4M90 88h4M102 89h4M114 86h4" class="s-chain"/>')
    elif k == "uv":
        rays = "".join(f'<path d="M{150 - i * 16} {30 + i * 4} L{118 - i * 22} {72}" class="s-ray"/>' for i in range(3))
        body = ('<rect width="200" height="120" class="s-sky"/>' + ground +
                '<path d="M20 78 C60 84 120 82 180 78 L180 80 C120 86 60 88 20 80Z" class="s-water"/>'
                f'<circle cx="160" cy="24" r="11" class="s-sun"/>{rays}'
                '<path d="M30 92l8 4 6-6 8 5" class="s-min"/>')
    elif k == "ice":
        body = ('<rect width="200" height="120" class="s-ice"/>'
                '<path d="M0 30 L60 34 L52 70 L0 66Z M70 26 L140 30 L134 74 L62 70Z M150 30 L200 28 V72 L144 74Z M0 76 L48 78 L40 120 H0Z M58 80 L130 82 L136 120 H50Z M142 82 L200 80 V120 H146Z" class="s-cryst"/>'
                '<path d="M56 30 L58 74 L54 120 M138 26 L140 76 L142 120 M0 72 H200" class="s-brine"/>')
    else:
        body = ('<rect width="200" height="120" class="s-sea"/>' + ground.replace("78", "98").replace("92", "104").replace("106", "112") +
                '<path d="M86 100 L92 52 Q100 44 108 52 L114 100Z" class="s-chim"/><path d="M92 70h16M90 84h20" class="s-lam"/>'
                '<path d="M100 46 C96 36 104 28 100 16" class="s-plume"/>')
    return f'<svg viewBox="0 0 200 120" class="set" aria-hidden="true" focusable="false">{body}</svg>'


def fig_settings():
    cards = "".join(f'<li>{setting_svg(k)}<b>{e(t)}</b><span>{e(d)}</span></li>' for k, t, d in SETTINGS)
    return fig(f'<ul class="settings">{cards}</ul>', "Three scenarios put the chemistry at the surface; one puts it on the sea floor",
               "Illustration. Not to scale.", "settings-fig")


def fig_coverage(m, scen_text):
    """Which stages each scenario has any published yield for. Source: map.json routes[].summary.stages_with_yield and
    steps (purified or not). Explains / cannot-yet text: site/content.json map.scenarios."""
    head = "".join(f'<th scope="col"><abbr title="{e(STAGE_SHORT[s])}">{e(s)}</abbr><span>{e(STAGE_SHORT[s])}</span></th>' for s in m["stages"])
    rows = []
    for r in routes_in_order(m):
        cells = []
        for st in m["stages"]:
            sts = [s["yield_status"] for s in r["steps"] if s["stage"] == st]
            if "demonstrated" in sts:
                k = "demonstrated"
            elif "demonstrated_purified" in sts:
                k = "demonstrated_purified"
            elif not sts:
                k = None
            else:
                k = "unread" if "unread" in sts else "missing"
            cells.append(f'<td>{node_glyph(k, 18) if k else "<span class=na>not in route</span>"}<span class="vh">{e(YIELD_WORD[k]) if k else ""}</span></td>')
        t = scen_text.get(r["id"], {})
        rows.append(f'<tr><th scope="row">{e(ROUTE_SHORT[r["id"]])}</th>{"".join(cells)}'
                    f'<td class="ex">{e(t.get("explains", ""))}</td><td class="ex">{e(t.get("gap", ""))}</td></tr>')
    inner = (f'<div class="tablewrap"><table class="cov"><thead><tr><th scope="col">Scenario</th>{head}<th scope="col">Explains</th>'
             f'<th scope="col">Cannot yet</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
             f'<ul class="key" aria-label="Key"><li>{node_glyph("demonstrated", 14)} Yield from own inputs</li><li>{node_glyph("demonstrated_purified", 14)} Purified inputs only</li>'
             f'<li>{node_glyph("missing", 14)} No published step</li><li>{node_glyph("unread", 14)} Full text not read</li></ul>')
    return fig(inner, "No scenario has published chemistry for every stage",
               "Real data for the four routes on our pathway map. <span class=src>Source: experiments/pathway_map/map.json; site/content.json</span>", "cov-fig")


# ---------------------------------------------------------------- approach
def fig_compat(res):
    """Planted pH 2 to pH 10 hand-off and its compliant twin. Source: experiments/compat/results.json
    (planted_pH2_to_pH10: flagged, F1) and planted_cases.csv (twin: mixing with pH 12 stream, no flags)."""
    flag = ", ".join(res["planted_pH2_to_pH10"]["got"]["1->2"])
    rows = [
        ("bad", "Planted fault", "Step 1 leaves pH 2", "Same pot", "Step 2 needs pH 10", f"Flagged: {flag} pH"),
        ("ok", "Twin", "Step 1 leaves pH 2", "Mix half and half with a pH 12 stream", "Step 2 needs pH 10", "Passes"),
    ]
    lis = "".join(f'<li class="cp {k}"><p class="cp-n">{e(n)}</p><div class="cp-row"><span class="cp-s">{e(a)}</span>'
                  f'<span class="cp-p">{link_glyph("broken" if k == "bad" else "continuous", True, 30)}<small>{e(p)}</small></span>'
                  f'<span class="cp-s">{e(b)}</span><span class="cp-v">{e(v)}</span></div></li>' for k, n, a, p, b, v in rows)
    return fig(f'<ol class="compat">{lis}</ol>', "The rule fails an acid product poured into an alkaline step, and passes the same step once a real process fixes the pH",
               "Real data. The planted control the rule had to pass before scoring any real route. "
               "<span class=src>Source: experiments/compat/results.json</span>", "compat-fig")


def fig_goal(n_routes, n_bench, n_pred):
    """R-open targets (README.md, docs/PLAN.md) against today. Counts: map.json routes; board tasks M3 / M5 done."""
    rows = [("Routes on the scored map", n_routes, 4, "at least 4"), ("Published claims benched against chance", n_bench, 10, "at least 10"),
            ("Sealed predictions confirmed by later data", n_pred, 3, "at least 3")]
    bars = "".join(f'<div class="bar goal"><span class="bl">{e(l)}</span><span class="track"><span class="fill" style="width:{min(v / n, 1) * 100:.0f}%"></span></span>'
                   f'<span class="bv">{v} of {n}</span></div>' for l, v, n, _ in rows)
    met = sum(1 for _, v, n, _ in rows if v >= n)
    words = {0: "No target", 1: "One target", 2: "Two targets", 3: "All three targets"}
    return fig(f'<div class="chart">{bars}</div>', f"{words[met]} of three met so far" if met < 3 else "All three targets met",
               "Real data from the live board. Bars run from zero to the target for the open goal, due by the end of 2027.", "goal-fig")


def fig_milestones(tasks, names, title):
    """Done / total per milestone. Source: board/board.db."""
    rows = []
    for mk, name in names:
        ts = [t for t in tasks if t["milestone"] == mk]
        if not ts:
            continue
        d = sum(1 for t in ts if t["status"] == "done")
        rows.append(f'<span class="mn">{e(mk)} · {e(name)}</span><span class="mtrack"><span class="mfill" style="width:{d / len(ts) * 100:.0f}%"></span></span>'
                    f'<span class="n">{d} of {len(ts)}</span>')
    return fig(f'<div class="ms">{"".join(rows)}</div>', title,
               "Real data. Tasks done per milestone. <span class=src>Source: board/board.db</span>", "ms-fig")
