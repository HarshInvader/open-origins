"""Stats for the sealed reporting audit (task #31). Usage: audit.py [--planted]"""
import sys, json, csv, numpy as np
from scipy.stats import spearmanr

ITEMS = ["end_pH", "end_T", "end_conc", "solvent", "carry", "workup"]

def load(path):
    with open(path) as f:
        return list(csv.DictReader(f))

def rep(r, item, s_counts=False, na_ok=True, rt_ok=False):
    v = r[item].strip()
    if item == "end_pH":
        if v == "NA": return na_ok
        return v == "E" or (s_counts and v == "S")
    if item == "end_T" and rt_ok and r.get("rt_only", "0").strip() == "1": return True
    return v == "Y"

def all4(r, **kw):
    return all(rep(r, i, **kw) for i in ["end_pH", "end_T", "end_conc", "solvent"])

def by_paper(rows):
    d = {}
    for r in rows: d.setdefault(r["paper_id"], []).append(r)
    return d

def pooled_share(papers, f):
    num = sum(sum(f(r) for r in rs) for rs in papers)
    den = sum(len(rs) for rs in papers)
    return num / den if den else float("nan")

def mean_share(papers, f):
    return float(np.mean([np.mean([f(r) for r in rs]) for rs in papers]))

def boot_diff(pa, pb, f, stat=pooled_share, B=10000, seed=0):
    rng = np.random.default_rng(seed)
    A, Bp = list(pa.values()), list(pb.values())
    obs = stat(A, f) - stat(Bp, f)
    ds = np.empty(B)
    for b in range(B):
        ia = rng.integers(0, len(A), len(A)); ib = rng.integers(0, len(Bp), len(Bp))
        ds[b] = stat([A[i] for i in ia], f) - stat([Bp[i] for i in ib], f)
    lo, hi = np.percentile(ds, [2.5, 97.5])
    return float(obs), float(lo), float(hi)

def p1(papers, s_counts=False):
    fr = []
    for rs in papers.values():
        rr = [r for r in rs if r["end_pH"].strip() != "NA"]
        if rr: fr.append(np.mean([rep(r, "end_pH", s_counts=s_counts) for r in rr]))
    return float(np.median(fr)) if fr else float("nan"), len(fr), [float(x) for x in fr]

def analyse(rows):
    pre = by_paper([r for r in rows if r["set"] == "prebiotic"])
    com = by_paper([r for r in rows if r["set"] == "comparison"])
    out = {"n_papers": {"prebiotic": len(pre), "comparison": len(com)},
           "n_handoffs": {"prebiotic": sum(map(len, pre.values())), "comparison": sum(map(len, com.values()))}}
    # item-level shares
    shares = {}
    for name, P in [("prebiotic", pre), ("comparison", com)]:
        s = {}
        for it in ITEMS:
            if it == "end_pH":
                rr = [r for rs in P.values() for r in rs if r["end_pH"].strip() != "NA"]
                s["end_pH_E_of_nonNA"] = float(np.mean([r["end_pH"].strip() == "E" for r in rr])) if rr else None
                s["end_pH_NA_handoffs"] = sum(r["end_pH"].strip() == "NA" for rs in P.values() for r in rs)
                s["end_pH_S_of_nonNA"] = float(np.mean([r["end_pH"].strip() == "S" for r in rr])) if rr else None
            else:
                s[it] = pooled_share(list(P.values()), lambda r, it=it: rep(r, it))
        s["all4"] = pooled_share(list(P.values()), all4)
        if any("uses_authentic" in r for rs in P.values() for r in rs):
            s["uses_authentic_Y"] = pooled_share(list(P.values()), lambda r: r.get("uses_authentic", "").strip() == "Y")
        shares[name] = s
    out["item_shares"] = shares
    m, n, fr = p1(pre)
    out["P1"] = {"median_frac_pH_E": m, "n_papers": n, "pass": bool(m < 0.30), "per_paper": fr}
    ms, _, _ = p1(pre, s_counts=True)
    out["P1_sens_S_counts"] = ms
    allc = [all(rep(r, "carry") for r in rs) for rs in pre.values()]
    out["P2"] = {"share_papers_carry_all": float(np.mean(allc)), "n": len(allc), "pass": bool(np.mean(allc) < 0.20)}
    obs, lo, hi = boot_diff(pre, com, all4)
    out["P3"] = {"prebiotic_all4": pooled_share(list(pre.values()), all4), "comparison_all4": pooled_share(list(com.values()), all4),
                 "diff": obs, "ci95": [lo, hi], "pass": bool(hi < 0)}
    sens = {}
    for k, f in {"S_counts": lambda r: all4(r, s_counts=True), "NA_strict": lambda r: all4(r, na_ok=False),
                 "rt_counts": lambda r: all4(r, rt_ok=True)}.items():
        o, l, h = boot_diff(pre, com, f); sens[k] = {"diff": o, "ci95": [l, h]}
    o, l, h = boot_diff(pre, com, all4, stat=mean_share); sens["per_paper_mean"] = {"diff": o, "ci95": [l, h]}
    # per-item differences (exploratory)
    for it in ["end_T", "end_conc", "solvent", "carry", "workup"]:
        o, l, h = boot_diff(pre, com, lambda r, it=it: rep(r, it)); sens["item_" + it] = {"diff": o, "ci95": [l, h]}
    o, l, h = boot_diff(pre, com, lambda r: rep(r, "end_pH", na_ok=False)); sens["item_end_pH_strict"] = {"diff": o, "ci95": [l, h]}
    out["P3_sensitivity_and_items"] = sens
    yrs, fr4 = [], []
    for rs in pre.values():
        yrs.append(int(rs[0]["year"])); fr4.append(np.mean([all4(r) for r in rs]))
    rho, p = spearmanr(yrs, fr4)
    out["P4"] = {"spearman_rho": float(rho), "p": float(p), "n": len(yrs), "pass": bool(abs(rho) < 0.2)}
    return out

def kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    po = np.mean(a == b); pa, pb = a.mean(), b.mean()
    pe = pa * pb + (1 - pa) * (1 - pb)
    if pe == 1: return 1.0 if po == 1 else 0.0
    return float((po - pe) / (1 - pe))

def reliability(prim, sec):
    P = {(r["paper_id"], r["handoff"]): r for r in prim}
    res = {}
    pairs = [(P[(r["paper_id"], r["handoff"])], r) for r in sec if (r["paper_id"], r["handoff"]) in P]
    for it in ITEMS:
        if it == "end_pH":
            pp = [(x, y) for x, y in pairs if x[it].strip() != "NA" and y[it].strip() != "NA"]
            na_agree = float(np.mean([(x[it].strip() == "NA") == (y[it].strip() == "NA") for x, y in pairs]))
            k = kappa([x[it].strip() == "E" for x, y in pp], [y[it].strip() == "E" for x, y in pp])
            res[it] = {"kappa": k, "n": len(pp), "agree": float(np.mean([(x[it].strip() == "E") == (y[it].strip() == "E") for x, y in pp])), "NA_agreement": na_agree}
        else:
            a = [x[it].strip() == "Y" for x, y in pairs]; b = [y[it].strip() == "Y" for x, y in pairs]
            res[it] = {"kappa": kappa(a, b), "n": len(pairs), "agree": float(np.mean(np.array(a) == np.array(b)))}
    res["mean_kappa"] = float(np.mean([res[i]["kappa"] for i in ITEMS]))
    res["n_pairs"] = len(pairs); res["n_secondary_rows"] = len(sec)
    res["kill"] = bool(res["mean_kappa"] < 0.6)
    return res

def planted():
    rng = np.random.default_rng(0)
    def synth(diff):
        rows = []
        for s, n, p4 in [("prebiotic", 40, 0.5 + diff), ("comparison", 20, 0.5)]:
            for i in range(n):
                for h in range(rng.integers(1, 6)):
                    ok = rng.random() < p4
                    v = "Y" if ok else "N"
                    rows.append({"set": s, "paper_id": f"{s}{i}", "handoff": str(h), "year": str(2010 + i % 16),
                                 "end_pH": "E" if ok else "N", "end_T": v, "end_conc": v, "solvent": v, "carry": v, "workup": v, "rt_only": "0"})
        return rows
    r1 = analyse(synth(-0.3)); r0 = analyse(synth(0.0))
    ok1 = abs(r1["P3"]["diff"] + 0.3) <= 0.05 and abs(r1["P3"]["comparison_all4"] - 0.5) <= 0.05 and r1["P3"]["pass"]
    ok0 = r0["P3"]["ci95"][0] <= 0 <= r0["P3"]["ci95"][1]
    return {"planted_minus0.3": r1["P3"], "planted_zero": r0["P3"], "pass": bool(ok1 and ok0)}

if __name__ == "__main__":
    if "--planted" in sys.argv:
        print(json.dumps(planted(), indent=1)); sys.exit()
    pl = planted()
    assert pl["pass"], pl
    out = {"planted_check": pl, **analyse(load("extraction.csv"))}
    try:
        out["reliability"] = reliability(load("extraction.csv"), load("reliability.csv"))
    except FileNotFoundError:
        pass
    json.dump(out, open("results.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("planted_check",)}, indent=1)[:6000])
