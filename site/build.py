#!/usr/bin/env python3
"""Build the Open Origins site from site/*.json, the repo's result files and the live board.

Run from the repo root:  python3 -I site/build.py   (or .venv/bin/python -I site/build.py)
Standard library only, so the parent site (open-citizen-science/build.py) can run it with any Python.
Writes site/dist/: one HTML file per page, a news article per item, news.xml, assets/ and data/.
Static; works from file:// and from Cloudflare Pages. Ends with a link check that fails the build on any broken link.

Inputs (read-only):
  site/content.json, site/findings.json, site/news.json       page text
  experiments/pathway_map/map.json, handoffs.csv              pathway map (tasks #4, #5, #17, #18)
  experiments/qt45_numbers/results_calc.json                  QT45 growth factor (task #2)
  experiments/compat/results.json, planted_cases.csv          compatibility rule control (task #3)
  docs/PAPERS.csv                                             paper ledger (tasks #1, #14)
  docs/prereg/HASHES.txt                                      sealed plans
  board/board.db                                              task board (opened read-only)
  site/assets/news/*.webp                                     news pictures (made by site/illustrate_news.py)
"""
import csv, html, importlib.util, json, re, shutil, sqlite3, sys, time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def news_date(s):
    """2026-05-28 -> 28 May 2026; 2026-06 -> Jun 2026; anything else (2001-2020) as given."""
    p = s.split("-")
    if len(p) == 3 and all(x.isdigit() for x in p):
        return f"{int(p[2])}\u00a0{MONTHS[int(p[1]) - 1]} {p[0]}"
    if len(p) == 2 and len(p[1]) == 2 and p[1].isdigit():
        return f"{MONTHS[int(p[1]) - 1]} {p[0]}"
    return s


def news_head(s):
    """Drop a trailing author list in brackets: the card already shows the authors."""
    return re.sub(r"\s*\((?=[^()]*(,|et al))[^()]*\)\s*$", "", s)

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DIST = SITE / "dist"
EXP = ROOT / "experiments"
e = html.escape


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ART = load_module("oo_art", SITE / "art.py")
FIG = load_module("oo_figures", SITE / "figures.py")
CH = load_module("oo_chrome", SITE / "chrome.py")

C = json.loads((SITE / "content.json").read_text())
F = json.loads((SITE / "findings.json").read_text())
NEWS = sorted(json.loads((SITE / "news.json").read_text())["items"], key=lambda n: n["date"], reverse=True)
MAP = json.loads((EXP / "pathway_map" / "map.json").read_text())
CALC = json.loads((EXP / "qt45_numbers" / "results_calc.json").read_text())
COMPAT = json.loads((EXP / "compat" / "results.json").read_text())
CASES = list(csv.DictReader((EXP / "compat" / "planted_cases.csv").open()))
PAPERS = list(csv.DictReader((ROOT / "docs" / "PAPERS.csv").open()))
HASHES = [l.split() for l in (ROOT / "docs" / "prereg" / "HASHES.txt").read_text().splitlines() if l.strip()]
TOTALS = FIG.map_totals(MAP)


def board():
    db = ROOT / "board" / "board.db"
    if not db.exists():
        return [], []
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    tasks = [dict(r) for r in c.execute("SELECT id, milestone, title, body, deps, status, owner FROM tasks ORDER BY id")]
    landed = [dict(r) for r in c.execute("SELECT ts, task, verdict, path, summary FROM landed ORDER BY ts DESC")]
    c.close()
    return tasks, landed


TASKS, LANDED = board()
N_DONE = sum(1 for t in TASKS if t["status"] == "done")
N_CLAIMED = sum(1 for t in TASKS if t["status"] == "claimed")
N_OPEN = sum(1 for t in TASKS if t["status"] == "open")

PAGES = [("findings.html", "Findings"), ("map.html", "Pathway map"), ("theories.html", "Theories"), ("approach.html", "Approach"),
         ("tracker.html", "Tracker"), ("news.html", "News"), ("contribute.html", "Contribute"), ("data.html", "Data"), ("resources.html", "Resources")]


def md(s):
    """Tiny inline markup: **bold**, `code`."""
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", e(s))
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def mark_svg(cls="mark"):
    return f'<svg class="{cls}" viewBox="0 0 32 32" aria-hidden="true" focusable="false">{ART.MARK}</svg>'


REPO = "https://github.com/HarshInvader/open-origins"
NAV_GROUPS = (
    ("Research", (("findings.html", "Findings", "What is known, and what we found", "find"),
                  ("map.html", "Pathway map", "Four routes, scored step by step", "map"),
                  ("theories.html", "Theories", "The proposed origins we score", "theory"),
                  ("approach.html", "Approach", "How every idea gets tested", "approach"),
                  ("news.html", "News", "New papers, summarised", "news"),
                  ("tracker.html", "Tracker", "Progress and the live task board", "tracker"))),
    ("Resources", (("data.html", "Datasets", "Every open dataset, used or not", "data"),
                   ("resources.html#h-data", "Open data", "Result files and the paper ledger", "data"),
                   ("resources.html#h-logo", "Logo", "Free to download", "logo"),
                   ("resources.html#h-files", "Research files", "Notes, plans and results", "files"),
                   (REPO, "Code on GitHub", "Everything we run, in the open", "code"),
                   ("../index.html", "Open Citizen Science", "Our sister projects", "family"))),
)


def render(name, title, desc, current, main, body_class=""):
    tpl = (SITE / "templates" / "layout.html").read_text()
    nav = CH.nav_items(NAV_GROUPS, current)
    foot = "".join(f'<a href="{f}">{e(n)}</a>' for f, n in [("index.html", "Home")] + PAGES)
    note = (f"Figures marked Real data are drawn from the project's result files at build time; "
            f"pictures marked Illustration are drawn for this site. The code is on <a href=\"https://github.com/HarshInvader/open-origins\">GitHub</a>. Built {time.strftime('%d %b %Y').lstrip('0')}.")
    fills = {"TITLE": e(title), "DESC": e(desc), "ROOT": "", "BODY_CLASS": body_class, "MARK": mark_svg(), "NAME": e(C["name"]),
             "NAV": nav, "MAIN": main, "WORDMARK": CH.wordmark_svg(C["name"]), "REPO": REPO, "GOAL": e(C["goal"]), "FOOT_PAGES": foot, "FOOT_NOTE": note}
    out = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: fills[m.group(1)], tpl)
    assert "{{" not in out, f"unfilled placeholder in {name}"
    (DIST / name).write_text(out)


def block(num, rail, hid, title, inner, cls=""):
    return (f'<section class="block wrap {cls}" aria-labelledby="{hid}"><p class="rail"><span>{num}</span>{e(rail)}</p>'
            f'<div class="content"><h2 id="{hid}">{e(title)}</h2>{inner}</div></section>')


def page_head(kicker, h1, lede, jump=None, side=""):
    j = ""
    if jump:
        j = '<nav class="jump" aria-label="On this page">' + "".join(f'<a href="#{a}">{e(t)}</a>' for a, t in jump) + "</nav>"
    one = "" if side else " one"
    return (f'<section class="page-head wrap{one}"><div class="hero-text"><p class="kicker">{e(kicker)}</p><h1>{e(h1)}</h1>'
            f'<p class="lede">{md(lede)}</p>{j}</div>{side}</section>')


def chip(s):
    k = {"supported": "ok", "met": "ok", "largely met": "ok", "strained": "warn", "partial": "warn", "contested": "warn",
         "partly met": "warn", "failed": "bad", "refuted": "bad", "not met": "bad"}.get(s.lower(), "open")
    return f'<span class="chip chip-{k}">{e(s)}</span>'


def findings_by_n():
    return {f["n"]: f for f in F.get("findings", [])}


def mini_for(n):
    return {1: lambda: FIG.mini_planted(CASES), 2: lambda: FIG.mini_qt45(CALC), 3: lambda: FIG.mini_handoffs(MAP)}.get(n, lambda: "")()


# ---------------------------------------------------------------- data files copied into dist/data
DATA_FILES = [  # (published name, source, what it is)
    ("PAPERS.csv", ROOT / "docs" / "PAPERS.csv", "Paper ledger, every row resolved by DOI"),
    ("pathway_map.json", EXP / "pathway_map" / "map.json", "Pathway map: steps, hand-offs, verdicts and ranked gaps"),
    ("pathway_handoffs.csv", EXP / "pathway_map" / "handoffs.csv", "Every hand-off with its verdict and flags"),
    ("qt45_results_calc.json", EXP / "qt45_numbers" / "results_calc.json", "QT45 growth-factor calculation"),
    ("compat_planted_cases.csv", EXP / "compat" / "planted_cases.csv", "The 28 planted cases for the compatibility rule"),
    ("catalog.csv", ROOT / "datasets" / "catalog.csv", "Dataset catalogue: every relevant dataset, its terms, and whether we use it"),
]


def size_of(p):
    b = p.stat().st_size
    return f"{b / 1024:.0f} KB" if b >= 1024 else f"{b} B"


def data_list():
    return [(n, f"data/{n}", w, size_of(src)) for n, src, w in DATA_FILES]


# ---------------------------------------------------------------- home
SIGNS = [  # the frieze: signs of early Earth and early life, each in a 48-unit box
    '<path d="M18 44V22M30 44V22M18 22a9 9 0 1 1 12 0M18 29h12M18 36h12"/>',  # RNA hairpin
    '<path d="M24 8l15 11-6 18H15L9 19z"/><circle cx="24" cy="8" r="2.5"/>',  # ribose ring
    '<path d="M4 40h40M7 40c0-14 8-24 17-24s17 10 17 24M13 40c0-9 5-16 11-16s11 7 11 16M19 40c0-5 2-9 5-9s5 4 5 9"/>',  # stromatolite
    '<path d="M17 44l4-24h6l4 24M22 16c-3-4 3-6 0-11M27 16c3-4-3-6 0-11"/>',  # vent chimney
    '<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="13"/><circle cx="20" cy="21" r="2.5"/><circle cx="28" cy="28" r="2"/>',  # protocell
    '<path d="M9 33l10-9 10 9 10-9"/><circle cx="9" cy="33" r="3"/><circle cx="19" cy="24" r="3"/><circle cx="29" cy="33" r="3"/><circle cx="39" cy="24" r="3"/>',  # a small molecule
    '<path d="M28 4L14 26h10l-4 18 14-24H24z"/>',  # the spark
    '<path d="M24 6c8 10 12 17 12 24a12 12 0 0 1-24 0c0-7 4-14 12-24z"/>',  # water
]


def page_index():
    art = ART.hero().replace('<figure class="hero-art">', '<figure class="hero-art plate">', 1)
    art = re.sub(r"<figcaption>.*?</figcaption>",
                 '<figcaption><span class="cat">Pl. 1 · A stromatolite, cut in half</span>Illustration. Each layer was laid down by a mat of microbes. '
                 'Rocks like this, 3.4 billion years old, are among the oldest signs of life.</figcaption>', art, flags=re.S)
    hero = (f'<section class="hero home-hero wrap" aria-labelledby="claim"><div class="hero-text">'
            f'<p class="kicker">{e(C["name"])}, an open research group</p>'
            '<h1 id="claim">Map and test every route to the origin of life by 2027</h1>'
            '<p class="state">An open-source effort, run in public. All our code and data are free.</p>'
            '<div class="actions"><a class="btn primary" href="contribute.html">Donate your tokens</a><a class="btn" href="findings.html">Read the findings</a></div>'
            f'</div>{art}</section>')
    band = CH.frieze(SIGNS, "A band of the signs of this project: an RNA hairpin, a ribose ring, a stromatolite, a vent chimney, a protocell, a molecule, a spark and a drop of water")
    s1 = block("01", "The question", "h-question", "Chemistry can make each step toward life, but nobody has joined them up", f"""
<div class="split"><div class="say">
<p>Life began on Earth about four billion years ago, from chemistry alone. Nobody knows how.</p>
<p>Labs have made amino acids, RNA letters and an RNA that copies itself. Each step worked on its own, mostly with chemicals bought pure.</p>
<p>Nobody has run the steps one after another, in one setting, using only what the step before left behind. That gap is the question.</p>
<p class="more-link"><a href="findings.html">What is known and what has been tried</a></p></div>
{FIG.fig_steps_vs_joins(MAP)}</div>""", "broad")
    s2 = block("02", "Where we are", "h-where", "We know where the building blocks come from, not how copying began",
               f'{FIG.fig_ladder(C["ladder"])}<p class="more-link"><a href="tracker.html">Track the progress</a></p>', "broad")
    s3 = block("03", "Found so far", "h-found", "What we have found so far", """
<ul class="found">
<li><b>No proposed route joins up.</b> We scored four published routes hand-off by hand-off. None of the 22 hand-offs passes cleanly.</li>
<li><b>The best self-copying RNA cannot keep up.</b> On its published numbers, QT45 copies itself more slowly than it breaks down. A population would shrink each round.</li>
<li><b>Simple shortcuts cannot rebuild the first cell's genes.</b> On simulated family trees with a planted answer, no rule based only on which genes are present found the true set.</li>
</ul><p class="more-link"><a href="findings.html">All findings, with their evidence</a></p>""", "broad")
    s4 = block("04", "How we work", "h-how", "How we test a route",
               '<div class="say"><p>We write each test and its pass mark down and fingerprint it before we look. Every method must first find an answer we planted, and someone else must try to break every positive result.</p></div>'
               f'{FIG.fig_pipeline(len(HASHES), COMPAT["n_cases"])}<p class="more-link"><a href="approach.html">Our approach and what counts as done</a></p>', "broad")
    ledger, files = FIG.fig_ledger(PAPERS, data_list())
    s5 = block("05", "Open data", "h-data", "All origin-of-life data, free in one place", f"""
<div class="split"><div class="say"><p>Every paper we cite resolves to a real DOI, checked against its text where we could read it.</p>
<p>We list 92 datasets, where each lives and under which terms. Our own tables are free, and one script fetches the rest.</p>
<div class="actions"><a class="btn" href="data.html">Get the data</a></div></div>{ledger}</div>""", "broad")
    s6 = block("06", "Help", "h-help", "The fastest help is an AI agent working an open task",
               '<div class="say"><p>Donate your tokens: point a Claude Fable or Opus class agent at an open task. Wet labs can run a test we seal in advance.</p></div>'
               '<div class="actions"><a class="btn primary" href="contribute.html">Find a way to help</a></div>', "broad")
    return hero + band + s1 + s2 + s3 + s4 + s5 + s6


# ---------------------------------------------------------------- findings
STRENGTH = [("strong", "Solid", 3), ("moderate", "Likely", 2), ("weak", "Shaky", 1), ("exploratory", "Not yet tested", 0), ("descriptive", "A measurement", -1)]
LEVEL_TEXT = {"strong": "Replicated on held-out data and survived an independent red team.",
              "moderate": "Passed a sealed test on held-out data; red team pending or partial.",
              "weak": "Passed, but with small numbers or a caveat that could undo it.",
              "exploratory": "A pattern we saw; it has not yet faced a sealed test.",
              "descriptive": "A measurement or count, not a test of a hypothesis."}
NOVELTY = {"new": ("New", "We know of no earlier report of this."), "partly": ("Partly new", "Builds on earlier work; the new part is stated."),
           "known": ("Known", "Already reported by others; we re-tested it with stricter rules."), "tests": ("Tests a claim", "A published claim that we put to a test.")}
TAGS = {"out": "Ruled out", "wait": "Can't test yet", "weak": "Weakened", "ns": "Not supported", "open": "Still open", "part": "Works in part"}
TAG_CLS = {"out": "out", "wait": "wait", "weak": "weak", "ns": "bad", "open": "open", "part": "part"}


def meter(level):
    _, word, n = next(x for x in STRENGTH if x[0] == level)
    pips = "" if n < 0 else "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
    return f'<span class="meter {level}"><span class="pips" aria-hidden="true">{pips}</span>{e(word)}</span>'


def nov(k):
    return f'<span class="nov nov-{k}">{e(NOVELTY.get(k, (k,))[0])}</span>'


def tag(k):
    return f'<span class="tag {TAG_CLS.get(k, "open")}">{e(TAGS.get(k, k))}</span>'


def page_findings():
    d = F
    known_figs = {0: FIG.fig_deep_time(), 2: FIG.fig_bennu()}
    rows = []
    for i, p in enumerate(d.get("known", [])):
        txt = f'<div class="art-text"><h3>{e(p["h"])}</h3>' + "".join(f"<p>{md(x)}</p>" for x in p["paras"]) + "</div>"
        f = known_figs.get(i, "")
        rows.append(f'<div class="art-row{"" if f else " solo"}">{txt}{f}</div>')
    disputed = "".join(f'<div class="art-row solo"><div class="art-text"><h3>{e(p["h"])}</h3>' + "".join(f"<p>{md(x)}</p>" for x in p["paras"]) + "</div></div>"
                       for p in d.get("disputed", []))
    tried = "".join(f'<li><div class="tr-head"><h4>{e(t["approach"])}</h4>{tag(t["status"])}</div>'
                    f'<p class="tr-meta">{e(t.get("who", ""))}{" · " if t.get("who") and t.get("when") else ""}{e(t.get("when", ""))}</p>'
                    f'<p>{md(t["idea"])}</p><p><strong>What happened:</strong> {md(t["outcome"])}</p></li>' for t in d.get("tried", []))
    key = ('<dl class="levels">' + "".join(f"<div><dt>{meter(k)}</dt><dd>{e(LEVEL_TEXT[k])}</dd></div>" for k, _, _ in STRENGTH) + "</dl>"
           '<h3 class="key-h">Is it new?</h3><dl class="levels">' + "".join(f"<div><dt>{nov(k)}</dt><dd>{e(v[1])}</dd></div>" for k, v in NOVELTY.items()) + "</dl>")
    fl = []
    fs = d.get("findings", [])
    for level, _, _ in STRENGTH:
        grp = [f for f in fs if f["level"] == level]
        if not grp:
            continue
        fl.append(f'<h3 class="fgroup">{meter(level)}<span class="fgn">{len(grp)}</span></h3><ol class="findings">')
        for f in grp:
            cav = f'<p class="caveat">{md(f["caveat"])}</p>' if f.get("caveat") else ""
            where = ", ".join(f"<code>{e(x)}</code>" for x in f.get("folders", []))
            fl.append(f'<li class="fcard" id="f{f["n"]}">{mini_for(f["n"])}<div class="fh"><div class="fmeta">{nov(f["novelty"])}</div>'
                      f'<h4 class="ft">{e(f["head"])}</h4><p class="fg">{md(f["gist"])}</p><details class="tech"><summary>Technical version</summary>'
                      f'<div class="fbody"><p class="ftech">{e(f["title"])}</p><p>{md(f["plain"])}</p><p class="prior"><b>Earlier work.</b> {md(f["prior"])}</p>'
                      f'<p class="nums">{md(f["nums"])}</p>{cav}<p class="where">Code and results: {where}</p></div></details></div></li>')
        fl.append("</ol>")
    n = len(fs)
    cl = d.get("closed", [])
    routes = "".join(f'<li><div class="tr-head"><h4>{e(r["route"])}</h4>{tag(r["tag"])}</div><p>{md(r["why"])}</p></li>' for r in cl)
    legend = '<ul class="legend-row">' + "".join(f"<li>{tag(k)} {e(v)}</li>" for k, v in (
        ("out", "the test ran and failed, with enough power to see a real effect"), ("wait", "the data cannot decide yet"),
        ("weak", "an earlier result shrank or failed its pass mark"))) + "</ul>"
    rv = d.get("reversed", [])
    pubs = "".join(f'<li><div class="tr-head"><h4>{e(o["title"])}</h4><span class="tag {"done" if o.get("status") == "Done" else ("run" if o.get("status") == "In progress" else "open")}">{e(o.get("status", ""))}</span></div><p>{md(o["what"])}</p></li>'
                   for o in d.get("outputs", []))
    n_known, n_disp = len(d.get("known", [])), len(d.get("disputed", []))
    words = {5: "Five", 6: "Six", 4: "Four", 3: "Three"}
    out = [page_head("Findings", "Life started early and its building blocks form easily. How they joined up is still open.", d["lede"],
                     [("h-known", "What is known"), ("h-open", "Still disputed"), ("h-tried", "What has been tried"), ("h-ours", "Our findings"),
                      ("h-closed", "Closed routes"), ("h-rev", "Reversed"), ("h-pub", "Outputs")])]
    out.append(block("01", "Known", "h-known", f"{words.get(n_known, n_known)} things scientists agree on", "".join(rows)))
    out.append(block("02", "Disputed", "h-open", f"{words.get(n_disp, n_disp)} questions still argued over", disputed))
    out.append(block("03", "Tried", "h-tried", "What has been tried, and how it went",
                     f'<p class="intro">{md(d.get("tried_intro", ""))}</p>{FIG.fig_tried(d.get("tried", []))}<ol class="tried-list">{tried}</ol>'))
    out.append(block("04", "Labels", "h-levels", "How to read the labels", key))
    out.append(block("05", "Ours", "h-ours", f"What our tests add: {n} finding{'s' if n != 1 else ''}",
                     f'<p class="intro">{md(d.get("ours_intro", ""))}</p>' + "".join(fl)))
    out.append(block("06", "Closed", "h-closed", f"{len(cl)} routes tested and closed" if cl else "No route tested and closed yet",
                     f'<p class="intro">{md(d.get("closed_intro", ""))}</p>' + legend + (f'<ol class="tried-list">{routes}</ol>' if cl else "")))
    revs = "".join(f'<li><h4>{e(r["head"])}</h4><p>{md(r["what"])}</p><p><strong>Why it broke:</strong> {md(r["why"])}</p></li>' for r in rv)
    out.append(block("07", "Reversed", "h-rev", f"{len(rv)} of our own results the red team broke" if rv else "No result of ours has been reversed yet",
                     f'<ol class="tried-list">{revs}</ol>' if rv else "<p>Every positive result goes to a red team before it is listed above.</p>"))
    out.append(block("08", "Outputs", "h-pub", "What can be published along the way",
                     '<p class="intro">None of this needs the whole problem solved. Clean negatives and tools are worth publishing on their own.</p>'
                     f'<ol class="tried-list">{pubs}</ol>'))
    return "".join(out)


# ---------------------------------------------------------------- pathway map
def page_map():
    t = TOTALS
    stats = (f'<div class="stats"><div class="stat"><b>4</b><span>routes scored</span></div><div class="stat"><b>{t["steps"]}</b><span>steps</span></div>'
             f'<div class="stat"><b>{t["cont"]} of {t["hand"]}</b><span>hand-offs pass cleanly</span></div><div class="stat"><b>{t["gaps"]}</b><span>gaps, ranked</span></div></div>')
    head = page_head("Pathway map", "No proposed route runs from raw materials to self-copying RNA",
                     "We wrote four proposed routes as step tables, straight from the papers, and scored every hand-off with a rule we sealed before we started. "
                     "A step counts as joined only if it can run on what the step before left behind, using a named physical process.",
                     [("h-map", "The map"), ("h-breaks", "First breaks"), ("h-gaps", "Top gaps"), ("h-rule", "The rule"), ("h-lit", "Literature view"), ("h-files", "Files")])
    s1 = block("01", "The map", "h-map", "Each route, step by step", f'{stats}{FIG.map_key()}{FIG.fig_map_full(MAP)}')
    # Wording from experiments/pathway_map/RESULTS.md ("Where each route first breaks").
    breaks = [
        ("Cyanosulfidic", "after step 1", "The sugars come out trapped as oxazolidinones (Ritson 2012), and the next step needs free glycolaldehyde. It still gets furthest, to short RNA chains, but 8 of its 9 hand-offs are unexplained."),
        ("Alkaline vent", "after step 1", "Formate and acetate form across iron-sulfide walls (Altair 2025). No vent step to sugars or nucleotides has been published."),
        ("Warm pond", "before step 1", "The pond has no nucleotide source. Both pond papers start from laboratory nucleotides."),
        ("Ice and RNA", "before step 1", "Nothing makes the triplet building blocks, and every RNA input, the ribozyme included, is supplied purified."),
    ]
    bl = "".join(f'<li><div class="tr-head"><h4>{e(n)}</h4><span class="tag warn">Breaks {e(w)}</span></div><p>{e(x)}</p></li>' for n, w, x in breaks)
    s2 = block("02", "First breaks", "h-breaks", "Two routes break before their first step, two right after it",
               f'<ol class="tried-list">{bl}</ol><p class="note">The alkaline vent ranks first by the rule, with no hard fail. That is an artefact: 5 of its 6 steps have no published chemistry, so there is nothing to break.</p>')
    full_stage = sum(1 for st in MAP["stages"] if max((g["routes_blocked_at_stage"] for g in MAP["gaps"] if g["stage"] == st), default=0) == 4)
    gaps = FIG.fig_gaps(MAP).replace("Sustained replication is the gap no route has touched", f"{full_stage} of 5 stages block all four routes")
    s3 = block("03", "Top gaps", "h-gaps", "Sustained replication is missing from every route",
               f'<p class="intro">No route has any published step in which a replicator makes more copies of itself than it loses. The only template copying with a yield uses a purified, selected ribozyme with purified triplets, primers and a hexamer.</p>{gaps}')
    names = MAP["check_names"]
    hard = "".join(f'<li><b>{e(k)}</b> <span>{e(v)}</span></li>' for k, v in names.items() if k.startswith("F"))
    warn = "".join(f'<li><b>{e(k)}</b> <span>{e(v)}</span></li>' for k, v in names.items() if k.startswith("W"))
    s4 = block("04", "The rule", "h-rule", "Nine hard fails decide whether a hand-off breaks", f'''
<div class="two-col"><div class="say"><p>Step k+1 may use what step k leaves only through named physical processes from a closed list of 14, such as drying, heating, mixing or thermophoresis.
The rule was hashed before any route was encoded, and it caught all 28 planted test cases first.</p>
<p class="more-link"><a href="approach.html#h-rule">The rule and its planted control</a></p></div>
<div><h3 class="key-h">Hard fails</h3><ul class="checks codes">{hard}</ul><h3 class="key-h">Warnings</h3><ul class="checks codes">{warn}</ul></div></div>
<details class="tech"><summary>Every hand-off, with the reason</summary>{FIG.handoff_table(MAP)}</details>''')
    m = C["map"]
    steps = "".join(f'<tr><th scope="row">{e(s[0])}</th><td>{md(s[1])}</td><td>{chip(s[2])}</td></tr>' for s in m["steps"])
    scen = "".join(f'<div class="card"><h3>{e(s["name"])}</h3><p><strong>Explains</strong> {md(s["explains"])}</p><p><strong>Cannot yet</strong> {md(s["gap"])}</p></div>' for s in m["scenarios"])
    s5 = block("05", "Literature view", "h-lit", "The literature runs further, to compartments and evolution, but with gaps at every stage", f'''
<p class="intro">{md(m["note"])}</p><div class="tablewrap"><table class="score"><thead><tr><th scope="col">Step</th><th scope="col">Best evidence</th><th scope="col">Status</th></tr></thead><tbody>{steps}</tbody></table></div>
<h3 class="key-h">Scenarios</h3><div class="cards">{scen}</div>''')
    files = "".join(f'<li><a href="data/{n}" download>{e(n)}</a><span>{e(w)} · {size_of(src)}</span></li>' for n, src, w in DATA_FILES if "pathway" in n)
    s6 = block("06", "Files", "h-files", "The map is a data file anyone can rescore", f'''
<ul class="dl">{files}</ul>
<p class="note">Not checked: Powner 2009 and Šimonis 2026 were read as abstracts only (steps C5, C7 and P1 count as unread), and no supplementary files were read. An audit of the encoding by another agent is open (task #21).
Results: <code>experiments/pathway_map/RESULTS.md</code>.</p>''')
    return head + s1 + s2 + s3 + s4 + s5 + s6


# ---------------------------------------------------------------- theories
SCEN_KEY = {"Alkaline hydrothermal vents": "alkaline_vent", "Surface ponds with wet-dry cycles": "warm_pond",
            "Cyanosulfidic surface chemistry": "cyanosulfidic", "Ice (eutectic freezing)": "ice_rna"}


def page_theories():
    scen = {SCEN_KEY[s["name"]]: s for s in C["map"]["scenarios"] if s["name"] in SCEN_KEY}
    rows = "".join(f'<tr><th scope="row">{e(t["name"])}<span class="sub">{e(t.get("who", ""))}</span></th><td>{md(t["prediction"])}</td>'
                   f'<td>{md(t["evidence"])}</td><td>{chip(t["status"])}</td></tr>' for t in C["theories"])
    bench = "".join(f"<li><strong>{e(b[0])}.</strong> {md(b[1][0].upper() + b[1][1:])}</li>" for b in C["bench"])
    head = page_head("Theories", "No theory of how life began is supported end to end", C["theories_lede"],
                     [("h-where", "Where"), ("h-cover", "What each explains"), ("h-score", "Scoreboard"), ("h-bench", "What we will re-test")])
    s1 = block("01", "Where", "h-where", "The scenarios disagree first about where the chemistry happened",
               '<p class="intro">Each scenario names a place on the early Earth, and the place decides which chemicals, temperatures and energy sources a route may use.</p>' + FIG.fig_settings())
    s2 = block("02", "Coverage", "h-cover", "Each scenario explains some stages and has no chemistry for others", FIG.fig_coverage(MAP, scen))
    s3 = block("03", "Scoreboard", "h-score", "Each theory's riskiest prediction, and how it is doing", f'''
<div class="tablewrap"><table class="score"><thead><tr><th scope="col">Theory</th><th scope="col">Riskiest prediction</th><th scope="col">Evidence so far</th><th scope="col">Status</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Status comes from the published literature as of {e(C["as_of"])}, plus our pathway map where it applies. Each row changes as our own benched results land.</p>''')
    s4 = block("04", "Bench", "h-bench", f"{len(C['bench'])} published claims we will re-test against chance", f'<ul class="mk">{bench}</ul>')
    return head + s1 + s2 + s3 + s4


# ---------------------------------------------------------------- approach
def page_approach():
    rules = "".join(f"<li><b>{e(r[0])}</b> <span>{md(r[1])}</span></li>" for r in C["rules"])
    traps = "".join(f"<li><strong>{e(t[0])}</strong> {md(t[1])}</li>" for t in C["traps"])
    crit = "".join(f"<li>{md(x)}</li>" for x in C["criteria"])
    nots = "".join(f"<li>{md(x)}</li>" for x in C["not_claimed"])
    raise_ = "".join(f"<li>{md(x)}</li>" for x in C["raise_odds"])
    odds = "".join(f'<div class="stat"><b>{e(v)}</b><span>{e(k)}</span></div>' for k, v in C["odds"])
    n_bench = sum(1 for t in TASKS if t["milestone"] == "M3" and t["status"] == "done")
    hashes = "".join(f'<li><b>{e(Path(h[1]).stem.replace("_", " "))}</b><span><code>{e(h[1])}</code></span><span><code>sha256 {e(h[0][:16])}...</code></span></li>' for h in HASHES)
    head = page_head("Approach", "Our rules exist to stop us fooling ourselves", C["approach_lede"],
                     [("h-path", "The path"), ("h-rules", "Rules"), ("h-rule", "Compatibility rule"), ("h-done", "What counts as done"),
                      ("h-traps", "Traps"), ("h-not", "Not claimed"), ("h-sealed", "Sealed plans")])
    s1 = block("01", "The path", "h-path", "Every test is sealed before anyone sees the data", FIG.fig_pipeline(len(HASHES), COMPAT["n_cases"]))
    s2 = block("02", "Rules", "h-rules", "Five rules we hold every test to", f'<ol class="rules">{rules}</ol>')
    hard = MAP["check_names"]
    s3 = block("03", "Compatibility", "h-rule", "A sealed rule decides when one step can feed the next", f'''
<div class="say"><p>"Prebiotically plausible" is a judgement, so we fixed the judgement in advance. Step k+1 may use what step k leaves only through named physical processes from a closed list of 14, such as drying, heating, mixing or thermophoresis.</p>
<p>The rule then checks {sum(1 for k in hard if k.startswith("F"))} hard fails and {sum(1 for k in hard if k.startswith("W"))} warnings. Its tolerances, such as pH within 1 unit and temperature within 10 °C, are our own generous conventions, not literature values.</p></div>
{FIG.fig_compat(COMPAT)}
<p class="note">Result: {COMPAT["n_correct"]} of {COMPAT["n_cases"]} planted cases correct. Rule sha256 <code>{e(COMPAT["rule_sha256"][:16])}...</code>, file <code>{e(COMPAT["rule_file"])}</code>.</p>''')
    s4 = block("04", "Done", "h-done", "What \"cracked\" means, and how far we are", f'''
<p class="intro">{md(C["criteria_intro"])}</p><ol class="crit">{crit}</ol>
{FIG.fig_goal(len(MAP["routes"]), n_bench, 0)}
<h3 class="key-h">Our honest odds</h3><div class="stats">{odds}</div>
<p>What would raise them most:</p><ul class="mk">{raise_}</ul>''')
    s5 = block("05", "Traps", "h-traps", "Five traps we watch for", f'<ul class="mk">{traps}</ul>')
    s6 = block("06", "Not claimed", "h-not", "What we do not claim", f'<ul class="mk">{nots}</ul>')
    s7 = block("07", "Sealed", "h-sealed", f"{len(HASHES)} plans sealed so far", f'<p class="intro">Each line of <code>docs/prereg/HASHES.txt</code> holds the SHA-256 of a plan, written before its data were looked at.</p><ul class="hashes">{hashes}</ul>')
    return head + s1 + s2 + s3 + s4 + s5 + s6 + s7


# ---------------------------------------------------------------- tracker
def status_word(s):
    return {"done": ("done", "Done"), "claimed": ("run", "In progress"), "open": ("open", "Open")}.get(s, ("open", s))


def page_tracker():
    head = page_head("Tracker", f"{N_DONE} of {len(TASKS)} tasks are done", "Built from the live task board when this site was built. Agents claim tasks, land results and log them here, whichever way they go.",
                     [("h-ladder", "Where the field stands"), ("h-ms", "Milestones"), ("h-landed", "Landed"), ("h-all", "All tasks")])
    stats = (f'<div class="stats"><div class="stat"><b>{N_DONE}</b><span>done</span></div><div class="stat"><b>{N_CLAIMED}</b><span>in progress</span></div>'
             f'<div class="stat"><b>{N_OPEN}</b><span>open</span></div><div class="stat"><b>{len(LANDED)}</b><span>results landed</span></div></div>')
    ladder_rows = "".join(f'<li><span class="lv">{e(l)}</span><div><b>{e(n)}</b><p>{md(d)}</p></div>{chip(s)}</li>' for l, n, d, s in C["ladder"])
    s1 = block("01", "The field", "h-ladder", "Building blocks are largely met; self-replication is not",
               f'{stats}<p class="intro">{md(C["ladder_intro"])}</p>{FIG.fig_ladder(C["ladder"])}<ol class="ladder-list">{ladder_rows}</ol>')
    done = lambda mk: [t for t in TASKS if t["milestone"] == mk]
    m2_done = all(t["status"] == "done" for t in done("M2")) and done("M2")
    started = lambda mk: sum(1 for t in done(mk) if t["status"] == "done")
    if m2_done and started("M3") == 0 and started("M5") == 0:
        title = "The pathway map is done; no bench or prediction task has finished yet"
    else:
        title = "Tasks done per milestone"
    s2 = block("02", "Milestones", "h-ms", "Progress by milestone", FIG.fig_milestones(TASKS, C["milestones"], title))
    tname = {t["id"]: t["title"] for t in TASKS}
    lands = "".join(f'<li><span class="id">#{l["task"]}</span><div><p class="lt"><b>{e(tname.get(l["task"], ""))}</b><span class="tag">{e(l["verdict"])}</span>'
                    f'<span>{time.strftime("%d %b %Y", time.gmtime(l["ts"])).lstrip("0")}</span></p><p>{e(l["summary"])}</p><p class="where"><code>{e(l["path"])}</code></p></div></li>' for l in LANDED)
    s3 = block("03", "Landed", "h-landed", f"{len(LANDED)} results landed, newest first", f'<ol class="landed">{lands}</ol>')
    ms = dict(C["milestones"])
    groups = []
    for mk, name in C["milestones"]:
        ts = done(mk)
        if not ts:
            continue
        items = "".join(f'<li class="task"><details><summary><span class="id">#{t["id"]}</span><span>{e(t["title"])}</span><span class="tag {status_word(t["status"])[0]}">{status_word(t["status"])[1]}</span></summary>'
                        f'<div class="more-t"><p>{e(t["body"] or "")}</p>{"<p>Needs task #" + e(t["deps"]) + " first.</p>" if t["deps"] else ""}</div></details></li>' for t in ts)
        groups.append(f'<h3 class="key-h">{e(mk)} · {e(name)}</h3><ul class="tasks">{items}</ul>')
    s4 = block("04", "All tasks", "h-all", "Every task on the board", "".join(groups))
    return head + s1 + s2 + s3 + s4


# ---------------------------------------------------------------- news
STATUS_WORD = {"planned": "Planned test", "context": "Background", "running": "Running", "done": "Tested"}


def thumb(n, cls="nthumb", eager=False):
    p = SITE / "assets" / "news" / f"{n['id']}.webp"
    if not p.exists():
        return ""
    return (f'<img class="{cls}" src="assets/news/{e(n["id"])}.webp" width="900" height="600" alt="Illustration for: {e(n["head"])}"'
            f'{"" if eager else " loading=lazy"} decoding="async">')


def news_card(n):
    st = n.get("status", "")
    return (f'<article class="ncard" id="{e(n["id"])}"><p class="nmeta"><span class="nkind">{e(n.get("kind", "Paper"))}</span><time datetime="{e(n["date"])}">{news_date(n["date"])}</time></p>'
            f'<div class="nrow">{thumb(n)}<div class="nbody"><h3 class="nh"><a href="news-{e(n["id"])}.html">{e(news_head(n["head"]))}</a></h3>'
            f'<p class="nsrc">{e(n.get("who", ""))} · <a href="{e(n["url"])}">{e(n["venue"])}</a></p>'
            f'<p class="z z-gist">{md(n["gist"])}</p><p class="z z-plain">{md(n.get("plain") or n["gist"])}</p><p class="z z-tech">{md(n.get("tech") or n["gist"])}</p>'
            f'<div class="nborrow"><span class="tag {"part" if st == "planned" else "open"}">{e(STATUS_WORD.get(st, st))}</span><p><b>What we take from it.</b> {md(n["borrow"])}</p></div></div></div></article>')


def page_news():
    latest = "".join(news_card(n) for n in NEWS if n.get("section") != "landmark")
    land = "".join(news_card(n) for n in NEWS if n.get("section") == "landmark")
    n_plan = sum(1 for n in NEWS if n.get("status") == "planned")
    head = page_head("News", "New research on how life began, and what we take from each paper",
                     f"The latest papers and the landmark ones, each in a sentence, in plain words or in full detail. {n_plan} of the {len(NEWS)} feed a test we have planned. "
                     "Every source was checked against its DOI.", [("latest", "Latest"), ("landmarks", "Landmarks")])
    head = head.replace("</nav></div>", '</nav><p class="illustration-note">Pictures are illustrations drawn for this site, not figures from the papers.</p><div class="actions"><a class="btn" href="news.xml">Follow the feed (RSS)</a></div></div>', 1)
    zoom = ('<div class="zoombar" role="group" aria-label="How much detail"><div class="zoom-controls"><span>Detail</span>'
            '<button type="button" data-zoom="gist" aria-pressed="false">In a sentence</button><button type="button" data-zoom="plain" aria-pressed="true">Plain words</button>'
            '<button type="button" data-zoom="tech" aria-pressed="false">Technical</button></div></div>')
    s1 = f'<section class="block wrap news-feed" data-zoom="plain" aria-labelledby="latest"><p class="rail"><span>01</span>Latest</p><div class="content"><h2 id="latest">Latest papers, newest first</h2>{latest}</div></section>'
    s2 = (f'<section class="block wrap news-feed" data-zoom="plain" aria-labelledby="landmarks"><p class="rail"><span>02</span>Landmarks</p><div class="content">'
          f'<h2 id="landmarks">The papers that set the terms of the question</h2>{land}</div></section>')
    return head + f'<div class="news-feeds">{zoom}{s1}{s2}</div>'


def news_article(n, prev, nxt):
    st = n.get("status", "")
    pic = thumb(n, "nart", True)
    vis = f'<figure class="article-visual">{pic}<figcaption>Illustration drawn for this site, not a figure from the paper.</figcaption></figure>' if pic else ""
    nb = ""
    for lab, x in (("Newer", prev), ("Older", nxt)):
        if x:
            nb += f'<a href="news-{e(x["id"])}.html"><small>{lab}</small>{e(x["head"])}</a>'
    return f'''<article class="news-article wrap">
<header><a class="nback" href="news.html">Back to News</a><p class="kicker">{e(n.get("kind", "Paper"))} · {news_date(n["date"])}</p><h1>{e(news_head(n["head"]))}</h1>
<p class="article-source">{e(n.get("who", ""))} · <a href="{e(n["url"])}">{e(n["venue"])}</a></p></header>{vis}
<section aria-labelledby="sentence"><h2 id="sentence">In a sentence</h2><p>{md(n["gist"])}</p></section>
<section aria-labelledby="plain"><h2 id="plain">In plain words</h2><p>{md(n.get("plain") or n["gist"])}</p></section>
<section aria-labelledby="technical"><h2 id="technical">Technical detail</h2><p>{md(n.get("tech") or "")}</p></section>
<section aria-labelledby="borrow"><h2 id="borrow">What we take from it</h2><p><span class="tag {"part" if st == "planned" else "open"}">{e(STATUS_WORD.get(st, st))}</span></p><p>{md(n["borrow"])}</p>
<p class="note">Source checked against its DOI. <a href="{e(n["url"])}">Read the original</a>.</p></section>
<a class="nback" href="news.html">Back to News</a><nav class="article-neighbors" aria-label="Other news summaries">{nb}</nav></article>'''


def news_rss():
    base = C.get("base_url", "")
    rows = "".join(f"<item><title>{e(n['head'])}</title><link>{base}news-{e(n['id'])}.html</link><guid isPermaLink=\"false\">open-origins-{e(n['id'])}</guid>"
                   f"<pubDate>{e(n['date'])}</pubDate><description>{e(n['gist'])}</description></item>" for n in NEWS)
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{e(C["name"])} news</title><link>{base}news.html</link>'
            f'<description>{e(C["goal"])}</description>{rows}</channel></rss>')


# ---------------------------------------------------------------- contribute
def agent_prompt(t):
    return (f"You are contributing to Open Origins, https://github.com/HarshInvader/open-origins. Clone it.\n"
            f"Read docs/AGENT_BRIEF.md and follow its rules of evidence. Then do task #{t['id']} ({t['title']}) from board/TASKS.md.\n"
            f"Seal your plan and pass mark in docs/prereg/ (sha256 into HASHES.txt) before you look at any outcome, check a planted answer first, "
            f"work only in experiments/<your_folder>/, write RESULTS.md with the verdict first whichever way it goes, and open a pull request.")


def page_contribute():
    open_t = [t for t in TASKS if t["status"] == "open"]
    ready = [t for t in open_t if not t["deps"] or all(next((x["status"] for x in TASKS if str(x["id"]) == d.strip()), "") == "done" for d in t["deps"].split(","))]
    def starter(t, is_ready):
        dep = "" if is_ready else f'<p><b>Waits for</b> task #{e(t["deps"])}.</p>'
        return (f'<li class="starter"><details><summary><span class="sid">#{t["id"]}</span><span class="st">{e(t["title"])}</span>'
                f'<span class="tag {"part" if is_ready else "wait"}">{"Ready" if is_ready else "Waiting"}</span></summary><div class="sb"><p>{e(t["body"] or "")}</p>{dep}'
                f'<p><b>Milestone</b> {e(t["milestone"])} · {e(dict(C["milestones"]).get(t["milestone"], ""))}</p>'
                f'<p>Give your agent this:</p><pre class="code"><code>{e(agent_prompt(t))}</code></pre></div></details></li>')
    starters = "".join(starter(t, t in ready) for t in open_t)
    claimed = "".join(f'<li><b>#{t["id"]} {e(t["title"])}</b><span>Claimed by {e(t["owner"] or "an agent")}. Do not duplicate it.</span></li>' for t in TASKS if t["status"] == "claimed")
    head = page_head("Contribute", "Donate your tokens: point your AI agent at an open task",
                     f"Run an agent on your own subscription, give it one task and our rules, and send back the result as a pull request. {len(open_t)} tasks are open, {len(ready)} of them ready now. The steps are in <a href=\"https://github.com/HarshInvader/open-origins/blob/main/CONTRIBUTING.md\">CONTRIBUTING.md</a>. Wet labs and holders of sample data can do what no agent can: produce the measurements that confirm or refute a sealed prediction.",
                     [("h-tasks", "Donate your tokens"), ("h-labs", "Wet labs"), ("h-data", "Data holders"), ("h-other", "Other ways")])
    s1 = block("01", "Agents", "h-tasks", f"{len(ready)} tasks an agent can start today", f'''
<p class="intro">Open an issue named <code>Taking #id</code> so nobody duplicates it, then give your agent the prompt under the task. It seals its plan, tests against a planted answer and a null, and lands the result, positive or negative, as a pull request.</p>
<ol class="starters">{starters}</ol><h3 class="key-h">Already in progress</h3><ul class="asks">{claimed}</ul>''')
    labs = [("Run a sealed test.", "Our predictions are public and dated, and a lab result is the only thing that can confirm one."),
            ("Open a paywalled step.", "Three map steps count as unread because we could not open Powner et al. 2009 or the full text of Šimonis et al. 2026."),
            ("Fix a step on the map.", "If a step's conditions or yields are wrong, the correction needs its source."),
            ("Measure what we predict.", "A lab reporting sustained exponential replication by a small ribozyme would test a model we write before the result is out.")]
    s2 = block("02", "Wet labs", "h-labs", "Only a lab can confirm a prediction", '<ul class="asks">' + "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in labs) + "</ul>")
    data = [("Returned-sample tables.", "New Bennu or Ryugu compound tables, released after we seal predictions about them (tasks #11 and #19)."),
            ("Ribozyme mutant scans.", "Single-mutant fitness data for QT45, from which we seal predictions for double mutants (task #12)."),
            ("Mass spectra with assembly indices.", "The data behind assembly-index claims, to test them against a size-only baseline (task #7).")]
    s3 = block("03", "Data", "h-data", "Data released after we seal a prediction is worth the most", '<ul class="asks">' + "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in data) + "</ul>")
    ways = "".join(f"<li>{md(w)}</li>" for w in C["contribute"])
    s4 = block("04", "Other ways", "h-other", "Rerun, attack or correct anything we publish", f'<ul class="mk">{ways}</ul><p class="note">Everything is on <a href="https://github.com/HarshInvader/open-origins">GitHub</a>: open an issue to challenge a result or a pull request to correct one.</p>')
    return head + s1 + s2 + s3 + s4


# ---------------------------------------------------------------- resources
def wordmark_svg(inline=False):
    if inline:
        return (f'<svg class="word-big" viewBox="-10 -14 {150 + CH.wordmark_inner(C["name"])[1] + 20} 128" role="img" aria-label="{e(C["name"])}">'
                f'<g transform="translate(-6 -14) scale(4)" fill="none" stroke="var(--accent)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{ART.MARK}</g>'
                f'<g transform="translate(150 0)" fill="none" stroke="var(--ink)" stroke-width="10.5" stroke-linecap="round" stroke-linejoin="round">{CH.wordmark_inner(C["name"])[0]}</g></svg>')
    return CH.lockup_svg(C["name"], ART.MARK, color="#1C1B17", mark_color="#1D6670")


def mark_file():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="none" stroke="#1D6670" stroke-width="2.6" '
            f'stroke-linecap="round" stroke-linejoin="round">{ART.MARK}</svg>')


def favicon_file():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><style>g{stroke:#1D6670}@media (prefers-color-scheme: dark){g{stroke:#79C2C9}}</style>'
            f'<g fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">{ART.MARK}</g></svg>')


def page_resources():
    head = page_head("Resources", "Logos, research files and data, in one place",
                     "Download the mark and wordmark, the data behind every figure, and the list of research files in the repository.",
                     [("h-logo", "Logo"), ("h-files", "Research files"), ("h-data", "Data")])
    s1 = block("01", "Logo", "h-logo", f"The mark is {ART.NAME_MARK}", f'''
<p class="intro">One strand of RNA folded back on itself: the molecule that may once have both carried information and copied it. Use it on light backgrounds as drawn; on dark ones, use the lighter teal from the site's dark theme.</p>
<div class="logo-show"><div class="logo-tile">{mark_svg("mark-big")}</div><div class="logo-tile wide">{wordmark_svg(True)}</div></div>
<ul class="dl"><li><a href="assets/downloads/open-origins-mark.svg" download>open-origins-mark.svg</a><span>The mark alone</span></li>
<li><a href="assets/downloads/open-origins-wordmark.svg" download>open-origins-wordmark.svg</a><span>Mark and name; the name uses the system sans</span></li></ul>''')
    rows = []
    for d in sorted(p for p in EXP.iterdir() if p.is_dir() and (p / "RESULTS.md").exists()):
        first = (d / "RESULTS.md").read_text().splitlines()[0].lstrip("# ").strip()
        rows.append(f'<li><a href="https://github.com/HarshInvader/open-origins/blob/main/experiments/{e(d.name)}/RESULTS.md"><code>experiments/{e(d.name)}/RESULTS.md</code></a><span>{e(first)}</span></li>')
    docs = [("docs/PLAN.md", "The research plan and the 2027 targets"), ("docs/AGENT_BRIEF.md", "Rules of evidence every agent follows"),
            ("docs/PAPERS.csv", "The paper ledger"), ("docs/NEGATIVE_ATLAS.md", "Closed routes, each with the effect size its test could have caught; empty so far"),
            ("docs/prereg/", "Sealed plans; their hashes are in HASHES.txt")]
    rows += [f'<li><a href="https://github.com/HarshInvader/open-origins/blob/main/{e(p)}"><code>{e(p)}</code></a><span>{e(w)}</span></li>' for p, w in docs if (ROOT / p).exists()]
    s2 = block("02", "Files", "h-files", "Every result has a file you can rerun", f'''
<p class="intro">Each path links to the file in the <a href="https://github.com/HarshInvader/open-origins">public repository</a>.</p><ul class="dl">{"".join(rows)}</ul>''')
    files = "".join(f'<li><a href="{e(h)}" download>{e(n)}</a><span>{e(w)} · {e(s)}</span></li>' for n, h, w, s in data_list())
    s3 = block("03", "Data", "h-data", "The data behind every figure, free to download", f'<ul class="dl">{files}</ul>')
    return head + s1 + s2 + s3



# ---------------------------------------------------------------- data catalogue
TIER_TEXT = {
    "included": ("In this repository", "Tables this project made, in datasets/open/ (CC BY 4.0)"),
    "fetch": ("Public, fetch it yourself", "Open deposits: datasets/fetch.py gets the subsets our results use; the rest link to their source"),
    "request": ("On request", "Physical samples lent after a reviewed proposal; only the human lead applies"),
    "reference-only": ("Reference only", "Paywalled, unlicensed or web-only: cited, not reusable as data"),
}
WANTED = [
    "Yields and rates for each prebiotic step run on the previous step's crude output, not on purified inputs. This decides whether any route runs end to end.",
    "Any per-cycle measurement of a replicator whose copies outgrow its decay. QT45 shrinks by about half per cycle on its own numbers.",
    "QT45 double-mutant fitness, which our sealed prediction (task #12) is waiting for.",
    "A non-enumerated abiotic reference set: formula lists from meteorite and spark-discharge mass spectrometry. Schmitt-Kopplin 2010 has no deposit.",
    "A downloadable prebiotic reaction network. NOEL and the Wołos 2020 network can only be browsed; KEGG and MetaCyc need a subscription.",
    "Harmonised compound-abundance tables for Bennu and Ryugu. The instrument data are open but raw, tens of GB per bundle.",
    "Any open dataset on vesicles or membranes under prebiotic conditions, and one open compilation of banded-iron and stromatolite records. We found neither.",
]
CATALOG = ROOT / "datasets" / "catalog.csv"


def page_data():
    rows = list(csv.DictReader(open(CATALOG, newline="", encoding="utf-8")))
    by = {t: [r for r in rows if r["tier"] == t] for t in TIER_TEXT}
    ver = sum(r["verified"] == "yes" for r in rows)
    used = sum(r["used_by_us"] == "yes" for r in rows)
    head = page_head("Data", "Most origin-of-life data is open; the data that would confirm a route does not exist yet",
                     f"We list {len(rows)} datasets: {len(by['included'])} we made, {len(by['fetch'])} public sets anyone can fetch, "
                     f"{len(by['request'])} sample collections on request and {len(by['reference-only'])} that are cited but not reusable. "
                     f"We opened {ver} of them at their DOI, API or landing page on 18 Nov 2026. {used} feed our results today.",
                     [("h-included", "Catalogue"), ("h-wanted", "Missing"), ("h-get", "Get it")])
    secs = []
    for t, (label, intro) in TIER_TEXT.items():
        trs = []
        for r in sorted(by[t], key=lambda r: (r["used_by_us"] != "yes", r["title"].lower())):
            o = r["origin"]
            name = f'<a href="{e(o)}">{e(r["title"])}</a>' if o.startswith("http") else e(r["title"])
            marks = ('<span class="chip chip-ok">used by us</span> ' if r["used_by_us"] == "yes" else "") + \
                    ("" if r["verified"] == "yes" else '<span class="chip chip-warn">not verified</span>')
            trs.append(f'<tr><th scope="row">{name}<span class="sub">{e(r["id"])} · {e(r["kind"])}</span></th>'
                       f'<td>{e(r["terms"])}</td><td>{e(r["size"]) or "–"}</td><td>{e(r["serves_tasks"]) or "–"}</td><td>{marks or "–"}</td></tr>')
        table = ('<div class="tablewrap"><table class="score"><thead><tr><th scope="col">Dataset</th><th scope="col">Terms</th>'
                 '<th scope="col">Size</th><th scope="col">Tasks</th><th scope="col">Status</th></tr></thead>'
                 f'<tbody>{"".join(trs)}</tbody></table></div>')
        secs.append(block(f"{len(secs) + 1:02d}", label, f"h-{t}", f"{len(by[t])} {label.lower()}", f'<p class="intro">{e(intro)}.</p>{table}'))
    unver = ", ".join(r["id"] for r in rows if r["verified"] != "yes")
    wanted = "".join(f"<li>{md(w)}</li>" for w in WANTED)
    secs.append(block(f"{len(secs) + 1:02d}", "Missing", "h-wanted", "Missing, and wanted",
                      '<p class="intro">No archive holds the measurements that would confirm or close a route, because nobody has made them. '
                      'If you hold any of these, the <a href="contribute.html">Contribute</a> page says how to share them.</p>'
                      f'<ul class="mk">{wanted}</ul><p class="note">Not verified: {e(unver)}. Each catalogue row says why.</p>'))
    secs.append(block(f"{len(secs) + 1:02d}", "Get it", "h-get", "One file lists them all; one script fetches what we use",
                      f'<ul class="dl"><li><a href="data/catalog.csv" download>catalog.csv</a><span>Every row, with how it was checked · {size_of(CATALOG)}</span></li></ul>'
                      f'<p class="note">In the <a href="{REPO}/tree/main/datasets">repository</a>, <code>python3 -I datasets/fetch.py list</code> prints the catalogue '
                      'and <code>fetch &lt;id&gt;</code> downloads a subset into <code>datasets/local/</code>. Downloads stay under 1.5 GB in total. '
                      'Nothing third-party is republished here.</p>'))
    return head + "".join(secs)


# ---------------------------------------------------------------- link check
class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k) is not None:
                self.refs.append(a[k])


def check_links():
    """Every internal href and src must resolve to a file in dist (or the parent site for ../index.html), and every
    #fragment must exist in its target page. Returns (n_checked, n_external, broken)."""
    pages = {p.name: p for p in DIST.glob("*.html")}
    parsed = {}
    for name, p in pages.items():
        lp = _Links()
        lp.feed(p.read_text())
        parsed[name] = lp
    broken, n, ext = [], 0, 0
    for name, lp in parsed.items():
        for ref in lp.refs:
            u = urlsplit(ref)
            if u.scheme in ("http", "https", "mailto") or ref.startswith("data:"):
                ext += 1
                continue
            n += 1
            path = unquote(u.path)
            if path == "../index.html":
                continue  # parent site, copied alongside by open-citizen-science/build.py
            target = name if path == "" else path
            f = DIST / target
            if not f.exists():
                broken.append(f"{name}: {ref} (missing file)")
                continue
            if u.fragment and target.endswith(".html"):
                ids = parsed[target].ids if target in parsed else set()
                if u.fragment not in ids:
                    broken.append(f"{name}: {ref} (missing #{u.fragment})")
    return n, ext, broken


def assets_check():
    """Images under 4 MB in total; robots meta on every page."""
    imgs = sum(p.stat().st_size for p in (DIST / "assets").rglob("*") if p.suffix in (".webp", ".png", ".jpg", ".svg"))
    no_robots = [p.name for p in DIST.glob("*.html") if '<meta name="robots" content="noindex, nofollow">' not in p.read_text()]
    return imgs, no_robots


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets" / "downloads").mkdir(parents=True)
    (DIST / "data").mkdir()
    (DIST / "assets" / "site.css").write_text((SITE / "site.css").read_text() + "\n" + (SITE / "family.css").read_text() + "\n" + (SITE / "brand.css").read_text())
    shutil.copytree(SITE / "assets" / "fonts", DIST / "assets" / "fonts")
    shutil.copy2(SITE / "assets" / "site.js", DIST / "assets" / "site.js")
    (DIST / "assets" / "favicon.svg").write_text(favicon_file())
    (DIST / "assets" / "downloads" / "open-origins-mark.svg").write_text(mark_file())
    (DIST / "assets" / "downloads" / "open-origins-wordmark.svg").write_text(wordmark_svg())
    news_src = SITE / "assets" / "news"
    if news_src.exists():
        shutil.copytree(news_src, DIST / "assets" / "news")
    for n, src, _ in DATA_FILES:
        shutil.copy2(src, DIST / "data" / n)
    desc = C["goal"]
    render("index.html", f"{C['name']}: {C['goal']}", desc, "index.html", page_index(), "home")
    render("findings.html", f"Findings · {C['name']}", "What is known about how life began, what has been tried, and what our tests add.", "findings.html", page_findings())
    render("map.html", f"Pathway map · {C['name']}", "Four proposed routes to the origin of life, scored hand-off by hand-off.", "map.html", page_map())
    render("theories.html", f"Theories · {C['name']}", C["theories_lede"], "theories.html", page_theories())
    render("approach.html", f"Approach · {C['name']}", C["approach_lede"], "approach.html", page_approach())
    render("tracker.html", f"Tracker · {C['name']}", "The live task board.", "tracker.html", page_tracker())
    render("news.html", f"News · {C['name']}", "New research on how life began, summarised.", "news.html", page_news())
    render("contribute.html", f"Contribute · {C['name']}", "Open tasks for AI agents, and asks for wet labs and data holders.", "contribute.html", page_contribute())
    render("data.html", f"Data · {C['name']}", "Every open dataset on the origin of life, its terms, and whether we use it.", "data.html", page_data())
    render("resources.html", f"Resources · {C['name']}", "Logos, research files and data downloads.", "resources.html", page_resources())
    for i, n in enumerate(NEWS):
        prev = NEWS[i - 1] if i > 0 else None
        nxt = NEWS[i + 1] if i + 1 < len(NEWS) else None
        render(f"news-{n['id']}.html", f"{n['head']} · {C['name']}", n["gist"][:180], "news.html", news_article(n, prev, nxt))
    (DIST / "news.xml").write_text(news_rss())
    pages = sorted(p.name for p in DIST.glob("*.html"))
    print(f"wrote {len(pages)} pages, news.xml, assets and {len(DATA_FILES)} data files to {DIST}")
    n, ext, broken = check_links()
    imgs, no_robots = assets_check()
    print(f"link check: {n} internal links and assets checked, {ext} external links skipped, {len(broken)} broken")
    print(f"images: {imgs / 1024:.0f} KB in total (limit 4096 KB); pages without the robots meta: {len(no_robots)}")
    for b in broken:
        print("  BROKEN", b)
    if broken or no_robots or imgs > 4 * 1024 * 1024:
        sys.exit(1)


if __name__ == "__main__":
    main()
