"""Fetch the sealed Europe PMC frames and produce seed-0 random screening orders (task #31)."""
import json, time, urllib.request, urllib.parse, numpy as np, csv
UA = {"User-Agent": "open-research-site/1.0"}
Q = {
 "prebiotic": '(TITLE_ABS:"prebiotic") AND (TITLE_ABS:"synthesis" OR TITLE_ABS:"formation") AND (TITLE_ABS:nucleotide* OR TITLE_ABS:nucleoside* OR TITLE_ABS:sugar* OR TITLE_ABS:ribose OR TITLE_ABS:"amino acid*" OR TITLE_ABS:peptide* OR TITLE_ABS:lipid* OR TITLE_ABS:"fatty acid*" OR TITLE_ABS:phospholipid*) AND OPEN_ACCESS:y AND HAS_FT:y AND PUB_YEAR:[2010 TO 2025] AND PUB_TYPE:"research-article" AND SRC:MED',
 "comparison": '(JOURNAL:"Beilstein J Org Chem") AND (TITLE_ABS:"total synthesis" OR TITLE_ABS:"multistep synthesis" OR TITLE_ABS:"multi-step synthesis" OR TITLE_ABS:"steps") AND OPEN_ACCESS:y AND HAS_FT:y AND PUB_YEAR:[2010 TO 2025] AND PUB_TYPE:"research-article" AND SRC:MED',
}
def get(url):
    for i in range(8):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90))
        except Exception as e:
            time.sleep(5 * (i + 1))
    raise RuntimeError(url)
def fetch(q):
    out, cur = [], "*"
    while True:
        u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
            {"query": q, "format": "json", "pageSize": 1000, "resultType": "lite", "cursorMark": cur})
        r = get(u); res = r["resultList"]["result"]; out += res
        nxt = r.get("nextCursorMark")
        if not res or not nxt or nxt == cur or len(out) >= r["hitCount"]: return r["hitCount"], out
        cur = nxt
for name, q in Q.items():
    n, res = fetch(q)
    d = {}
    for x in res:
        if x.get("pmcid"): d[x["pmcid"]] = x
    keys = sorted(d, key=lambda k: int(k[3:]))
    perm = np.random.default_rng(0).permutation(len(keys))
    with open(f"frame_{name}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["rank", "pmcid", "doi", "year", "journal", "title"])
        for r_, i in enumerate(perm):
            x = d[keys[i]]
            w.writerow([r_, x["pmcid"], x.get("doi", ""), x.get("pubYear"), x.get("journalTitle"), x.get("title")])
    print(name, "hitCount", n, "with pmcid", len(keys))
