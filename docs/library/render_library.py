#!/usr/bin/env python3
"""Render docs/library/library.json to docs/library/LIBRARY.md.

Run from the repo root:  python3 -I docs/library/render_library.py
Standard library only. library.json is the source; do not edit LIBRARY.md by hand.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "library.json").read_text())
P = D["papers"]
ORDER = {"core": 0, "useful": 1, "context": 2}


def one(s):
    return " ".join(str(s or "").split())


lines = ["# Open Origins paper library", "",
         f"Generated from `library.json` on {D['updated']}. {len(P)} papers: "
         f"{sum(p['read_depth'] == 'full' for p in P)} read in full, {sum(p['read_depth'] != 'full' for p in P)} from the abstract only; "
         f"{sum(bool(p.get('imported')) for p in P)} imported from `docs/PAPERS.csv`.", "",
         "Relevance: **core** bears directly on a current study; **useful** feeds a step, a table or a planned test; **context** is background. "
         "Citations marked (unverified) have not been checked against the DOI record.", "",
         "Ideas drawn from these papers are in [IDEAS.md](IDEAS.md). The same library, searchable, is `library.html` on the project site.", ""]
topics = sorted({p["topic"] for p in P})
lines.append("## Topics")
lines += [f"- [{t}](#{t.lower().replace(' ', '-')}) ({sum(p['topic'] == t for p in P)})" for t in topics]
lines.append("")
flagged = [p for p in P if p.get("changes_plan")]
if flagged:
    lines += ["## Papers that bear on a current study's plan", ""]
    lines += [f"- **{p['id']}** ({', '.join(p.get('touches', []))}): {one(p['changes_plan'])}" for p in flagged]
    lines.append("")
for t in topics:
    lines += [f"## {t}", ""]
    for p in sorted((p for p in P if p["topic"] == t), key=lambda p: (ORDER.get(p["relevance"], 3), -int(str(p["year"])[:4]), p["id"])):
        doi = f"[doi:{p['doi']}]({p['url']})" if p.get("doi") else (p.get("url") or "")
        flags = [p["relevance"], "full text" if p["read_depth"] == "full" else "abstract only"]
        if p.get("in_news"):
            flags.append("in news")
        if not p.get("verified"):
            flags.append("(unverified)")
        lines += [f"### {one(p['title'])}", "",
                  f"{one(p['authors'])} ({p['year']}). *{one(p['venue'])}*. {doi}. `{p['id']}` · {' · '.join(flags)}"
                  + (f" · touches {', '.join(p['touches'])}" if p.get("touches") else ""), ""]
        for k, lab in (("question", "Question"), ("tried", "Tried"), ("method_data", "Method and data"), ("key_results", "Key results"),
                       ("limits", "Limits"), ("ideas_for_us", "Ideas for us"), ("changes_plan", "Changes a current plan")):
            if p.get(k):
                lines.append(f"- **{lab}.** {one(p[k])}")
        lines.append("")
(HERE / "LIBRARY.md").write_text("\n".join(lines).rstrip() + "\n")
print(f"wrote LIBRARY.md: {len(P)} papers")
