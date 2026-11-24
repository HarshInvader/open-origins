"""T9 (prereg docs/prereg/t9_dpann_completeness.md): does DPANN's high gene-loss rate in Huang et al. 2026
survive a check against genome completeness?

Usage (single process; run under nice):
  python -I t9_analysis.py <experiments/t9_dpann_completeness dir> gate       # published numbers and structure only
  python -I t9_analysis.py <experiments/t9_dpann_completeness dir> planted    # synthetic loss counts on the real tree
  python -I t9_analysis.py <experiments/t9_dpann_completeness dir> sealcheck  # says whether `real` would run
  python -I t9_analysis.py <experiments/t9_dpann_completeness dir> dryrun     # `real` code, labels and completeness shuffled
  python -I t9_analysis.py <experiments/t9_dpann_completeness dir> real       # the sealed test; refuses without a seal

Units: the 512 non-root branches of Huang's rooted species tree (257 tips, 255 internal), Euryarchaeota root.
Per branch: f = losses / (losses + copies), from the deposited per-species event counts (AleRax, 72-parameter
model). A branch is DPANN if it is the node labelled "DPANN" in the deposited tree or lies below it.

Blinding: `gate` reads loss counts only to test published totals and prints match flags, never a value.
`planted` never reads loss counts.  `dryrun` shuffles the DPANN label (within depth bins) and the completeness
values (over tips) before any statistic is computed.
"""
import sys, os, re, json, hashlib, math
import numpy as np
from scipy.stats import t as student_t

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t9_dpann_completeness/scripts/t9_analysis.py"
SEED = 20261127
NBOOT = 2000            # clade-block bootstrap draws (real, dryrun)
NBOOT_PLANT = 1000      # bootstrap draws inside each planted replicate
NPERM = 2000            # depth-matched label permutations (reported only)
KILL_R, SUP_R, SUP_LO = 1.15, 1.3, 1.15    # D7 thresholds (from the plan)
MIN_TIPS = 3            # D5: arm B uses internal branches with at least this many descendant tips
DEPTH_BINS = [2, 3, 5, 9, 17, 33, 10 ** 9]  # D8: internal branches binned by descendant tips: 2, 3-4, 5-8, ...
NFAM_LIKE = 7059        # number of gene families (BIC sample size)

DEP = "cache/deposit/4_Ancestral_reconstruction/"
F = {
    "sd1": "cache/supp/sheet1.tsv",
    "sd10": "cache/supp/sheet10.tsv",
    "sd20": "cache/supp/sheet20.tsv",
    "sd33": "cache/supp/sheet33.tsv",
    "ev_E": DEP + "Euryarchaeota_root/reconciliations/perspecies_eventcount_transfer_corrected.txt",
    "tr_E": DEP + "Euryarchaeota_root/species_trees/inferred_species_tree.newick",
    "st_E": DEP + "Euryarchaeota_root/species_trees/starting_species_tree.newick",
    "mp_E": DEP + "Euryarchaeota_root/model_parameters/model_parameters.txt",
    "ev_M": DEP + "MHH_root/reconciliations/perspecies_eventcount_transfer_corrected.txt",
    "tr_M": DEP + "MHH_root/species_trees/inferred_species_tree.newick",
    "st_M": DEP + "MHH_root/species_trees/starting_species_tree.newick",
    "mp_M": DEP + "MHH_root/model_parameters/model_parameters.txt",
}
INPUT_SHA = {  # sha256 of every file read; check_inputs() stops on a mismatch
    "sd1": "fd9767fe177f9a29309adc68e7fc35c89cd18389e3c7fecd1520e86940608524",
    "sd10": "c405af80c41526ca1e9348050b6ab15df67db0277f76b0b00986fb64255e0e98",
    "sd20": "da0bd267bbb977d15001eedf0708a34161b32df8bccb77279fabe1f2017c4ec0",
    "sd33": "c565ab0b094c491fe1264db5bc1bdac32125914b848ddb18442a60db525bece8",
    "ev_E": "5173c698353fc66ef746347fe1f49501a87a2de4a4a28f3cb58e0765359ffe56",
    "tr_E": "97009007b4a205a52f84b1d0eb0e7de85223302e5a9e2f774e69a170c370cf7e",
    "st_E": "872e0ae2ff2153fb2c1ddd9ba41e6861f46f283d0afd76403e3133068f1b4e4d",
    "mp_E": "c8ca0b4bb20340b57be1b668cd993ada38ecbefd08379a60ac20fda3e0c3124f",
    "ev_M": "a2d24df401868ffc5485f5d417378883488730f8bf0ec9f0a4d58d04e3a2ad2e",
    "tr_M": "1eba48f214bd025ba4179ce67f33d62ff64953b101ab909fa8444b60a7e158cd",
    "st_M": "9e2141b051ee85d6a4459efce9b4cd6e098e60c13586524daf1e57c20183c632",
    "mp_M": "4078e23fc18844af9ecf8b07740b3321f3d969e57c7ff77c626d3f0af4642d13",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def path(k):
    return os.path.join(D, F[k])


def check_inputs():
    bad = [k for k in F if INPUT_SHA.get(k) != sha256(path(k))]
    if bad:
        sys.exit("input hash mismatch: %s" % ", ".join("%s=%s" % (k, sha256(path(k))) for k in bad))


def seal_status():
    """`real` runs only if HASHES.txt has a line naming this script with its current sha256."""
    me = sha256(os.path.abspath(__file__))
    hp = os.path.join(REPO, "docs", "prereg", "HASHES.txt")
    named = hashed = False
    if os.path.exists(hp):
        for line in open(hp, encoding="utf-8"):
            if SELF in line:
                named = True
                if line.split()[:1] == [me]:
                    hashed = True
    return {"script_sha256": me, "line_naming_script": named, "line_with_current_hash": hashed,
            "real_allowed": named and hashed}


def dump(name, obj, sub="scripts_out"):
    os.makedirs(os.path.join(D, sub), exist_ok=True)
    with open(os.path.join(D, sub, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=False, default=float)
    print(json.dumps(obj, indent=1, default=float)[:20000])


# ---------------------------------------------------------------- loading (structure)
def parse_newick(s):
    """Return list of nodes: dict(name, parent, children, length). Index 0 is the root."""
    s = s.strip().rstrip(";")
    nodes, stack, i, cur = [], [], 0, None
    tok = re.compile(r"[^(),:;]+")

    def new(parent):
        nodes.append({"name": None, "parent": parent, "children": [], "length": None})
        if parent is not None:
            nodes[parent]["children"].append(len(nodes) - 1)
        return len(nodes) - 1

    cur = new(None)
    while i < len(s):
        c = s[i]
        if c == "(":
            cur = new(cur)
            i += 1
        elif c == ",":
            cur = new(nodes[cur]["parent"])
            i += 1
        elif c == ")":
            cur = nodes[cur]["parent"]
            i += 1
        elif c == ":":
            m = tok.match(s, i + 1)
            nodes[cur]["length"] = float(m.group(0))
            i = m.end()
        else:
            m = tok.match(s, i)
            nodes[cur]["name"] = m.group(0).strip()
            i = m.end()
    return nodes


class Tree:
    def __init__(self, text):
        nd = parse_newick(text)
        self.n = len(nd)
        self.name = [x["name"] for x in nd]
        self.parent = np.array([-1 if x["parent"] is None else x["parent"] for x in nd])
        self.children = [x["children"] for x in nd]
        self.length = np.array([np.nan if x["length"] is None else x["length"] for x in nd])
        self.is_tip = np.array([len(c) == 0 for c in self.children])
        # postorder
        order, st = [], [(0, False)]
        while st:
            v, done = st.pop()
            if done:
                order.append(v)
            else:
                st.append((v, True))
                for c in self.children[v]:
                    st.append((c, False))
        self.post = np.array(order)
        self.pre = self.post[::-1].copy()
        self.ntips = np.zeros(self.n, int)
        self.tipset = [None] * self.n
        for v in self.post:
            if self.is_tip[v]:
                self.ntips[v] = 1
                self.tipset[v] = frozenset([self.name[v]])
            else:
                self.ntips[v] = sum(self.ntips[c] for c in self.children[v])
                self.tipset[v] = frozenset().union(*[self.tipset[c] for c in self.children[v]])
        self.idx = {nm: i for i, nm in enumerate(self.name)}

    def subtree(self, v):
        out, st = [], [v]
        while st:
            x = st.pop()
            out.append(x)
            st.extend(self.children[x])
        return out

    def splits(self):
        return set(self.tipset[v] for v in range(self.n) if not self.is_tip[v])


def read_events(p):
    lines = [l.rstrip("\n").split(",") for l in open(p, encoding="utf-8") if l.strip()]
    head = lines[0]
    return head, {r[0]: dict(zip(head[1:], map(float, r[1:]))) for r in lines[1:]}


def read_sd1():
    rows = [l.rstrip("\n").split("\t") for l in open(path("sd1"), encoding="utf-8")]
    head = rows[3]
    out = {}
    for r in rows[4:]:
        if len(r) < len(head) or r[-1] != "focal":
            continue
        acc = r[0].strip()
        out[acc.replace("_", "-")] = {"acc": acc, "c1": float(r[1]), "c2": float(r[4]),
                                      "gtdb202": r[17], "phylum": r[17].split(";")[1][3:] if ";" in r[17] else ""}
    return head, out


def rate_classes(p, tree):
    """Class id per node from identical (D, L, T) triplets in model_parameters.txt. Values are not kept."""
    trip, orig = {}, {}
    for l in open(p, encoding="utf-8"):
        t = l.split()
        trip[t[0]] = tuple(t[1:4])
        orig[t[0]] = t[4]
    keys = sorted(set(trip.values()))
    kid = {k: i for i, k in enumerate(keys)}
    cls = np.array([kid[trip[tree.name[v]]] for v in range(tree.n)])
    return cls, len(keys), len(set(orig.values()))


class Data:
    def __init__(self, root="E"):
        self.root = root
        self.tree = Tree(open(path("tr_" + root), encoding="utf-8").read())
        t = self.tree
        st = Tree(open(path("st_" + root), encoding="utf-8").read())
        self.sublen = np.array([st.length[st.idx[nm]] if nm in st.idx else np.nan for nm in t.name])
        self.same_topology = st.splits() == t.splits() and set(st.name) == set(t.name)
        self.cls, self.nclass, self.norig = rate_classes(path("mp_" + root), t)
        _, self.sd1 = read_sd1()
        dp = t.idx["DPANN"]
        self.dpann = np.zeros(t.n, bool)
        self.dpann[t.subtree(dp)] = True
        self.nonroot = t.parent >= 0
        self.internal = self.nonroot & ~t.is_tip
        self.tips = t.is_tip
        self.c2 = np.full(t.n, np.nan)
        self.c1 = np.full(t.n, np.nan)
        for v in np.where(t.is_tip)[0]:
            r = self.sd1.get(t.name[v])
            if r:
                self.c2[v], self.c1[v] = min(r["c2"], 100.0) / 100, min(r["c1"], 100.0) / 100
        # spurious-internal-loss floor from the plan's null: prod over descendant tips of (1 - c)
        self.s_floor = self.prod_miss(self.c2)
        self.dbin = np.digitize(t.ntips, DEPTH_BINS)  # 1.. for ntips >= 2 ; tips -> 0
        self.block = self.cls * 2 + self.dpann.astype(int)

    def prod_miss(self, c):
        t = self.tree
        s = np.ones(t.n)
        for v in t.post:
            if t.is_tip[v]:
                s[v] = 1 - c[v]
            else:
                s[v] = np.prod([s[ch] for ch in t.children[v]])
        return s

    def events(self):
        head, ev = read_events(path("ev_" + self.root))
        t = self.tree
        L = np.array([ev[nm]["losses"] for nm in t.name])
        C = np.array([ev[nm]["copies"] for nm in t.name])
        return L, C


# ---------------------------------------------------------------- statistics
def frac(L, C):
    tot = L + C
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(tot > 0, L / tot, np.nan)


def block_boot(vals_a, blk_a, vals_b, blk_b, stat, rng, nboot):
    """Resample blocks with replacement inside each group; return array of stat(a_sample, b_sample)."""
    ua, ub = np.unique(blk_a), np.unique(blk_b)
    ia = [np.where(blk_a == u)[0] for u in ua]
    ib = [np.where(blk_b == u)[0] for u in ub]
    out = np.empty(nboot)
    for k in range(nboot):
        sa = np.concatenate([ia[j] for j in rng.integers(0, len(ia), len(ia))])
        sb = np.concatenate([ib[j] for j in rng.integers(0, len(ib), len(ib))])
        out[k] = stat(vals_a[sa], vals_b[sb])
    return out


def ratio_of_means(a, b):
    mb = np.nanmean(b)
    return np.nanmean(a) / mb if mb > 0 else np.nan


def ols(x, y):
    ok = ~np.isnan(x) & ~np.isnan(y)
    x, y = x[ok], y[ok]
    if len(x) < 3 or np.var(x) == 0:
        return np.nan, np.nan
    b = np.cov(x, y, bias=True)[0, 1] / np.var(x)
    return y.mean() - b * x.mean(), b


def arm_b(d, f, mask_extra=None, rng=None, nboot=NBOOT):
    m = d.internal.copy()
    if mask_extra is not None:
        m &= mask_extra
    m &= ~np.isnan(f)
    a, b = m & d.dpann, m & ~d.dpann
    r = ratio_of_means(f[a], f[b])
    bs = block_boot(f[a], d.block[a], f[b], d.block[b], ratio_of_means, rng, nboot)
    ka, kb = len(np.unique(d.block[a])), len(np.unique(d.block[b]))
    # D6: few-block interval. The block bootstrap gives the spread of log(ratio); the interval uses a
    # Student t quantile with df = (fewer blocks) - 1, because a percentile bootstrap over 7 blocks is too narrow.
    lb = np.log(bs[np.isfinite(bs) & (bs > 0)])
    sd = float(np.std(lb, ddof=1))
    q = float(student_t.ppf(0.975, max(min(ka, kb) - 1, 1)))
    lo, hi = float(np.exp(np.log(r) - q * sd)), float(np.exp(np.log(r) + q * sd))
    plo, phi = np.nanpercentile(bs, [2.5, 97.5])
    return {"ratio": r, "lo": lo, "hi": hi, "boot_sd_log": sd, "t_quantile": q,
            "percentile_lo": float(plo), "percentile_hi": float(phi), "n_dpann": int(a.sum()), "n_other": int(b.sum()),
            "blocks_dpann": int(ka), "blocks_other": int(kb),
            "mean_dpann": float(np.nanmean(f[a])), "mean_other": float(np.nanmean(f[b]))}


def arm_a(d, f, c, rng, nboot=NBOOT):
    """Tip branches outside DPANN: slope of f on (1 - completeness)."""
    m = d.tips & ~d.dpann & ~np.isnan(f) & ~np.isnan(c)
    x, y, blk = 1 - c[m], f[m], d.block[m]
    a0, b0 = ols(x, y)
    ub = np.unique(blk)
    ib = [np.where(blk == u)[0] for u in ub]
    bs = np.empty(nboot)
    for k in range(nboot):
        s = np.concatenate([ib[j] for j in rng.integers(0, len(ib), len(ib))])
        bs[k] = ols(x[s], y[s])[1]
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return {"intercept": a0, "slope": b0, "lo": lo, "hi": hi, "n": int(m.sum()), "blocks": int(len(ub)),
            "n_below_0.9": int((c[m] < 0.9).sum())}


def arm_c(d, f, c, rng, nboot=NBOOT):
    """DPANN tips: observed mean f over the mean predicted from the non-DPANN tip fit (reported only)."""
    mo = d.tips & ~d.dpann & ~np.isnan(f) & ~np.isnan(c)
    md = d.tips & d.dpann & ~np.isnan(f) & ~np.isnan(c)

    def st(idx_o, idx_d):
        a0, b0 = ols(1 - c[mo][idx_o], f[mo][idx_o])
        pred = a0 + b0 * (1 - c[md][idx_d])
        return np.mean(f[md][idx_d]) / np.mean(pred)

    r = st(np.arange(mo.sum()), np.arange(md.sum()))
    bo, bd = d.block[mo], d.block[md]
    io = [np.where(bo == u)[0] for u in np.unique(bo)]
    idd = [np.where(bd == u)[0] for u in np.unique(bd)]
    bs = np.empty(nboot)
    for k in range(nboot):
        so = np.concatenate([io[j] for j in rng.integers(0, len(io), len(io))])
        sd = np.concatenate([idd[j] for j in rng.integers(0, len(idd), len(idd))])
        bs[k] = st(so, sd)
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    return {"obs_over_pred": r, "lo": lo, "hi": hi, "n_dpann_tips": int(md.sum())}


def verdict_b(b):
    if b["ratio"] < KILL_R and b["lo"] <= 1.0:
        return "kill"
    if b["ratio"] >= SUP_R and b["lo"] > SUP_LO:
        return "support"
    return "inconclusive"


def verdict_plan(a, b):
    """The plan's rule as written: kill needs arm A slope > 0 (interval excludes 0) and B < 1.15 with 1 inside
    its interval; support needs B >= 1.3 with lower > 1.15 AND arm A slope not different from 0."""
    a_pos = a["lo"] > 0
    a_zero = a["lo"] <= 0 <= a["hi"]
    if a_pos and b["ratio"] < KILL_R and b["lo"] <= 1 <= b["hi"]:
        return "kill"
    if b["ratio"] >= SUP_R and b["lo"] > SUP_LO and a_zero:
        return "support"
    return "inconclusive"


def adjusted(f, s):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.clip((f - s) / (1 - s), 0, None)


# ---------------------------------------------------------------- gate
def gate():
    out = {"mode": "gate"}
    d = Data("E")
    t = d.tree
    out["inputs_sha256"] = {k: sha256(path(k)) for k in F}
    # tips and completeness
    tipnames = [t.name[v] for v in np.where(t.is_tip)[0]]
    out["n_nodes"], out["n_tips"] = int(t.n), int(t.is_tip.sum())
    out["sd1_focal_rows"] = len(d.sd1)
    out["tips_found_in_sd1_focal"] = int(sum(nm in d.sd1 for nm in tipnames))
    out["tips_with_checkm2"] = int((~np.isnan(d.c2[t.is_tip])).sum())
    # label agreement
    head, ev = read_events(path("ev_E"))
    out["event_header"] = head
    out["event_rows"] = len(ev)
    out["labels_event_eq_tree"] = set(ev) == set(t.name)
    out["starting_tree_same_topology_E"] = bool(d.same_topology)
    # rate classes
    out["distinct_DTL_triplets_E"] = d.nclass
    out["params_3x_triplets"] = 3 * d.nclass
    out["published_parameters"] = 72
    out["distinct_origination_values_E"] = d.norig
    names_by_class = {}
    for v in range(t.n):
        names_by_class.setdefault(int(d.cls[v]), []).append(v)
    named = [v for v in range(t.n) if not t.is_tip[v] and not t.name[v].startswith("Node_")]
    cls_desc = []
    for k, vs in sorted(names_by_class.items()):
        vs = np.array(vs)
        cls_desc.append({"class": k, "branches": int(len(vs)), "tips": int(t.is_tip[vs].sum()),
                         "dpann_branches": int(d.dpann[vs].sum()),
                         "named_nodes": [t.name[v] for v in vs if v in named]})
    out["rate_classes_E"] = cls_desc
    # BIC table
    rows = [l.rstrip("\n").split("\t") for l in open(path("sd10"), encoding="utf-8")]
    hi = next(i for i, r in enumerate(rows) if r and r[0] == "Root abbreviation")
    head10 = rows[hi]
    models = head10[3:12]
    kpar = {"global": 3, "DPANN_L": 4, "DPANN_DL": 5, "DPANN_TL": 5, "DPANN_DTL": 6, "DTL_br1": 21,
            "DTL_br1_O": 25, "DTL_br2": 72, "DTL_br3": 81}
    # columns 3-11: lnL of the 9 models; 12: lnL family wise; 13-21: BIC of the 9 models; 22: BIC family wise
    bic_cols = list(range(13, 22))
    maxdiff, ncell = 0.0, 0
    for r in rows[hi + 1: hi + 16]:
        for j, mname in enumerate(models):
            lnl = float(r[3 + j])
            bic = float(r[bic_cols[j]])
            calc = -2 * lnl + kpar[mname] * math.log(NFAM_LIKE)
            maxdiff = max(maxdiff, abs(calc - bic))
            ncell += 1
        if r[0] == "Cluster2root":
            out["BIC_DPANN_L_Cluster2root_recomputed"] = round(-2 * float(r[4]) + 4 * math.log(NFAM_LIKE), 1)
        if r[0] == "Euryroot":
            out["BIC_DTL_br3_Euryroot_recomputed"] = round(-2 * float(r[11]) + 81 * math.log(NFAM_LIKE), 2)
    out["BIC_models"] = models
    out["BIC_cells_checked"] = ncell
    out["BIC_max_abs_diff"] = maxdiff
    out["BIC_published_text"] = {"DPANN_L": 3284636.6, "DTL_br3_81par": 3264897.57}
    # parameter counts in SD33
    out["sd33_parameter_counts"] = {r.split("\t")[0]: r.split("\t")[2] for r in
                                    open(path("sd33"), encoding="utf-8").read().splitlines()[2:11]}
    # Fig. 2 group sizes (nodes and tips per group)
    fig2 = {"MHH": 41, "Halobacteriota": 81, "Thermoplasmatota": 67, "Korarchaeota": 5, "TAC": 121,
            "Asgard": 39, "Cluster1": 35, "Undinarchaeota": 3, "Cluster2": 113}
    out["fig2_group_nodes"] = {g: {"published": n, "tree": len(t.subtree(t.idx[g]))} for g, n in fig2.items()}
    # DPANN clade
    dp = t.idx["DPANN"]
    dtips = [t.name[v] for v in t.subtree(dp) if t.is_tip[v]]
    out["dpann_tips"] = len(dtips)
    out["dpann_internal_nonroot_branches"] = int((d.internal & d.dpann).sum())
    out["other_internal_nonroot_branches"] = int((d.internal & ~d.dpann).sum())
    ph = {}
    for nm in dtips:
        p = d.sd1[nm]["phylum"]
        ph[p] = ph.get(p, 0) + 1
    out["dpann_tip_phyla_gtdb202"] = ph
    oph = {}
    for nm in tipnames:
        if nm not in dtips:
            p = d.sd1[nm]["phylum"]
            oph[p] = oph.get(p, 0) + 1
    out["other_tip_phyla_gtdb202"] = oph
    # completeness (allowed: distributions, not joined to losses)
    for lab, msk in (("dpann", d.tips & d.dpann), ("other", d.tips & ~d.dpann)):
        c2, c1 = d.c2[msk], d.c1[msk]
        out["checkm2_" + lab] = {"n": int(msk.sum()), "median": float(np.median(c2) * 100),
                                 "below_90": int((c2 < 0.9).sum()), "below_80": int((c2 < 0.8).sum()),
                                 "below_70": int((c2 < 0.7).sum()), "min": float(c2.min() * 100)}
        out["checkm1_" + lab] = {"median": float(np.median(c1) * 100), "below_90": int((c1 < 0.9).sum())}
    sf = d.s_floor
    out["plan_null_spurious_internal_floor"] = {
        "dpann_mean": float(sf[d.internal & d.dpann].mean()), "dpann_max": float(sf[d.internal & d.dpann].max()),
        "other_mean": float(sf[d.internal & ~d.dpann].mean()), "other_max": float(sf[d.internal & ~d.dpann].max())}
    out["internal_depth_bins"] = {
        "edges_tips": DEPTH_BINS[:-1],
        "dpann": np.bincount(d.dbin[d.internal & d.dpann], minlength=len(DEPTH_BINS)).tolist(),
        "other": np.bincount(d.dbin[d.internal & ~d.dpann], minlength=len(DEPTH_BINS)).tolist()}
    # SD20 equals the deposit (both roots); and published per-branch numbers (match flags only)
    rows20 = [l.rstrip("\n").split("\t") for l in open(path("sd20"), encoding="utf-8")]
    h20 = [x.strip() for x in rows20[3]]
    flags = {}
    for root, key in (("E", "Eury"), ("M", "MHH")):
        _, evr = read_events(path("ev_" + root))
        sub = [r for r in rows20[4:] if len(r) >= len(h20) - 1 and key.lower() in r[h20.index("Root")].lower()]
        same = len(sub) == len(evr)
        for r in sub:
            e = evr.get(r[0])
            if e is None:
                same = False
                continue
            for col in ("duplications", "losses", "transfers", "copies"):
                if abs(float(r[h20.index(col)]) - e[col]) > 0.006:
                    same = False
        flags["sd20_equals_deposit_" + root] = same
        flags["sd20_rows_" + root] = len(sub)
        tr = Tree(open(path("tr_" + root), encoding="utf-8").read())
        nr = [nm for nm in tr.name if nm in evr and tr.parent[tr.idx[nm]] >= 0]
        pub = {"E": (639.82, 490.19, 507, 177), "M": (592.64, 588.91, 501, 154)}[root]
        flags["LDCA_losses_match_" + root] = abs(evr["DPANN"]["losses"] - pub[0]) < 0.006
        flags["UnCl2_losses_match_" + root] = abs(evr["UnCl2"]["losses"] - pub[1]) < 0.006
        # "gene transfer ... outnumbers duplication events across nearly all (507/501 out of 513 branches ...),
        # and loss events on many branches (177/154 out of 513 branches)". Which transfer column the authors
        # used is not stated; both are tested. Whole-tree branch counts, not joined to clade or completeness.
        for tcol in ("transfers", "receiving_transfers"):
            tg = sum(evr[nm][tcol] > evr[nm]["duplications"] for nm in evr)
            tl = sum(evr[nm][tcol] > evr[nm]["losses"] for nm in evr)
            flags["%s_gt_dups_branches_%s" % (tcol, root)] = {"count": tg, "published": pub[2]}
            flags["%s_gt_losses_branches_%s" % (tcol, root)] = {"count": tl, "published": pub[3]}
    out["published_value_flags"] = flags
    dM = Data("M")
    out["MHH_root"] = {"distinct_DTL_triplets": dM.nclass, "starting_tree_same_topology": bool(dM.same_topology),
                       "dpann_tips": int((dM.tips & dM.dpann).sum()),
                       "dpann_internal_nonroot": int((dM.internal & dM.dpann).sum())}
    out["not_reproducible"] = ("The DPANN_L loss rates (0.40-0.45 vs 0.26-0.27) are parameters of the 4-parameter "
                               "model; the deposit holds parameters and event counts only for the 72-parameter "
                               "model used for ancestral reconstruction.")
    dump("t9_gate.json", out)
    # structure file (no loss counts)
    with open(os.path.join(D, "data", "t9_structure.tsv"), "w", encoding="utf-8") as fh:
        fh.write("label\tparent\tis_tip\tn_tips\tdpann\trate_class\tdepth_bin\tsub_length\tcheckm2\tcheckm1\n")
        for v in range(t.n):
            fh.write("%s\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s\t%s\n" % (
                t.name[v], t.name[t.parent[v]] if t.parent[v] >= 0 else "", t.is_tip[v], t.ntips[v], d.dpann[v],
                d.cls[v], d.dbin[v], "%.6f" % d.sublen[v] if not np.isnan(d.sublen[v]) else "",
                "%.4f" % d.c2[v] if not np.isnan(d.c2[v]) else "", "%.4f" % d.c1[v] if not np.isnan(d.c1[v]) else ""))


# ---------------------------------------------------------------- planted
class Sim:
    """Gene presence/absence on the real tree, observed through the real CheckM2 completeness, counted by
    Dollo parsimony. Families with fewer than 4 observed copies are dropped, as in Huang's pipeline."""

    def __init__(self, d):
        self.d = d
        t = d.tree
        self.pre = t.pre
        self.par = t.parent
        self.ch = t.children
        self.post = t.post

    def run(self, rng, p, c_true, n0=1200, gain_scale=1.0):
        t, d = self.d.tree, self.d
        n = t.n
        gains = rng.poisson(gain_scale * p.mean() * n0, n)
        gains[0] = n0
        F = int(gains.sum())
        origin = np.repeat(np.arange(n), gains)
        pres = np.zeros((n, F), bool)
        for v in self.pre:
            if v == 0:
                pres[0] = origin == 0
                continue
            u = self.par[v]
            pres[v] = (pres[u] & (rng.random(F, dtype=np.float32) >= p[v])) | (origin == v)
        obs = np.zeros((n, F), bool)
        tipm = t.is_tip
        for v in np.where(tipm)[0]:
            obs[v] = pres[v] & (rng.random(F, dtype=np.float32) < c_true[v])
        cnt = np.zeros((n, F), np.int32)
        for v in self.post:
            if tipm[v]:
                cnt[v] = obs[v]
            else:
                cnt[v] = sum(cnt[c] for c in self.ch[v])
        tot = cnt[0]
        keep = tot >= 4
        cnt, tot = cnt[:, keep], tot[keep]
        full = cnt == tot[None, :]
        above = np.zeros_like(full)
        for v in range(n):
            if not tipm[v]:
                above[v] = full[v] & np.logical_or.reduce([full[c] for c in self.ch[v]])
        present = (cnt > 0) & ~above
        L = np.zeros(n)
        C = present.sum(1).astype(float)
        for v in range(1, n):
            L[v] = (present[self.par[v]] & ~present[v]).sum()
        return L, C


def planted():
    d = Data("E")
    t = d.tree
    sim = Sim(d)
    rng = np.random.default_rng([SEED, 2])
    ncls = int(d.cls.max()) + 1
    c2 = np.where(np.isnan(d.c2), 1.0, d.c2)
    c1 = np.where(np.isnan(d.c1), 1.0, d.c1)

    def make_p(p0, sb, se, k_int=1.0, k_tip=1.0):
        mc = np.exp(sb * rng.standard_normal(ncls) - sb * sb / 2)
        mb = np.exp(se * rng.standard_normal(t.n) - se * se / 2)
        p = p0 * mc[d.cls] * mb
        p[d.dpann & d.internal] *= k_int
        p[d.dpann & d.tips] *= k_tip
        return np.clip(p, 0, 0.9)

    NN, NA = 150, 80
    scen = [
        # name, p0, sigma_block, sigma_branch, k_internal, k_tip, true completeness, reps
        ("null p0=0.03", 0.03, 0.3, 0.4, 1, 1, None, NN),
        ("null p0=0.06", 0.06, 0.3, 0.4, 1, 1, None, NN),
        ("null p0=0.12", 0.12, 0.3, 0.4, 1, 1, None, NN),
        ("null p0=0.06 sd_block=0.6", 0.06, 0.6, 0.4, 1, 1, None, NN),
        ("null, CheckM2 10 pts too high in DPANN", 0.06, 0.3, 0.4, 1, 1, "dpann10", NN),
        ("null, true completeness = CheckM1", 0.06, 0.3, 0.4, 1, 1, "checkm1", NN),
        ("null, CheckM2 noisy (true = est - |N(0,5)| pts)", 0.06, 0.3, 0.4, 1, 1, "noisy5", NN),
        ("null, DPANN tips biologically x2 (tips only)", 0.06, 0.3, 0.4, 1, 2.0, None, NN),
        ("DPANN x1.3", 0.06, 0.3, 0.4, 1.3, 1.3, None, NA),
        ("DPANN x1.6", 0.06, 0.3, 0.4, 1.6, 1.6, None, NA),
        ("DPANN x2.0", 0.06, 0.3, 0.4, 2.0, 2.0, None, NA),
        ("DPANN x1.6 p0=0.03", 0.03, 0.3, 0.4, 1.6, 1.6, None, NA),
        ("DPANN x1.6 p0=0.12", 0.12, 0.3, 0.4, 1.6, 1.6, None, NA),
        ("DPANN x1.6 sd_block=0.6", 0.06, 0.6, 0.4, 1.6, 1.6, None, NA),
        ("DPANN x1.6 internal only", 0.06, 0.3, 0.4, 1.6, 1.0, None, NA),
        ("DPANN x1.6, CheckM2 10 pts too high in DPANN", 0.06, 0.3, 0.4, 1.6, 1.6, "dpann10", NA),
        ("DPANN x1.6, true completeness = CheckM1", 0.06, 0.3, 0.4, 1.6, 1.6, "checkm1", NA),
    ]
    variants = {"all_internal(plan)": 2, "ntips>=3": 3, "ntips>=5": 5}
    rows = []
    for name, p0, sb, se, ki, kt, dist, reps in scen:
        rec = {"A": [], "A_pos": [], "C": [], "plan": [], "fint": []}
        for vn in variants:
            rec[vn] = {"ratio": [], "lo": [], "verdict": []}
        for r in range(reps):
            p = make_p(p0, sb, se, ki, kt)
            ct = c2.copy()
            if dist == "dpann10":
                ct[d.dpann & d.tips] = np.clip(ct[d.dpann & d.tips] - 0.10, 0.05, 1)
            elif dist == "checkm1":
                ct = c1.copy()
            elif dist == "noisy5":
                ct[d.tips] = np.clip(ct[d.tips] - np.abs(0.05 * rng.standard_normal(int(d.tips.sum()))), 0.05, 1)
            L, C = sim.run(rng, p, ct)
            f = frac(L, C)
            bb = {}
            for vn, mt in variants.items():
                b = arm_b(d, f, mask_extra=t.ntips >= mt, rng=rng, nboot=NBOOT_PLANT)
                bb[vn] = b
                rec[vn]["ratio"].append(b["ratio"]); rec[vn]["lo"].append(b["lo"])
                rec[vn]["verdict"].append(verdict_b(b))
            a = arm_a(d, f, c2, rng, nboot=300)
            cc = arm_c(d, f, c2, rng, nboot=200)
            rec["A"].append(a["slope"]); rec["A_pos"].append(a["lo"] > 0)
            rec["C"].append(cc["obs_over_pred"])
            rec["plan"].append(verdict_plan(a, bb["all_internal(plan)"]))
            rec["fint"].append(np.nanmean(f[d.internal]))

        def share(lst):
            return {v: float(np.mean([x == v for x in lst])) for v in ("kill", "inconclusive", "support")}
        row = {"scenario": name, "reps": reps, "p0": p0, "sd_block": sb, "k_internal": ki, "k_tip": kt,
               "true_completeness": dist or "CheckM2 as estimated",
               "mean_f_internal": float(np.mean(rec["fint"])),
               "A_slope_mean": float(np.mean(rec["A"])), "P_A_slope_interval_above_0": float(np.mean(rec["A_pos"])),
               "C_obs_over_pred_mean": float(np.mean(rec["C"])), "plan_rule": share(rec["plan"])}
        for vn in variants:
            row[vn] = {"ratio_mean": float(np.mean(rec[vn]["ratio"])),
                       "ratio_q05_50_95": np.percentile(rec[vn]["ratio"], [5, 50, 95]).tolist(),
                       "lower_mean": float(np.mean(rec[vn]["lo"])), "verdict": share(rec[vn]["verdict"])}
        rows.append(row)
        print(json.dumps({"scenario": name, **{vn: [round(row[vn]["ratio_mean"], 3), row[vn]["verdict"]]
                                               for vn in variants}, "plan": row["plan_rule"],
                          "A": round(row["A_slope_mean"], 3)}), flush=True)
    nulls = [r for r in rows if r["scenario"].startswith("null")]
    alts = [r for r in rows if not r["scenario"].startswith("null")]
    summ = {}
    for vn in variants:
        summ[vn] = {"max_false_support_over_nulls": max(r[vn]["verdict"]["support"] for r in nulls),
                    "min_kill_over_nulls": min(r[vn]["verdict"]["kill"] for r in nulls),
                    "max_kill_over_nulls": max(r[vn]["verdict"]["kill"] for r in nulls),
                    "max_support_over_alternatives": max(r[vn]["verdict"]["support"] for r in alts)}
    summ["plan_rule"] = {"max_false_support_over_nulls": max(r["plan_rule"]["support"] for r in nulls),
                         "max_support_over_alternatives": max(r["plan_rule"]["support"] for r in alts)}
    ok = [vn for vn, mt in sorted(variants.items(), key=lambda kv: kv[1])
          if mt >= 3 and summ[vn]["max_false_support_over_nulls"] <= 0.05]
    summ["D5_rule"] = ("primary = the smallest cutoff in (3, 5) whose worst-null false support is <= 0.05; "
                       "the script's MIN_TIPS must equal it")
    summ["D5_chosen"] = ok[0] if ok else None
    summ["script_MIN_TIPS"] = MIN_TIPS
    dump("t9_planted.json", {"mode": "planted", "seed": [SEED, 2], "script_sha256": sha256(os.path.abspath(__file__)),
                             "rows": rows, "summary": summ})


# ---------------------------------------------------------------- real (sealed)
def analyse(d, L, C, c2, c1, rng, nboot=NBOOT):
    f = frac(L, C)
    b = arm_b(d, f, mask_extra=d.tree.ntips >= MIN_TIPS, rng=rng, nboot=nboot)
    a = arm_a(d, f, c2, rng, nboot)
    res = {"primary_arm_B": b, "min_tips": MIN_TIPS, "verdict": verdict_b(b), "arm_A_positive_control": a}
    ex = {}
    ex["arm_C_dpann_tip_excess_over_completeness_prediction"] = arm_c(d, f, c2, rng, nboot)
    b2 = arm_b(d, f, rng=rng, nboot=nboot)
    ex["arm_B_all_internal_plan"] = b2
    ex["plan_rule_verdict"] = verdict_plan(a, b2)
    ex["arm_B_adjusted_for_spurious_floor"] = arm_b(d, adjusted(f, d.s_floor), rng=rng, nboot=nboot)
    ex["arm_B_ntips_ge5"] = arm_b(d, f, mask_extra=d.tree.ntips >= 5, rng=rng, nboot=nboot)
    ex["arm_B_ntips_ge9"] = arm_b(d, f, mask_extra=d.tree.ntips >= 9, rng=rng, nboot=nboot)
    with np.errstate(invalid="ignore", divide="ignore"):
        fl = f / d.sublen
    ex["arm_B_per_substitution_length"] = arm_b(d, fl, rng=rng, nboot=nboot)
    m = d.internal
    ex["arm_B_pooled_sums"] = {
        "ratio": float((L[m & d.dpann].sum() / (L + C)[m & d.dpann].sum()) /
                       (L[m & ~d.dpann].sum() / (L + C)[m & ~d.dpann].sum()))}
    ex["tip_ratio_raw"] = ratio_of_means(f[d.tips & d.dpann], f[d.tips & ~d.dpann])
    ex["arm_A_checkm1"] = arm_a(d, f, c1, rng, nboot)
    ex["arm_C_checkm1"] = arm_c(d, f, c1, rng, nboot)
    # depth-matched permutation null for the arm B ratio
    mi = d.internal & ~np.isnan(f) & (d.tree.ntips >= MIN_TIPS)
    idx = np.where(mi)[0]
    lab = d.dpann[idx]
    bins = d.dbin[idx]
    obs = ratio_of_means(f[idx][lab], f[idx][~lab])
    null = np.empty(NPERM)
    for k in range(NPERM):
        l2 = lab.copy()
        for bb in np.unique(bins):
            w = np.where(bins == bb)[0]
            l2[w] = l2[w][rng.permutation(len(w))]
        null[k] = ratio_of_means(f[idx][l2], f[idx][~l2])
    ex["depth_matched_permutation"] = {"observed": obs, "null_q": np.percentile(null, [2.5, 50, 97.5]).tolist(),
                                       "p_ge_observed": float((null >= obs).mean())}
    # leakage check: DPANN rate classes, internal mean f vs median tip incompleteness
    rows = []
    for k in np.unique(d.cls[d.dpann]):
        mk = d.dpann & (d.cls == k)
        if (mk & d.internal).sum() >= 1 and (mk & d.tips).sum() >= 2:
            rows.append((np.nanmean(f[mk & d.internal]), np.median(1 - c2[mk & d.tips])))
    if len(rows) >= 4:
        x, y = np.array(rows).T
        rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
        ex["dpann_class_internal_f_vs_incompleteness_spearman"] = {"rho": float(np.corrcoef(rx, ry)[0, 1]),
                                                                   "n_classes": len(rows)}
    res["reported_only"] = ex
    return res


def real(dry=False):
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    check_inputs()
    rng = np.random.default_rng([SEED, 4 if dry else 3])
    out = {"mode": "dryrun_shuffled_labels" if dry else "real", "seed": [SEED, 4 if dry else 3], "seal": st}
    for root in ("E", "M"):
        d = Data(root)
        L, C = d.events()
        c2, c1 = d.c2.copy(), d.c1.copy()
        if dry:
            # D11: shuffle the DPANN label within depth bins (tips among tips, internal within ntips bins),
            # and permute completeness over tips, before anything is computed.
            lab = d.dpann.copy()
            for bb in np.unique(d.dbin[d.nonroot]):
                w = np.where(d.nonroot & (d.dbin == bb))[0]
                lab[w] = lab[w][rng.permutation(len(w))]
            d.dpann = lab
            d.block = d.cls * 2 + d.dpann.astype(int)
            tp = np.where(d.tips)[0]
            perm = rng.permutation(len(tp))
            c2[tp], c1[tp] = c2[tp][perm], c1[tp][perm]
            d.s_floor = d.prod_miss(c2)
        out["root_" + {"E": "Euryarchaeota", "M": "MHH"}[root]] = analyse(d, L, C, c2, c1, rng)
    out["verdict"] = out["root_Euryarchaeota"]["verdict"]
    dump("t9_dryrun_shuffled_labels.json" if dry else "t9_real.json", out,
         sub="scripts_out" if dry else "results")


if __name__ == "__main__":
    if MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "real":
        real()
    elif MODE == "dryrun":
        real(dry=True)
    elif MODE == "gate":
        check_inputs()
        os.makedirs(os.path.join(D, "data"), exist_ok=True)
        gate()
    elif MODE == "planted":
        check_inputs()
        planted()
    else:
        sys.exit("unknown mode")
