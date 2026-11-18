"""Crossref lookup. Usage: cr.py q "bibliographic query" [rows] | cr.py doi DOI"""
import sys, json, urllib.request, urllib.parse, urllib.error
UA = {"User-Agent": "citation-checker/0.1"}
import time
def get(url):
    for i in range(5):
        try:
            time.sleep(1.5)
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as ex:
            if ex.code == 429: time.sleep(5 * (i + 1)); continue
            raise
    raise RuntimeError("rate limited")
def fmt(m):
    au = m.get("author", [])
    names = ", ".join(a.get("family", a.get("name", "?")) for a in au[:4]) + (f" ... ({len(au)} authors)" if len(au) > 4 else "")
    d = (m.get("published-print") or m.get("published-online") or m.get("issued") or {}).get("date-parts", [[None]])[0]
    don = (m.get("published-online") or {}).get("date-parts", [[None]])[0]
    return f"{m.get('DOI')} | {names} | {d} online {don} | {(m.get('container-title') or [''])[0]} {m.get('volume','')}:{m.get('page', m.get('article-number',''))} | {(m.get('title') or [''])[0][:150]}"
if sys.argv[1] == "abs":
    import re
    for d in sys.argv[2:]:
        m = get("https://api.crossref.org/works/" + urllib.parse.quote(d))["message"]
        print(fmt(m)); print("   ABS:", re.sub("<[^>]+>", "", m.get("abstract", "(none)"))[:2500]); print()
    sys.exit()
if sys.argv[1] == "doi":
    for d in sys.argv[2:]:
        try: print(fmt(get("https://api.crossref.org/works/" + urllib.parse.quote(d))["message"]))
        except Exception as ex: print(d, "ERROR", ex)
else:
    rows = sys.argv[3] if len(sys.argv) > 3 else "3"
    for it in get("https://api.crossref.org/works?rows=" + rows + "&filter=from-pub-date:2023-01-01,type:journal-article&query.bibliographic=" + urllib.parse.quote(sys.argv[2]))["message"]["items"]:
        print(fmt(it))
