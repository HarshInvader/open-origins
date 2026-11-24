"""T11 (prereg docs/prereg/t11_ribozyme_epistasis.md): does pairwise epistasis find tertiary contacts in
self-cleaving ribozymes with solved structures, beyond what sequence separation and single-mutant effects predict?
Data: Roberts et al. 2023 (eLife, doi:10.7554/elife.80360), deposit gitlab.com/bsu/biocompute-public/mut_12 at
commit 7be31e58784ab6ffe5f15790ebbda98279af84d2.  Contact labels: data/t11_contacts.json (t11_structures.py).

Usage (one process, one thread, under nice):
  python -I t11_analysis.py <experiments/t11_ribozyme_epistasis dir> gate      # inputs, coverage, depth, noise; no activity joined to labels
  python -I t11_analysis.py <experiments/t11_ribozyme_epistasis dir> planted   # synthetic doubles only
  python -I t11_analysis.py <experiments/t11_ribozyme_epistasis dir> dryrun    # `real` code, labels permuted within separation bins
  python -I t11_analysis.py <experiments/t11_ribozyme_epistasis dir> sealcheck # says whether `real` would run
  python -I t11_analysis.py <experiments/t11_ribozyme_epistasis dir> real      # the sealed test; refuses without a seal

Definitions (prereg D3-D9).
  FC(g)  = (C + 0.5) / (N + 1), C cleaved and N total reads of genotype g, summed over the three replicates
  f(g)   = log10( FC(g) / FC(wt) )
  g      = isotonic (non-decreasing) fit of f(double) on f(a) + f(b), over all doubles with N >= MIN_READS
           (the global nonlinearity, as in study #30)
  z      = (p_obs - p0) / sd, p_obs = FC(wt) 10^f(double), p0 = FC(wt) 10^g(f(a) + f(b)),
           sd^2 = p0(1-p0)/N + (sum_r N_r^2 / N^2) (p0(1-p0))^2 tau^2, tau = replicate noise on the logit scale
           estimated from the singles (noise_tau).  z is the epistasis of one double: how far it beats the
           global-nonlinearity prediction, in units of its own counting plus replicate noise.
  S(i,j) = the largest z over the usable doubles at positions i, j (doubles with N < MIN_READS are not used;
           pairs with < MIN_DOUBLES usable doubles are dropped)
  eps    = f(double) - f(single a) - f(single b) is the plan's statistic; it fails the planted null (see prereg)
           and is reported only, as are its isotonic and mean forms.
  s(i)   = mean f over the three singles at i  (position sensitivity)
  stratum(i,j) = (separation bin, sorted pair of sensitivity quantile bins)
  Delta  = stratified AUC - 0.5: the share of (contact, non-contact) pairs in the same stratum in which the contact
           scores higher (ties count half).  95% interval: bootstrap over nucleotide positions (pair weight m_i*m_j).

Decision (prereg D10-D12).
  base-pair check: a deciding ribozyme passes if its base-pair Delta >= BP_PASS.  Fewer than 3 pass -> "void".
  pooled Delta: contact-weighted mean over the passing ribozymes; its interval combines their bootstraps.
  support: pooled tertiary Delta >= T_SUPPORT, its 5th percentile > 0, and >= 2 passing ribozymes with
           tertiary Delta >= T_SUPPORT.   kill: pooled 95th percentile < T_EXCLUDE.   else "inconclusive".
"""
import sys, os, json, hashlib
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_pickle

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t11_ribozyme_epistasis/scripts/t11_analysis.py"
SEED = 20261125
MIN_READS = 20          # D4: a double needs at least this many reads over the three replicates
MIN_DOUBLES = 5         # D5: a pair needs at least this many usable doubles (of 9)
SEP_BINS = [4, 8, 16, 31, 10 ** 6]   # D6: 4-7, 8-15, 16-30, 31+
NQ = 4                  # D6: sensitivity quantile bins per ribozyme (quartiles of s over mapped positions)
NBOOT = 2000            # real; planted uses NBOOT_PL
NBOOT_PL = 200
NREP = int(sys.argv[3]) if len(sys.argv) > 3 and MODE == "planted" else 200   # planted replicates per scenario
BP_PASS = 0.15          # D10: a ribozyme passes the base-pair check if its base-pair Delta >= this
T_SUPPORT = 0.10        # D11: pooled tertiary Delta needed for support (and per-ribozyme Delta for consistency)
T_EXCLUDE = 0.15        # D11: kill if the pooled one-sided 95% upper bound is below this
DECIDING = ["HDV", "Hammerhead", "Hairpin", "Hatchet", "Twister"]
REPORTED_ONLY = ["CPEB3"]
FILE = {"HDV": "HDV", "Hammerhead": "HHIII", "Hairpin": "Hairpin", "Hatchet": "Hatchet", "Twister": "Twister", "CPEB3": "CPEB3"}
F = {k: "raw/gitlab/files/Data_Counts_JB_%s_Mut12_seqData_JB.p" % v for k, v in FILE.items()}
F["contacts"] = "data/t11_contacts.json"
SHA = {
    "HDV": "a6267b417f6315675290628878156237b9b9d5050e807faca41c3678ba56cc18",
    "Hammerhead": "d85919e5d2438b561549d3a761b4bb36d8528c58520d14ab20de3bb78d16c84b",
    "Hairpin": "6149e2a75eff2e35f2f4b572fcaff87db4ef8a19b12c5a382c9a9370ade92275",
    "Hatchet": "4a89503524e752d8b1909d31b5c9987094a1fe3470e54aae5321fa989b3989f5",
    "Twister": "f2467181555ef5f21d2c8ea9ee175659b4f0d2f09a8e2108d06b1df657d3d52b",
    "CPEB3": "ab44c25662b1a4dffad631e6f3321d6e9cae2009d8b065a4cfdaa37b133fbb32",
    "contacts": "3ed1a94a02a9ac8c1f530add799065fc97fc1c1258cb4c81a4b0f700339e0bda",
}
BASES = "ACGT"
WC = {("G", "C"), ("C", "G"), ("A", "T"), ("T", "A"), ("G", "T"), ("T", "G")}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_inputs():
    want = SHA
    for k, rel in F.items():
        got = sha256(os.path.join(D, rel))
        if got != want[k]:
            sys.exit("input hash mismatch for %s: %s" % (rel, got))
    return want


def seal_status():
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
    with open(os.path.join(D, sub, name), "w") as f:
        json.dump(obj, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("wrote", os.path.join(sub, name))


# ---------------------------------------------------------------- data
class Ribo:
    """Counts, genotype index and pair structure of one ribozyme.  Nothing here joins activity to labels."""

    def __init__(self, name, contacts):
        self.name = name
        o = safe_pickle.load(os.path.join(D, F[name]))
        cl = [o["rz_cleaved%d" % r] for r in (1, 2, 3)]
        un = [o["rz_uncleaved%d" % r] for r in (1, 2, 3)]
        ct = contacts[name]
        self.wt = wt = ct["wt"]
        L = self.L = len(wt)
        self.Cwt = np.array([c.get(wt, 0) for c in cl], float)
        self.Nwt = self.Cwt + np.array([u.get(wt, 0) for u in un], float)
        # singles: index (pos 1..L, base) -> row
        self.s_pos, self.s_base, sc, sn = [], [], [], []
        sid = {}
        for p in range(1, L + 1):
            for b in BASES:
                if b == wt[p - 1]:
                    continue
                g = wt[:p - 1] + b + wt[p:]
                sid[(p, b)] = len(self.s_pos)
                self.s_pos.append(p); self.s_base.append(b)
                sc.append([c.get(g, 0) for c in cl]); sn.append([c.get(g, 0) + u.get(g, 0) for c, u in zip(cl, un)])
        self.sC, self.sN = np.array(sc, float), np.array(sn, float)
        self.s_pos = np.array(self.s_pos)
        # doubles
        di, dj, da, db, dc, dn = [], [], [], [], [], []
        for i in range(1, L + 1):
            for j in range(i + 1, L + 1):
                for a in BASES:
                    if a == wt[i - 1]:
                        continue
                    for b in BASES:
                        if b == wt[j - 1]:
                            continue
                        g = wt[:i - 1] + a + wt[i:j - 1] + b + wt[j:]
                        di.append(i); dj.append(j); da.append(sid[(i, a)]); db.append(sid[(j, b)])
                        dc.append([c.get(g, 0) for c in cl]); dn.append([c.get(g, 0) + u.get(g, 0) for c, u in zip(cl, un)])
        self.di, self.dj = np.array(di), np.array(dj)
        self.da, self.db = np.array(da), np.array(db)
        self.dC, self.dN = np.array(dc, float), np.array(dn, float)
        self.dwc = np.array([(self.s_base[a], self.s_base[b]) in WC for a, b in zip(da, db)])   # new bases can pair
        self.dwithin = np.arange(len(di)) % 9     # doubles are stored pair by pair, nine per pair
        # pairs: mapped, separation >= 4, not helical.  label 2 canonical, 1 tertiary, 0 non-contact
        lab = {}
        for k, v in (("canonical_pairs_sep_ge4", 2), ("tertiary_contacts", 1), ("non_contacts", 0)):
            for a, b in ct[k]:
                lab[(a, b)] = v
        self.pairs = sorted(lab)
        self.label = np.array([lab[p] for p in self.pairs])
        self.pi = np.array([p[0] for p in self.pairs]); self.pj = np.array([p[1] for p in self.pairs])
        self.sep = self.pj - self.pi
        self.mindist = np.array([ct["mindist"]["%d-%d" % p] for p in self.pairs])
        pidx = {p: k for k, p in enumerate(self.pairs)}
        self.dpair = np.array([pidx.get((i, j), -1) for i, j in zip(di, dj)])
        self.mapped = sorted(set(range(1, L + 1)) - set(ct["unmapped"]))
        self.sepbin = np.digitize(self.sep, SEP_BINS) - 1


def fvals(C, N, Cwt, Nwt):
    fc = (C.sum(1) + 0.5) / (N.sum(1) + 1)
    fw = (Cwt.sum() + 0.5) / (Nwt.sum() + 1)
    return np.log10(fc / fw)


def zscores(r, fs, fd, dN, fw, tau, min_reads=MIN_READS):
    """Primary per-double epistasis: z of the observed double against the isotonic global-nonlinearity prediction."""
    x = fs[r.da] + fs[r.db]
    ok = dN.sum(1) >= min_reads
    gx, gy = isotonic_fit(x[ok], fd[ok])
    pred = np.interp(x, gx, gy)
    p0 = np.clip(fw * 10 ** pred, 1e-4, 0.999)
    ph = fw * 10 ** fd
    N = np.maximum(dN.sum(1), 1)
    q = p0 * (1 - p0)
    var = q / N + (dN ** 2).sum(1) / N ** 2 * q ** 2 * tau ** 2
    return (ph - p0) / np.sqrt(var)


def pair_scores(r, fs, fd, dN, min_reads=MIN_READS, stat="max", eps_override=None):
    """S per pair (nan if fewer than MIN_DOUBLES usable doubles) and position sensitivity s."""
    eps = fd - fs[r.da] - fs[r.db] if eps_override is None else eps_override
    use = (dN.sum(1) >= min_reads) & (r.dpair >= 0)
    P = len(r.pairs)
    n = np.zeros(P); np.add.at(n, r.dpair[use], 1)
    if stat == "max":
        S = np.full(P, -np.inf); np.maximum.at(S, r.dpair[use], eps[use])
    else:
        S = np.zeros(P); np.add.at(S, r.dpair[use], eps[use]); S = S / np.maximum(n, 1)
    S[n < MIN_DOUBLES] = np.nan
    s = np.zeros(r.L + 1); cnt = np.zeros(r.L + 1)
    np.add.at(s, r.s_pos, fs); np.add.at(cnt, r.s_pos, 1)
    s = s / np.maximum(cnt, 1)
    return S, s, eps, use


def strata(r, s, nq=NQ):
    """Separation bin x unordered pair of sensitivity quantile bins (quantiles over mapped positions)."""
    qs = np.quantile(s[r.mapped], np.linspace(0, 1, nq + 1)[1:-1])
    qb = np.digitize(s, qs)
    lo, hi = np.minimum(qb[r.pi], qb[r.pj]), np.maximum(qb[r.pi], qb[r.pj])
    return r.sepbin * 100 + lo * 10 + hi


def strat_auc(S, pos_mask, neg_mask, st, W=None):
    """Stratified AUC of S for pos vs neg pairs within strata.  W: (B, P) pair weights or None.
    Returns (auc or array of B aucs, n_pos_used, n_strata_used)."""
    ok = ~np.isnan(S)
    pos_mask, neg_mask = pos_mask & ok, neg_mask & ok
    Wm = np.ones((1, len(S))) if W is None else W
    num = np.zeros(Wm.shape[0]); den = np.zeros(Wm.shape[0])
    npos, nst = 0, 0
    for k in np.unique(st[pos_mask]):
        P = np.where(pos_mask & (st == k))[0]; N = np.where(neg_mask & (st == k))[0]
        if len(N) == 0:
            continue
        npos += len(P); nst += 1
        sn = S[N]; o = np.argsort(sn); sn = sn[o]; wn = Wm[:, N[o]]
        cum = np.concatenate([np.zeros((Wm.shape[0], 1)), np.cumsum(wn, 1)], 1)
        lo = np.searchsorted(sn, S[P], "left"); hi = np.searchsorted(sn, S[P], "right")
        below = cum[:, lo]; eq = cum[:, hi] - cum[:, lo]
        wp = Wm[:, P]
        num += (wp * (below + 0.5 * eq)).sum(1)
        den += wp.sum(1) * wn.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        a = num / den
    return (a[0] if W is None else a), npos, nst


def boot_weights(r, rng, B):
    m = rng.multinomial(len(r.mapped), np.full(len(r.mapped), 1 / len(r.mapped)), size=B)
    full = np.zeros((B, r.L + 1)); full[:, r.mapped] = m
    return full[:, r.pi] * full[:, r.pj]


def delta(S, pos, neg, st, r, rng, B):
    a, npos, nst = strat_auc(S, pos, neg, st)
    ab, _, _ = strat_auc(S, pos, neg, st, boot_weights(r, rng, B))
    fin = ab[~np.isnan(ab)]
    lo, hi = (np.percentile(fin, [2.5, 97.5]) - 0.5) if len(fin) else (np.nan, np.nan)
    return {"delta": float(a - 0.5), "lo": float(lo), "hi": float(hi), "n_pos": int(npos), "n_strata": int(nst),
            "n_neg": int((neg & ~np.isnan(S)).sum()), "_boot": ab - 0.5}


def pooled(ds):
    """Contact-weighted mean of per-ribozyme Deltas; bootstrap draws are independent across ribozymes."""
    w = np.array([d["n_pos"] for d in ds], float)
    est = float((w * [d["delta"] for d in ds]).sum() / w.sum())
    bs = np.array([d["_boot"] for d in ds])
    ok = np.isfinite(bs).all(0)
    pb = (w[:, None] * bs[:, ok]).sum(0) / w.sum()
    p5, p95 = np.percentile(pb, [5, 95]) if ok.any() else (np.nan, np.nan)
    return {"delta": est, "p5": float(p5), "p95": float(p95), "n_contacts": int(w.sum()), "n_boot": int(ok.sum())}


def verdict(per, skip_bp_check=False):
    """per: {name: {"bp": delta dict, "tert": delta dict}} over the deciding ribozymes (D10-D12)."""
    passed = [n for n in DECIDING if skip_bp_check or (np.isfinite(per[n]["bp"]["delta"]) and per[n]["bp"]["delta"] >= BP_PASS)]
    K = len(passed)
    out = {"ribozymes_passing_base_pair_check": passed, "K": K}
    if K < 3:
        out["verdict"] = "void"
        return out
    pt = pooled([per[n]["tert"] for n in passed])
    out["pooled_base_pairs"] = pooled([per[n]["bp"] for n in passed])
    out["pooled_tertiary"] = pt
    n_cons = sum(per[n]["tert"]["delta"] >= T_SUPPORT for n in passed)
    out["n_passing_with_tertiary_delta_ge_%.2f" % T_SUPPORT] = n_cons
    if pt["p5"] > 0 and pt["delta"] >= T_SUPPORT and n_cons >= 2:
        out["verdict"] = "support"
    elif pt["p95"] < T_EXCLUDE:
        out["verdict"] = "kill"
    else:
        out["verdict"] = "inconclusive"
    return out


def verdict_plan(per):
    """The plan's per-ribozyme rule, with C_z as the statistic (reported only; see prereg 'Changes from the plan').
    A ribozyme is null if Delta < 0.05 or its 95% interval reaches 0, strong if Delta >= 0.15 with lo > 0.
    Base-pair check: base-pair class strong.  Kill: null in all but at most one checked ribozyme (4 of 5).
    Support: strong in at least 3."""
    def cls(d):
        if not np.isfinite(d["delta"]) or d["delta"] < 0.05 or not d["lo"] > 0:
            return "null"
        return "strong" if d["delta"] >= 0.15 else "weak"
    seen = [n for n in DECIDING if cls(per[n]["bp"]) == "strong"]
    K = len(seen)
    if K < 3:
        return "void"
    if sum(cls(per[n]["tert"]) == "null" for n in seen) >= K - 1:
        return "kill"
    if sum(cls(per[n]["tert"]) == "strong" for n in seen) >= 3:
        return "support"
    return "inconclusive"


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if not k.startswith("_")}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def analyse(r, fs, fd, dN, fw, tau, rng, B, label=None, extras=False):
    lab = r.label if label is None else label
    z = zscores(r, fs, fd, dN, fw, tau)
    S, s, eps, use = pair_scores(r, fs, fd, dN, eps_override=z)
    st = strata(r, s)
    neg = lab == 0
    res = {"bp": delta(S, lab == 2, neg, st, r, rng, B), "tert": delta(S, lab == 1, neg, st, r, rng, B)}
    if extras:
        ex = {}
        one = np.zeros(len(S), int)
        a, _, _ = strat_auc(S, lab == 1, neg, one); ex["tert_unmatched_auc_minus_0.5"] = float(a - 0.5)
        a, _, _ = strat_auc(S, lab == 2, neg, one); ex["bp_unmatched_auc_minus_0.5"] = float(a - 0.5)
        a, _, _ = strat_auc(S, lab == 1, neg, r.sepbin); ex["tert_sep_only_auc_minus_0.5"] = float(a - 0.5)
        st3 = strata(r, s, nq=3)
        ex["tert_tercile_strata"] = delta(S, lab == 1, neg, st3, r, rng, B)
        Sr, _, _, _ = pair_scores(r, fs, fd, dN)
        ex["tert_raw_eps_max_plan"] = delta(Sr, lab == 1, neg, st, r, rng, B)
        ex["bp_raw_eps_max_plan"] = delta(Sr, lab == 2, neg, st, r, rng, B)
        Sm, _, _, _ = pair_scores(r, fs, fd, dN, stat="mean")
        ex["tert_mean_eps"] = delta(Sm, lab == 1, neg, st, r, rng, B)
        ex["bp_mean_eps"] = delta(Sm, lab == 2, neg, st, r, rng, B)
        Szm, _, _, _ = pair_scores(r, fs, fd, dN, stat="mean", eps_override=z)
        ex["tert_mean_z"] = delta(Szm, lab == 1, neg, st, r, rng, B)
        for mr in (10, 50):
            Sx, sx, _, _ = pair_scores(r, fs, fd, dN, min_reads=mr, eps_override=zscores(r, fs, fd, dN, fw, tau, mr))
            ex["tert_min_reads_%d" % mr] = delta(Sx, lab == 1, neg, strata(r, sx), r, rng, B)
        far = neg & (r.mindist > 8.0)
        ex["tert_vs_noncontacts_over_8A"] = delta(S, lab == 1, far, st, r, rng, B)
        for lo_, hi_ in ((4.0, 6.0), (6.0, 8.0), (8.0, 12.0)):
            band = neg & (r.mindist > lo_) & (r.mindist <= hi_)
            ex["band_%g_%g_vs_over_12A" % (lo_, hi_)] = delta(S, band, neg & (r.mindist > 12.0), st, r, rng, B)
        # isotonic global nonlinearity, as in study #30: eps' = f_double - g(f_a + f_b)
        x = fs[r.da] + fs[r.db]
        ok = dN.sum(1) >= MIN_READS
        g = isotonic_fit(x[ok], fd[ok])
        e2 = fd - np.interp(x, g[0], g[1])
        Si, _, _, _ = pair_scores(r, fs, fd, dN, eps_override=e2)
        ex["tert_isotonic_eps"] = delta(Si, lab == 1, neg, st, r, rng, B)
        ex["bp_isotonic_eps"] = delta(Si, lab == 2, neg, st, r, rng, B)
        res["reported_only"] = ex
        # per-contact detail: rank of each contact within its stratum's non-contacts
        rows = []
        for k in np.where(lab == 1)[0]:
            N = np.where(neg & (st == st[k]) & ~np.isnan(S))[0]
            rows.append({"pair": r.pairs[k], "S": None if np.isnan(S[k]) else float(S[k]),
                         "share_of_matched_noncontacts_below": None if (len(N) == 0 or np.isnan(S[k])) else float(np.mean(S[N] < S[k]) + 0.5 * np.mean(S[N] == S[k])),
                         "n_matched": int(len(N)), "mindist": float(r.mindist[k])})
        res["contacts"] = rows
    return res


def isotonic_fit(x, y):
    o = np.argsort(x); xs, ys = x[o], y[o].astype(float)
    v, w, xl = [], [], []
    for xi, yi in zip(xs, ys):
        v.append(yi); w.append(1.0); xl.append([xi, xi])
        while len(v) > 1 and v[-2] > v[-1]:
            nw = w[-2] + w[-1]; nv = (v[-2] * w[-2] + v[-1] * w[-1]) / nw
            xl[-2][1] = xl[-1][1]; v[-2] = nv; w[-2] = nw; v.pop(); w.pop(); xl.pop()
    gx = np.array([(a + b) / 2 for a, b in xl]); gy = np.array(v)
    return gx, gy


def load_all(names):
    contacts = json.load(open(os.path.join(D, F["contacts"])))
    return {n: Ribo(n, contacts) for n in names}, contacts


# ---------------------------------------------------------------- gate
def gate():
    want = check_inputs()
    R, contacts = load_all(DECIDING + REPORTED_ONLY)
    out = {"inputs_sha256": want, "ribozymes": {}}
    for n, r in R.items():
        ct = contacts[n]
        tot = r.dN.sum(1)
        usable_pairs = {}
        for v, nm in ((2, "canonical"), (1, "tertiary"), (0, "non_contact")):
            m = r.label == v
            cnt = np.zeros(len(r.pairs)); u = (tot >= MIN_READS) & (r.dpair >= 0); np.add.at(cnt, r.dpair[u], 1)
            usable_pairs[nm] = {"pairs": int(m.sum()), "with_>=%d_usable_doubles" % MIN_DOUBLES: int((m & (cnt >= MIN_DOUBLES)).sum())}
        # replicate noise from singles (logit scale, excess over binomial), used by `planted`
        tau = noise_tau(r.sC, r.sN)
        out["ribozymes"][n] = {
            "deciding": n in DECIDING, "pdb": ct["pdb"], "length": r.L, "mapped_positions": len(r.mapped),
            "tertiary_contacts": len(ct["tertiary_contacts"]), "kept_by_gate": bool(ct["kept"]),
            "canonical_pairs_sep_ge4": len(ct["canonical_pairs_sep_ge4"]),
            "singles_observed": int((r.sN.sum(1) > 0).sum()), "singles_expected": 3 * r.L,
            "doubles_observed": int((tot > 0).sum()), "doubles_expected": 9 * r.L * (r.L - 1) // 2,
            "doubles_with_>=%d_reads" % MIN_READS: int((tot >= MIN_READS).sum()),
            "double_reads_median": float(np.median(tot)), "double_reads_p5": float(np.percentile(tot, 5)),
            "single_reads_min": float(r.sN.sum(1).min()), "wt_reads": float(r.Nwt.sum()),
            "wt_fc_by_replicate": (r.Cwt / r.Nwt).round(3).tolist(),
            "replicate_noise_tau_logit": tau, "usable_pairs": usable_pairs,
        }
    out["gate_passed"] = sum(out["ribozymes"][n]["kept_by_gate"] for n in DECIDING) >= 3
    dump("t11_gate.json", out)
    for n, v in out["ribozymes"].items():
        print(n, {k: v[k] for k in ("pdb", "tertiary_contacts", "kept_by_gate", "doubles_observed", "doubles_expected",
                                    "doubles_with_>=%d_reads" % MIN_READS, "double_reads_median", "replicate_noise_tau_logit")})
        print("   usable pairs", v["usable_pairs"])


def noise_tau(sC, sN):
    p = (sC + 0.5) / (sN + 1)
    lg = np.log(p / (1 - p))
    bv = 1 / ((sN + 1) * p * (1 - p))
    ex = lg.var(1, ddof=1) - bv.mean(1)
    return float(np.sqrt(max(np.median(ex), 0)))


# ---------------------------------------------------------------- planted
SCEN = [
    # name, null model, tertiary (pi, rho), base pairs on?
    ("null_mult", "mult", (0, 0), True),
    ("null_floor", "floor", (0, 0), True),
    ("null_floor_hetero", "floor_hetero", (0, 0), True),
    ("null_saturating", "saturating", (0, 0), True),
    ("null_floor_no_bp", "floor", (0, 0), False),
    ("tert_pi0.2_rho0.5", "floor", (0.2, 0.5), True),
    ("tert_pi0.4_rho0.5", "floor", (0.4, 0.5), True),
    ("tert_pi0.6_rho0.5", "floor", (0.6, 0.5), True),
    ("tert_pi0.8_rho0.5", "floor", (0.8, 0.5), True),
    ("tert_pi0.4_rho0.8", "floor", (0.4, 0.8), True),
    ("tert_pi0.8_rho0.8", "floor", (0.8, 0.8), True),
    ("tert_pi0.6_rho0.5_saturating", "saturating", (0.6, 0.5), True),
]


def synth(r, model, tert, bp_on, rng, tau):
    """Synthetic counts with the real read depths.  True single activities are the observed ones."""
    fw = (r.Cwt.sum() + 0.5) / (r.Nwt.sum() + 1)
    fs_true = fvals(r.sC, r.sN, r.Cwt, r.Nwt)
    floor = np.log10(max(((r.sC.sum(1) + 0.5) / (r.sN.sum(1) + 1)).min(), 1e-4) / fw)
    x = fs_true[r.da] + fs_true[r.db]
    if model == "mult":
        t = x.copy()
    elif model in ("floor", "floor_hetero"):
        t = x.copy()
        if model == "floor_hetero":
            u = rng.normal(0, 0.15, r.L + 1)
            t = t + u[r.di] + u[r.dj] + rng.normal(0, 0.15, len(t))
    elif model == "saturating":     # a second hit in a broken molecule costs little
        t = np.maximum(x, np.minimum(fs_true[r.da], fs_true[r.db]) - 0.3)
    t = np.minimum(t, 0.3)
    lab = np.where(r.dpair >= 0, r.label[np.maximum(r.dpair, 0)], -1)
    if bp_on:   # each base pair: with prob 0.8 its pairing-restoring doubles recover 75% of the way to wild type
        on = rng.random(len(r.pairs)) < 0.8
        m = (lab == 2) & r.dwc & on[np.maximum(r.dpair, 0)]
        t[m] = t[m] + 0.75 * (0 - t[m])
    pi, rho = tert
    if pi > 0:  # each visible tertiary contact: one random double of its nine recovers rho of the way to wild type
        vis = rng.random(len(r.pairs)) < pi
        pick = rng.integers(0, 9, len(r.pairs))
        m = (lab == 1) & vis[np.maximum(r.dpair, 0)] & (r.dwithin == pick[np.maximum(r.dpair, 0)])
        t[m] = t[m] + rho * (0 - t[m])
    t = np.maximum(t, floor)
    p_true = np.clip(fw * 10 ** t, 1e-6, 0.999)
    ps_true = np.clip(fw * 10 ** fs_true, 1e-6, 0.999)

    def draw(p, N):
        lg = np.log(p / (1 - p))[:, None] + rng.normal(0, tau, N.shape)
        pr = 1 / (1 + np.exp(-lg))
        return rng.binomial(N.astype(np.int64), pr).astype(float)

    Cs = draw(ps_true, r.sN)
    Cd = draw(p_true, r.dN)
    Cw = rng.binomial(r.Nwt.astype(np.int64), np.clip((r.Cwt / r.Nwt), 1e-6, 0.999)).astype(float)
    fwh = (Cw.sum() + 0.5) / (r.Nwt.sum() + 1)
    return fvals(Cs, r.sN, Cw, r.Nwt), fvals(Cd, r.dN, Cw, r.Nwt), fwh, noise_tau(Cs, r.sN)


def planted():
    check_inputs()
    R, _ = load_all(DECIDING)
    taus = {n: noise_tau(r.sC, r.sN) for n, r in R.items()}
    rng = np.random.default_rng([SEED, 2])
    rows = []
    for name, model, tert, bp_on in SCEN:
        vs, vplan, pooled_t, per_r = [], [], [], {n: {"bp": [], "tert": [], "bpc": [], "raw_tert": [], "raw_bp": []} for n in R}
        for rep in range(NREP):
            per = {}
            for n, r in R.items():
                fs, fd, fwh, tauh = synth(r, model, tert, bp_on, rng, taus[n])
                a = analyse(r, fs, fd, r.dN, fwh, tauh, rng, NBOOT_PL)
                per[n] = {"bp": a["bp"], "tert": a["tert"]}
                per_r[n]["bp"].append(a["bp"]["delta"]); per_r[n]["tert"].append(a["tert"]["delta"])
                per_r[n]["bpc"].append(a["bp"]["delta"] >= BP_PASS)
                # the plan's statistic (raw eps, max over doubles), point estimate only, for the calibration table
                Sr, sr, _, _ = pair_scores(r, fs, fd, r.dN)
                str_ = strata(r, sr)
                per_r[n]["raw_tert"].append(strat_auc(Sr, r.label == 1, r.label == 0, str_)[0] - 0.5)
                per_r[n]["raw_bp"].append(strat_auc(Sr, r.label == 2, r.label == 0, str_)[0] - 0.5)
            v = verdict(per)
            vs.append(v["verdict"]); vplan.append(verdict_plan(per))
            pooled_t.append(v.get("pooled_tertiary", {}).get("delta", np.nan))
        vs, vplan = np.array(vs), np.array(vplan)
        row = {"scenario": name, "null_model": model, "tert_pi_rho": tert, "base_pairs_planted": bp_on,
               "P": {v: float((vs == v).mean()) for v in ("kill", "inconclusive", "support", "void")},
               "P_plan_rule": {v: float((vplan == v).mean()) for v in ("kill", "inconclusive", "support", "void")},
               "pooled_tertiary_delta_mean": float(np.nanmean(pooled_t)) if np.isfinite(pooled_t).any() else None,
               "per_ribozyme": {n: {"tert_delta_mean": float(np.mean(v["tert"])), "tert_delta_sd": float(np.std(v["tert"])),
                                    "bp_delta_mean": float(np.mean(v["bp"])),
                                    "P_pass_bp_check": float(np.mean(v["bpc"])),
                                    "plan_raw_eps_tert_delta_mean": float(np.mean(v["raw_tert"])),
                                    "plan_raw_eps_bp_delta_mean": float(np.mean(v["raw_bp"]))} for n, v in per_r.items()}}
        rows.append(row)
        print(name, row["P"], "plan rule", row["P_plan_rule"], "pooled tert", row["pooled_tertiary_delta_mean"],
              {n: (round(v["tert_delta_mean"], 3), round(v["bp_delta_mean"], 3), v["P_pass_bp_check"]) for n, v in row["per_ribozyme"].items()}, flush=True)
    nulls = [r for r in rows if r["tert_pi_rho"][0] == 0]
    dump("t11_planted.json", {"mode": "planted", "seed": [SEED, 2], "nrep": NREP, "nboot": NBOOT_PL, "tau": taus,
                              "script_sha256": sha256(os.path.abspath(__file__)), "rows": rows,
                              "max_false_support_over_nulls": max(r["P"]["support"] for r in nulls),
                              "support_reachable": any(r["P"]["support"] >= 0.8 for r in rows),
                              "kill_reachable": any(r["P"]["kill"] >= 0.8 for r in rows)})


# ---------------------------------------------------------------- real (sealed)
def real(dry=False):
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    check_inputs()
    rng = np.random.default_rng([SEED, 4 if dry else 3])
    R, _ = load_all(DECIDING + REPORTED_ONLY)
    res, per = {}, {}
    for n, r in R.items():
        fs = fvals(r.sC, r.sN, r.Cwt, r.Nwt)
        fd = fvals(r.dC, r.dN, r.Cwt, r.Nwt)
        fw = (r.Cwt.sum() + 0.5) / (r.Nwt.sum() + 1)
        tau = noise_tau(r.sC, r.sN)
        label = None
        if dry:   # permute all three labels (canonical, tertiary, non-contact) within separation bins
            label = r.label.copy()
            for b in np.unique(r.sepbin):
                k = np.where(r.sepbin == b)[0]
                label[k] = label[k[rng.permutation(len(k))]]
        a = analyse(r, fs, fd, r.dN, fw, tau, rng, NBOOT, label=label, extras=True)
        a["tau"] = tau
        if dry:
            a.pop("contacts")
        res[n] = a
        per[n] = {"bp": a["bp"], "tert": a["tert"]}
        print(n, "base pairs", strip(a["bp"]), "| tertiary", strip(a["tert"]), flush=True)
    v = verdict({n: per[n] for n in DECIDING})
    # the verdict the tertiary rule alone would give if every ribozyme had passed the base-pair check
    v_nogate = verdict({n: per[n] for n in DECIDING}, skip_bp_check=True)
    # reported only: the plan's per-ribozyme rule, with the primary statistic and with the plan's raw-eps statistic
    v_plan_z = verdict_plan({n: per[n] for n in DECIDING})
    v_plan_raw = verdict_plan({n: {"bp": res[n]["reported_only"]["bp_raw_eps_max_plan"],
                                   "tert": res[n]["reported_only"]["tert_raw_eps_max_plan"]} for n in DECIDING})
    print("VERDICT", v, "| ignoring the base-pair check:", v_nogate)
    print("reported only: plan rule with z:", v_plan_z, "| plan rule as written (raw eps):", v_plan_raw)
    dump("t11_dryrun_permuted_labels.json" if dry else "t11_real.json",
         {"mode": "dryrun_permuted_labels" if dry else "real", "seed": [SEED, 4 if dry else 3], "seal": st,
          "verdict": v, "verdict_if_all_passed_base_pair_check": v_nogate,
          "reported_only_verdict_plan_rule_z": v_plan_z, "reported_only_verdict_plan_rule_raw_eps": v_plan_raw,
          "ribozymes": strip(res)},
         sub="scripts_out" if dry else "results")


if __name__ == "__main__":
    if MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "real":
        real()
    elif MODE == "dryrun":
        real(dry=True)
    else:
        {"gate": gate, "planted": planted}[MODE]()
