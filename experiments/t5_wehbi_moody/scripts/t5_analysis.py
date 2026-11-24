"""T5 (prereg docs/prereg/t5_wehbi_moody_base_rate.md): is Wehbi 2024's "88.6% agreement with Moody"
more than a breadth effect?

Usage (single process; run under nice):
  python -I t5_analysis.py <experiments/t5_wehbi_moody dir> gate      # LUCA / pre-LUCA side only
  python -I t5_analysis.py <experiments/t5_wehbi_moody dir> planted   # permuted PP only
  python -I t5_analysis.py <experiments/t5_wehbi_moody dir> sealcheck # says whether `real` would run
  python -I t5_analysis.py <experiments/t5_wehbi_moody dir> dryrun    # the `real` code on PP permuted over COGs
  python -I t5_analysis.py <experiments/t5_wehbi_moody dir> real      # the sealed test; refuses without a seal

Rule reproduced from Wehbi's deposited files (see the prereg, "Gate"):
  Pfam -> every COG that shares at least one UniProt accession with it in cog2uniprot2pfam.csv
  COG  -> every KEGG family in Moody Supplementary Data 1 whose modal COG it is
  Pfam PP = max `constrained_median` over those families; a Pfam is "present" if it maps to >= 1 COG,
  whether or not any family behind that COG has a PP.  hit = Pfam PP > 0.5.

Blinding: `gate` reads PP only through Pfams labelled LUCA or preLUCA.  `planted` and `dryrun` never join a
real PP to its own COG: the PP vector is first permuted over COGs.
"""
import sys, os, csv, json, hashlib
import numpy as np

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SEED = 20261125
NBOOT = 2000          # clan bootstrap draws
NFLOOR = 2000         # within-size-decile shuffles
NREP = 400            # planted replicates per scenario
PP_CUT = 0.5
OLD, POST = ("LUCA", "preLUCA"), ("LBCA", "LACA")
BINS_S1 = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 8), (9, 16), (17, 10 ** 9)]                    # D4: the decision bins
BINS = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 8), (9, 16), (17, 32), (33, 64), (65, 10 ** 9)]   # finer; reported only
KILL_G, KILL_UP, SUP_G, SUP_LO = 10.0, 20.0, 30.0, 20.0

F = {
    "labels": "raw/wehbi_github_01219d8/Pfam_data_ancestralAAC.csv",
    "classified": "raw/wehbi_github_01219d8/ClassifiedPFAMs.csv",
    "flags": "raw/wehbi_github_01219d8/MoodyPfams_probabilities.csv",
    "edges": "data/cog_pfam_edges.tsv",
    "cogsize": "data/cog_sizes.tsv",
    "moody_sd1": "raw/moody_springer_esm/41559_2024_2461_MOESM4_ESM.tsv",
    "moody_sd2_repo": "../luca_calib/raw/moody/Supp_data/Genome_Size_Number_estimates/COG_test/COG_LUCA_PP.csv",
}
SHA = {
    "labels": "c8ee6d1975bed699c1b6ae4934bed66680a4eae8d3a9cb8146661be64a54a894",
    "classified": "0f186fdc3187593177a8f516f897b7ff7790abb3d0c54fca779364288f54871d",
    "flags": "c3b19db381c659677d5ea6672f4d7f5f7e59fa295d6f0ccba5a792a3d211d609",
    "edges": "406bd1082b78e3a87ba39678a01d4c134dc649fbeb52b5866cb0410d95481ca3",
    "cogsize": "d10553b1fd58c7a5bd0c920b1cb8bf4730cbc9248dc1a01c260eaf6a84239bd7",
    "moody_sd1": "1a769b73b2945f1ff62c175a581b61ee27049b74fa8177fdcf917cd36233c3c0",
    "moody_sd2_repo": "bd7388d9f553330a27448fac6ccc7ef6ed1c6d4d6c9b9e90abaf8a0bf32221ff",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def path(key):
    return os.path.normpath(os.path.join(D, F[key]))


def check_inputs():
    for k in F:
        got = sha256(path(k))
        if got != SHA[k]:
            sys.exit("input hash mismatch for %s: %s" % (F[k], got))


def seal_status():
    """`real` runs only if HASHES.txt has a line naming this script with its current sha256."""
    me = sha256(os.path.abspath(__file__))
    hp = os.path.join(REPO, "docs", "prereg", "HASHES.txt")
    named = hashed = False
    if os.path.exists(hp):
        for line in open(hp, encoding="utf-8"):
            if "experiments/t5_wehbi_moody/scripts/t5_analysis.py" in line:
                named = True
                if line.split()[:1] == [me]:
                    hashed = True
    return {"script_sha256": me, "line_naming_script": named, "line_with_current_hash": hashed,
            "real_allowed": named and hashed}


# ---------------------------------------------------------------- loading
def load():
    lab, clan = {}, {}
    for r in csv.DictReader(open(path("labels"), encoding="utf-8")):
        lab[r["pfamIDs"]] = r["ancestor"]
        clan[r["pfamIDs"]] = r["clans"]
    cogs, size = [], []
    for l in open(path("cogsize"), encoding="utf-8"):
        if l.startswith("cog_id"):
            continue
        c, n, _ = l.rstrip("\n").split("\t")
        cogs.append(c); size.append(int(n))
    cidx = {c: i for i, c in enumerate(cogs)}
    pf_edges = {}
    for l in open(path("edges"), encoding="utf-8"):
        if l[0] == "#" or l.startswith("cog_id"):
            continue
        c, p, n = l.rstrip("\n").split("\t")
        if p == "NA":
            continue
        pf_edges.setdefault(p, []).append((cidx[c], int(n)))
    return lab, clan, cogs, np.array(size), pf_edges


def cog_pp_sd1(cogs, col="constrained_median"):
    """COG PP = max over Moody SD1 families with that modal COG; NaN if none has a value."""
    best = {}
    nfam = {}
    for r in csv.DictReader(open(path("moody_sd1"), encoding="utf-8"), delimiter="\t"):
        try:
            v = float(r[col])
        except ValueError:
            continue
        if v != v:
            continue
        c = r["COG"]
        nfam[c] = nfam.get(c, 0) + 1
        if c not in best or v > best[c]:
            best[c] = v
    return (np.array([best.get(c, np.nan) for c in cogs]),
            np.array([nfam.get(c, 0) for c in cogs]))


def cog_pp_sd2(cogs):
    d = {r["COG"]: float(r["PP"]) for r in csv.DictReader(open(path("moody_sd2_repo"), encoding="utf-8"))}
    return np.array([d.get(c, np.nan) for c in cogs])


class Panel:
    """Pfams of the chosen classes with >= 1 mapped COG, and their COG edges (CSR layout)."""

    def __init__(self, lab, clan, pf_edges, classes, min_n=1):
        ids, old, cl, ptr, col = [], [], [], [0], []
        self.absent = {"old": 0, "post": 0}
        for p in sorted(lab):
            if lab[p] not in classes:
                continue
            side_old = lab[p] in OLD
            e = [c for c, n in pf_edges.get(p, []) if n >= min_n]
            if not e:
                self.absent["old" if side_old else "post"] += 1
                continue
            ids.append(p); old.append(side_old); cl.append(clan[p])
            col.extend(sorted(e)); ptr.append(len(col))
        self.ids = ids
        self.cls = np.array([lab[p] for p in ids])
        self.old = np.array(old, bool)
        self.col = np.array(col, int)
        self.start = np.array(ptr[:-1], int)
        self.k = np.diff(np.array(ptr))
        uc = {c: i for i, c in enumerate(sorted(set(cl)))}
        self.clan = np.array([uc[c] for c in cl], int)
        self.nclan = len(uc)

    def maxpp(self, pp):
        v = np.where(np.isnan(pp), -1.0, pp)[self.col]
        return np.maximum.reduceat(v, self.start)

    def share(self, pp, cut):
        v = (np.where(np.isnan(pp), -1.0, pp)[self.col] > cut).astype(float)
        return np.add.reduceat(v, self.start) / self.k

    def weight_sum(self, w):
        return np.add.reduceat(w[self.col], self.start)


def bin_index(k, bins):
    b = np.full(len(k), -1)
    for i, (lo, hi) in enumerate(bins):
        b[(k >= lo) & (k <= hi)] = i
    assert (b >= 0).all()
    return b


def std_gap(sO, nO, sP, nP):
    """A, B, G in points.  B = post-side rate per bin, weighted by the old side's bin counts
    (the expected value of one-to-one matching with replacement).  Arrays are (..., bins)."""
    A = sO.sum(-1) / nO.sum(-1)
    ok = nP > 0
    rate = np.where(ok, sP / np.where(ok, nP, 1), 0.0)
    w = np.where(ok, nO, 0.0)
    B = (w * rate).sum(-1) / w.sum(-1)
    dropped = ((~ok) & (nO > 0)).any(-1)
    return 100 * A, 100 * B, 100 * (A - B), dropped


def collapse_s1(X):
    """Fine bins -> the decision bins: the last three (17-32, 33-64, 65+) are summed into 17+."""
    return np.concatenate([X[..., :6], X[..., 6:].sum(-1, keepdims=True)], axis=-1)


def clan_weights(nclan, nboot, rng):
    """nboot resamples of nclan clans with replacement, as a (nboot, nclan) matrix of counts."""
    idx = rng.integers(0, nclan, size=(nboot, nclan))
    off = (idx + np.arange(nboot)[:, None] * nclan).ravel()
    return np.bincount(off, minlength=nboot * nclan).reshape(nboot, nclan).astype(float)


def estimate(y, old, b, nb, clan, nclan, rng, nboot=NBOOT, also_s1=False):
    """Point estimate plus percentile 95% interval from a bootstrap over clans (both arms together).
    With also_s1 (b must be the fine bins) the same resamples are re-binned to the decision bins."""
    M = np.zeros((nclan, 4, nb))
    yo, yp = y * old, y * (~old)
    np.add.at(M[:, 0, :], (clan, b), yo)
    np.add.at(M[:, 1, :], (clan, b), old.astype(float))
    np.add.at(M[:, 2, :], (clan, b), yp)
    np.add.at(M[:, 3, :], (clan, b), (~old).astype(float))
    R = None
    if nboot:
        R = (clan_weights(nclan, nboot, rng) @ M.reshape(nclan, -1)).reshape(nboot, 4, nb)

    def summarise(tot, R):
        A, B, G, _ = std_gap(tot[0], tot[1], tot[2], tot[3])
        out = {"A": float(A), "B": float(B), "G": float(G)}
        if R is not None:
            _, _, g, dropped = std_gap(R[:, 0], R[:, 1], R[:, 2], R[:, 3])
            lo, hi = np.percentile(g, [2.5, 97.5])
            out.update({"G_lo": float(lo), "G_hi": float(hi),
                        "boot_draws_with_empty_post_bin": int(dropped.sum())})
        return out

    main = summarise(M.sum(0), R)
    if also_s1:
        return main, summarise(collapse_s1(M.sum(0)), None if R is None else collapse_s1(R))
    return main


def verdict(e):
    if e["G"] < KILL_G and e["G_hi"] < KILL_UP:
        return "kill"
    if e["G"] >= SUP_G and e["G_lo"] > SUP_LO:
        return "support"
    return "partly_informative"


def size_deciles(size, cogs):
    order = np.lexsort((np.array(cogs), size))
    lab = np.empty(len(size), int)
    for d, idx in enumerate(np.array_split(order, 10)):
        lab[idx] = d
    return lab


def shuffle_within(pp, groups, rng):
    out = pp.copy()
    for g in groups:
        out[g] = pp[rng.permutation(g)]
    return out


def breadth_table(P, bins):
    b = bin_index(P.k, bins)
    return [{"bin": "%d" % lo if lo == hi else ("%d+" % lo if hi > 10 ** 8 else "%d-%d" % (lo, hi)),
             "old": int((P.old & (b == i)).sum()), "post": int((~P.old & (b == i)).sum())}
            for i, (lo, hi) in enumerate(bins)]


def dump(name, obj, sub="scripts_out"):
    os.makedirs(os.path.join(D, sub), exist_ok=True)
    p = os.path.join(D, sub, name)
    json.dump(obj, open(p, "w"), indent=1, sort_keys=True)
    print(json.dumps(obj, indent=1, sort_keys=True))
    print("wrote", p)


# ---------------------------------------------------------------- gate (old side only)
def gate():
    rng = np.random.default_rng([SEED, 1])
    lab, clan, cogs, size, pf_edges = load()
    pp, nfam = cog_pp_sd1(cogs)
    P = Panel(lab, clan, pf_edges, OLD)            # no post-LUCA Pfam enters this panel
    m = P.maxpp(pp)
    mine = {p: ((1, 0, 0) if v > 0.75 else (0, 1, 0) if v > 0.5 else (0, 0, 1)) for p, v in zip(P.ids, m)}
    flags = {r["pfam_id"]: (int(r["greater_than_75"]), int(r["50_to_75"]), int(r["less_than_50"]))
             for r in csv.DictReader(open(path("flags"), encoding="utf-8"))}
    match = sum(mine.get(p, (0, 0, 0)) == f for p, f in flags.items())
    theirs_n = sum(1 for f in flags.values() if f[0] or f[1])
    theirs_d = sum(1 for f in flags.values() if sum(f))
    hit = m > PP_CUT
    A = 100 * hit.mean()
    groups = [np.where(size_deciles(size, cogs) == d)[0] for d in range(10)]
    floor = np.array([100 * (P.maxpp(shuffle_within(pp, groups, rng)) > PP_CUT).mean() for _ in range(NFLOOR)])
    allg = [np.arange(len(pp))]
    floor_all = np.array([100 * (P.maxpp(shuffle_within(pp, allg, rng)) > PP_CUT).mean() for _ in range(NFLOOR)])
    # alternatives that were tried and do not reproduce the flags (old side only)
    alt = {}
    for name, v in (("sd1_ML_median", cog_pp_sd1(cogs, "ML_median")[0]),
                    ("sd1_MEAN_OF_MEDIANS", cog_pp_sd1(cogs, "MEAN_OF_MEDIANS")[0]),
                    ("sd2_cog_pp_repo_file", cog_pp_sd2(cogs))):
        Q = P if name != "sd2_cog_pp_repo_file" else None
        if Q is None:   # presence then means: maps to a COG that has an SD2 PP
            keep = ~np.isnan(v)
            pe = {p: [(c, n) for c, n in e if keep[c]] for p, e in pf_edges.items()}
            Q = Panel(lab, clan, pe, OLD)
        mm = Q.maxpp(v)
        mi = {p: ((1, 0, 0) if x > 0.75 else (0, 1, 0) if x > 0.5 else (0, 0, 1)) for p, x in zip(Q.ids, mm)}
        alt[name] = {"A": round(100 * float((mm > PP_CUT).mean()), 2), "n_present": len(Q.ids),
                     "flags_matched": sum(mi.get(p, (0, 0, 0)) == f for p, f in flags.items())}
    Pall = Panel(lab, clan, pf_edges, OLD + POST)   # breadth counts only; no PP is joined to this panel
    res = {
        "mode": "gate", "seed": [SEED, 1],
        "A_percent": round(A, 3), "A_hits": int(hit.sum()), "A_present": len(P.ids),
        "published_percent": 88.6, "from_their_flags": [theirs_n, theirs_d, round(100 * theirs_n / theirs_d, 3)],
        "flags_matched": match, "flags_total": len(flags),
        "by_class": {c: [int(hit[P.cls == c].sum()), int((P.cls == c).sum())] for c in OLD},
        "A_at_0.75": round(100 * float((m > 0.75).mean()), 3),
        "A_mean_share_of_cogs_over_0.5": round(100 * float(P.share(pp, PP_CUT).mean()), 3),
        "old_absent_from_map": P.absent["old"],
        "floor_within_size_decile": {"n": NFLOOR, "mean": round(float(floor.mean()), 3),
                                     "p2.5": round(float(np.percentile(floor, 2.5)), 3),
                                     "p97.5": round(float(np.percentile(floor, 97.5)), 3),
                                     "max": round(float(floor.max()), 3),
                                     "p_floor_ge_A": float((1 + (floor >= A).sum()) / (1 + NFLOOR))},
        "floor_unrestricted_shuffle": {"n": NFLOOR, "mean": round(float(floor_all.mean()), 3),
                                       "p2.5": round(float(np.percentile(floor_all, 2.5)), 3),
                                       "p97.5": round(float(np.percentile(floor_all, 97.5)), 3)},
        "alternatives_rejected": alt,
        "map": {"cogs": len(cogs), "cogs_with_a_pp": int((~np.isnan(pp)).sum())},
        "breadth_counts_fine_bins": breadth_table(Pall, BINS),
        "breadth_counts_s1_bins": breadth_table(Pall, BINS_S1),
        "present": {"old": int(Pall.old.sum()), "post": int((~Pall.old).sum())}, "absent": Pall.absent,
        "clans_among_present": Pall.nclan,
    }
    res["gate_pass"] = bool(abs(A - 88.6) <= 2.0 and match >= 0.95 * len(flags))
    dump("t5_gate.json", res)


# ---------------------------------------------------------------- planted (permuted PP only)
def planted():
    rng = np.random.default_rng([SEED, 2])
    lab, clan, cogs, size, pf_edges = load()
    pp_real, _ = cog_pp_sd1(cogs)
    P = Panel(lab, clan, pf_edges, OLD + POST)
    n = len(P.ids)
    ncog = len(cogs)
    b9 = bin_index(P.k, BINS)
    # COG "old share": share of a COG's ancient Pfam partners that are LUCA or pre-LUCA (labels and map only)
    tot = np.bincount(P.col, minlength=ncog).astype(float)
    oldc = np.bincount(P.col, weights=np.repeat(P.old, P.k).astype(float), minlength=ncog)
    s = np.where(tot > 0, oldc / np.where(tot > 0, tot, 1), P.old.mean())
    sorted_pp = np.sort(np.where(np.isnan(pp_real), -1.0, pp_real))   # values only, detached from COG identity
    kvals = np.unique(P.k)
    strata = [np.where(P.k == k)[0] for k in kvals]

    def pp_planted(w):
        """PP values handed out by rank of  w * rank(old share) + (1 - w) * noise.  w = 0 is a full shuffle."""
        r = np.empty(ncog)
        r[np.lexsort((rng.random(ncog), s))] = np.arange(ncog) / ncog
        u = w * r + (1 - w) * rng.random(ncog)
        out = np.empty(ncog)
        out[np.argsort(u, kind="stable")] = sorted_pp
        return out

    def labels_from_hits(hit, f):
        """Within each exact breadth value, a fraction f of the old labels goes to Pfams that hit;
        the rest are dealt at random.  Class sizes per breadth value stay exactly as in the real data."""
        new = np.zeros(n, bool)
        for idx in strata:
            no = int(P.old[idx].sum())
            if no == 0:
                continue
            idx = rng.permutation(idx)
            m = int(round(f * no))
            h = idx[hit[idx]]
            take = h[:m]
            new[take] = True
            rest = rng.permutation(idx[~new[idx]])   # reshuffle: what is left of idx is no longer in random order
            new[rest[:no - len(take)]] = True
        return new

    scen = ([("pp_side", "w=%.2f" % w, w) for w in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0)]
            + [("label_side", "f=%.2f" % f, f) for f in (0.0, 0.1, 0.2, 0.3, 0.5, 1.0)])
    rows = []
    for kind, name, par in scen:
        acc = {k: [] for k in ("A", "B", "G", "G_lo", "G_hi", "G_finebins")}
        v9 = {"kill": 0, "support": 0, "partly_informative": 0}
        v7 = dict(v9)
        for _ in range(NREP):
            if kind == "pp_side":
                hit = (P.maxpp(pp_planted(par)) > PP_CUT).astype(float)
                old = P.old
            else:
                hit = (P.maxpp(pp_planted(0.0)) > PP_CUT).astype(float)
                old = labels_from_hits(hit > 0, par)
            e9, e7 = estimate(hit, old, b9, len(BINS), P.clan, P.nclan, rng, also_s1=True)
            for k in ("A", "B", "G", "G_lo", "G_hi"):
                acc[k].append(e7[k])
            acc["G_finebins"].append(e9["G"])
            v9[verdict(e9)] += 1
            v7[verdict(e7)] += 1
        row = {"family": kind, "scenario": name, "reps": NREP}
        row.update({"mean_" + k: round(float(np.mean(v)), 2) for k, v in acc.items()})
        row["sd_G"] = round(float(np.std(acc["G"])), 2)
        row["rates"] = {k: v / NREP for k, v in v7.items()}
        row["rates_finebins"] = {k: v / NREP for k, v in v9.items()}
        rows.append(row)
        print(row, flush=True)
    null, top = rows[0], rows[7]
    res = {"mode": "planted", "seed": [SEED, 2], "nboot": NBOOT, "pfams": n, "clans": P.nclan,
           "script_sha256": sha256(os.path.abspath(__file__)), "rows": rows,
           "kill_reachable": null["rates"]["kill"] >= 0.5,
           "support_reachable": top["rates"]["support"] >= 0.5}
    dump("t5_planted.json", res)


# ---------------------------------------------------------------- real (sealed)
def real(dry=False):
    """dry=True runs the same code on PP permuted over COGs (a code check; nothing real is estimated)."""
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming "
                 "experiments/t5_wehbi_moody/scripts/t5_analysis.py with its current sha256 (%s)." % st["script_sha256"])
    check_inputs()
    rng = np.random.default_rng([SEED, 4 if dry else 3])
    lab, clan, cogs, size, pf_edges = load()
    pp, nfam = cog_pp_sd1(cogs)
    v2 = cog_pp_sd2(cogs)
    if dry:
        perm = rng.permutation(len(cogs))
        pp, nfam, v2 = pp[perm], nfam[perm], v2[rng.permutation(len(cogs))]
    P = Panel(lab, clan, pf_edges, OLD + POST)
    bd = bin_index(P.k, BINS_S1)
    nb = len(BINS_S1)
    m = P.maxpp(pp)
    hit = (m > PP_CUT).astype(float)
    main = estimate(hit, P.old, bd, nb, P.clan, P.nclan, rng)
    main["verdict"] = verdict(main)
    per_bin = []
    bf = bin_index(P.k, BINS)
    for i, t in enumerate(breadth_table(P, BINS)):
        o, q = P.old & (bf == i), ~P.old & (bf == i)
        t.update({"old_rate": round(100 * float(hit[o].mean()), 2) if o.any() else None,
                  "post_rate": round(100 * float(hit[q].mean()), 2) if q.any() else None})
        per_bin.append(t)
    ex = {}
    ex["unmatched_post_rate"] = round(100 * float(hit[~P.old].mean()), 3)
    ex["fine_bins"] = estimate(hit, P.old, bf, len(BINS), P.clan, P.nclan, rng)
    ex["pp_over_0.75"] = estimate((m > 0.75).astype(float), P.old, bd, nb, P.clan, P.nclan, rng)
    ex["mean_share_of_cogs_over_0.5"] = estimate(P.share(pp, PP_CUT), P.old, bd, nb, P.clan, P.nclan, rng)
    kf = P.weight_sum(nfam.astype(float)).astype(int)        # PP-bearing Moody families behind the Pfam
    keep = kf > 0
    ex["matched_on_pp_bearing_families"] = estimate(hit[keep], P.old[keep], bin_index(kf[keep], BINS_S1), nb,
                                                    P.clan[keep], P.nclan, rng)
    for name, sel in (("old=LUCA_only", P.cls != "preLUCA"), ("old=preLUCA_only", P.cls != "LUCA"),
                      ("post=LBCA_only", P.cls != "LACA"), ("post=LACA_only", P.cls != "LBCA")):
        ex[name] = estimate(hit[sel], P.old[sel], bd[sel], nb, P.clan[sel], P.nclan, rng)
    P2 = Panel(lab, clan, pf_edges, OLD + POST, min_n=2)
    ex["map_needs_2_proteins"] = estimate((P2.maxpp(pp) > PP_CUT).astype(float), P2.old, bin_index(P2.k, BINS_S1),
                                          nb, P2.clan, P2.nclan, rng)
    keep2 = ~np.isnan(v2)
    P3 = Panel(lab, clan, {p: [(c, n) for c, n in e if keep2[c]] for p, e in pf_edges.items()}, OLD + POST)
    ex["moody_sd2_cog_pp"] = estimate((P3.maxpp(v2) > PP_CUT).astype(float), P3.old, bin_index(P3.k, BINS_S1),
                                      nb, P3.clan, P3.nclan, rng)
    groups = [np.where(size_deciles(size, cogs) == d)[0] for d in range(10)]
    fa, fg = [], []
    for _ in range(NFLOOR):
        h = (P.maxpp(shuffle_within(pp, groups, rng)) > PP_CUT).astype(float)
        e = estimate(h, P.old, bd, nb, P.clan, P.nclan, rng, nboot=0)
        fa.append(e["A"]); fg.append(e["G"])
    fa, fg = np.array(fa), np.array(fg)
    ex["floor_within_size_decile"] = {
        "A_mean": float(fa.mean()), "A_p97.5": float(np.percentile(fa, 97.5)),
        "G_mean": float(fg.mean()), "G_p2.5": float(np.percentile(fg, 2.5)), "G_p97.5": float(np.percentile(fg, 97.5)),
        "p_floor_G_ge_observed": float((1 + (fg >= main["G"]).sum()) / (1 + NFLOOR))}
    dump("t5_dryrun_permuted_pp.json" if dry else "t5_real.json",
         {"mode": "dryrun_permuted_pp" if dry else "real", "seed": [SEED, 4 if dry else 3], "seal": st,
          "main": main, "per_bin": per_bin,
          "present": {"old": int(P.old.sum()), "post": int((~P.old).sum())}, "absent": P.absent,
          "reported_only": ex}, sub="scripts_out" if dry else "results")


if __name__ == "__main__":
    if MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "real":
        real()
    elif MODE == "dryrun":
        real(dry=True)
    else:
        check_inputs()
        {"gate": gate, "planted": planted}[MODE]()
