"""Task #28: do Mrnjavac 2026 metabolic strata track enzyme age and metal catalysis?
Prereg: docs/prereg/metabolic_strata_age.md (sha256 406b3e37...). Planted checks run first; real test only if they pass.
Usage: .venv/bin/python -I experiments/metabolic_strata/strata_test.py
"""
import json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
T = HERE / "raw/tables"
RID = re.compile(r"R\d{5}")


def load():
    s = pd.read_excel(T / "aef3128_table_s8.xlsx", sheet_name="Stratification", header=None)
    rank, cur = {}, None
    for a, b in zip(s[0], s[1]):
        if isinstance(a, str):
            m = re.match(r"Rank (\d+) reactions", a)
            cur = int(m.group(1)) if m else None
        elif cur is not None and isinstance(b, str):
            m = RID.search(str(b))
            if m:
                rank[m.group(0)] = min(rank.get(m.group(0), 99), cur)
    rx = pd.read_excel(T / "aef3128_table_s8.xlsx", sheet_name="Reactions")
    path = {}
    for rid, p in zip(rx["Reaction ID"].astype(str), rx["Pathway"]):
        m = RID.search(str(rid))
        if m and m.group(0) not in path and isinstance(p, str):
            path[m.group(0)] = p
    d = pd.read_excel(T / "aef3128_table_s2.xlsx", sheet_name="Distribution")
    cats = {}
    for rids, c in zip(d["Reaction ID"].astype(str), d["Category"]):
        for r in RID.findall(str(rids)):
            cats.setdefault(r, set()).add(str(c))
    def age(cs, gray):
        if "LUCA" in cs: return "LUCA"
        lin = {"LBCA", "LACA"} | ({"gray LBCA", "gray LACA"} if gray else set())
        if cs & lin: return "lineage"
        return None
    m4 = pd.read_excel(T / "aef3128_table_s4.xlsx", header=3)
    gcol = [c for c in m4.columns if str(c).startswith("Reaction reported experimentally in aqueous")][0]
    grade = {}
    for rid, g in zip(m4["Reaction ID"].astype(str), m4[gcol]):
        for r in RID.findall(str(rid)):
            if isinstance(g, str) and g.strip():
                grade[r] = min(grade.get(r, "Z"), g.strip()[0])
    mo = pd.read_excel(T / "aef3128_table_s2.xlsx", sheet_name="Comparison Moody et al. 2024")
    moody = {}
    for rids, y in zip(mo.iloc[:, 1].astype(str), mo.iloc[:, 2].astype(str)):
        for r in RID.findall(str(rids)):
            moody[r] = moody.get(r, False) or str(y).strip().lower() == "yes"
    rows = []
    for r, k in rank.items():
        cs = cats.get(r, set())
        rows.append(dict(rid=r, stratum=k, pathway=path.get(r, "none"),
                         age=age(cs, False), age_gray=age(cs, True), cats=",".join(sorted(cs)),
                         grade=grade.get(r), moody=moody.get(r)))
    return pd.DataFrame(rows)


def perm_test(df, lab, n=10000, seed=0, within=True, y="stratum"):
    """lab: boolean Series ('old'). D = mean(y|old) - mean(y|young); one-sided p for D<0."""
    sub = df[lab.notna()].copy()
    sub["L"] = lab[lab.notna()].astype(bool).values
    yv = sub[y].to_numpy(float); L = sub["L"].to_numpy()
    d_obs = yv[L].mean() - yv[~L].mean()
    rng = np.random.default_rng(seed)
    groups = [np.flatnonzero((sub["pathway"] == p).to_numpy()) for p in sub["pathway"].unique()] if within else [np.arange(len(sub))]
    cnt = 0; Lp = L.copy()
    for _ in range(n):
        for g in groups:
            Lp[g] = rng.permutation(L[g])
        cnt += (yv[Lp].mean() - yv[~Lp].mean()) <= d_obs + 1e-12
    return dict(D=float(d_obs), p=(1 + cnt) / (n + 1), n_old=int(L.sum()), n_young=int((~L).sum()))


def within_pct(df):
    return df.groupby("pathway")["stratum"].rank(pct=True)


def planted(df, n_old):
    base = df[df.age.notna()].copy()
    med = base.groupby("pathway")["stratum"].transform("median")
    pow_hits = null_hits = 0
    for s in range(1, 201):
        rng = np.random.default_rng(s)
        pr = np.where(base["stratum"] < med, 0.7, np.where(base["stratum"] > med, 0.3, 0.5))
        lab = pd.Series(rng.random(len(base)) < pr, index=base.index)
        pow_hits += perm_test(base, lab, n=2000, seed=s)["p"] < 0.05
        lab0 = base.groupby("pathway")["age"].transform(lambda x: x.sample(frac=1, random_state=s).values) == "LUCA"
        null_hits += perm_test(base, lab0, n=2000, seed=s + 1000)["p"] < 0.05
    return dict(power=pow_hits / 200, null_rate=null_hits / 200,
                pass_=bool(pow_hits / 200 >= 0.8 and null_hits / 200 <= 0.08))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(order):
        run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj


if __name__ == "__main__":
    df = load()
    print("stratified base IDs:", len(df), "| age labelled:", df.age.notna().sum(),
          "| graded S4:", df.grade.notna().sum(), "| moody labelled:", df.moody.notna().sum())
    pl = planted(df, None)
    print("PLANTED:", pl)
    out = dict(task=28, prereg_sha256="406b3e3779f2b15b54fb5758a2e88b5f9e245a48a106ba481cd7737714ed8abe",
               n=dict(stratified=len(df), age=int(df.age.notna().sum()), grade=int(df.grade.notna().sum()),
                      moody=int(df.moody.notna().sum())), planted=pl)
    if not pl["pass_"]:
        print("planted check FAILED; real test not interpreted"); (HERE / "results.json").write_text(json.dumps(out, indent=2)); sys.exit(1)
    age = df.age.map({"LUCA": True, "lineage": False})
    metA = df.grade.eq("A").astype(object)
    moody = df.moody.map({True: True, False: False})
    tests = {"H1_age": age, "H2_metalA": metA, "H3_moody": moody}
    res = {}
    for k, lab in tests.items():
        res[k] = dict(within=perm_test(df, lab), glob=perm_test(df, lab, within=False),
                      within_pct=perm_test(df.assign(pct=within_pct(df)), lab, y="pct"))
    adj = holm([res[k]["within"]["p"] for k in tests])
    for k, a in zip(tests, adj): res[k]["within"]["p_holm"] = a
    # H4 splits
    for lin in ("LBCA", "LACA"):
        sel = df.cats.str.contains("LUCA") | (df.cats.str.contains(lin) & ~df.cats.str.contains("LUCA"))
        sub = df[sel & df.age.notna()]
        lab = sub.age.map({"LUCA": True, "lineage": False})
        res[f"H4_LUCA_vs_{lin}"] = dict(within=perm_test(sub, lab), glob=perm_test(sub, lab, within=False))
    res["H5_metalAB"] = dict(within=perm_test(df, df.grade.isin(["A", "B"]).astype(object)),
                             glob=perm_test(df, df.grade.isin(["A", "B"]).astype(object), within=False))
    res["S_age_gray"] = dict(within=perm_test(df, df.age_gray.map({"LUCA": True, "lineage": False})))
    # descriptive means
    res["means"] = {g: float(v) for g, v in df.groupby(df.age.fillna("unlabelled"))["stratum"].mean().items()}
    res["means_grade"] = {g: float(v) for g, v in df.groupby(df.grade.fillna("none"))["stratum"].mean().items()}
    out["results"] = res
    print(json.dumps(res, indent=1))
    (HERE / "results.json").write_text(json.dumps(out, indent=2))
    df.to_csv(HERE / "reactions_labelled.csv", index=False)
