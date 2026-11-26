"""Merge coder batches; keep the first 40 eligible prebiotic and first 20 eligible comparison papers in seed-0 rank order."""
import csv, glob, io
NEED = {"prebiotic": 40, "comparison": 20}
rank = {}
for s in NEED:
    for r in csv.DictReader(open(f"frame_{s}.csv")): rank[r["pmcid"]] = (s, int(r["rank"]), r)
def read(pattern):
    out = []
    for f in sorted(glob.glob(pattern)):
        txt = open(f).read().replace("\r", "")
        out += list(csv.DictReader(io.StringIO(txt)))
    return out
scr = {r["pmcid"].strip(): r for r in read("batches/screening_b*.csv")}
ext = read("batches/extraction_b*.csv")
s1 = {r["pmcid"]: r for r in csv.DictReader(open("stage1_prebiotic.csv"))}
keep, rows = set(), []
for s in NEED:
    order = sorted([p for p in rank if rank[p][0] == s], key=lambda p: rank[p][1])
    n = 0
    for p in order:
        if n >= NEED[s]: status = "not_screened_quota_met"; reason = ""
        elif s == "prebiotic" and s1[p]["stage1"] == "excluded": status, reason = "excluded_stage1", s1[p]["reason"]
        elif p not in scr: status, reason = "NOT_YET_SCREENED", ""
        else:
            e = scr[p]["eligible"].strip().upper().startswith("Y")
            nh = sum(1 for r in ext if r["paper_id"].strip() == p)
            if e and nh == 0: e = False; scr[p]["reason"] = "coded eligible but no hand-off rows"
            status, reason = ("included" if e else "excluded_fulltext"), scr[p]["reason"]
            if e: n += 1; keep.add(p)
        r = rank[p][2]
        rows.append([s, rank[p][1], p, r["doi"], r["year"], r["journal"], r["title"], status, reason])
    print(s, "included", n)
with open("screening.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["set", "rank", "pmcid", "doi", "year", "journal", "title", "status", "reason"]); w.writerows(rows)
cols = "set,paper_id,pmcid,doi,year,handoff,step_n,step_n1,end_pH,end_T,rt_only,end_conc,solvent,carry,uses_authentic,workup,si_used,evidence".split(",")
with open("extraction.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in ext:
        if r["paper_id"].strip() in keep: w.writerow([(r.get(c) or "").strip() for c in cols])
