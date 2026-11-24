"""T6 (prereg docs/prereg/t6_moody_ko_vs_cog.md): does merging split KEGG families into COGs rescue
LUCA families, beyond re-run noise?  Data: Moody et al. 2024, Supplementary Data 1 (KO) and 2 (COG).

Usage (single process; run under nice):
  python -I t6_analysis.py <experiments/t6_moody_ko_cog dir> gate      # published numbers, structure, KO-side counts
  python -I t6_analysis.py <experiments/t6_moody_ko_cog dir> planted   # synthetic COG PP only
  python -I t6_analysis.py <experiments/t6_moody_ko_cog dir> sealcheck # says whether `real` would run
  python -I t6_analysis.py <experiments/t6_moody_ko_cog dir> dryrun    # the `real` code on COG PP permuted over COGs
  python -I t6_analysis.py <experiments/t6_moody_ko_cog dir> real      # the sealed test; refuses without a seal

Units are the 3,088 COGs of Supplementary Data 2.  A COG's member KOs are the KEGG families of
Supplementary Data 1 whose modal COG it is.  x = largest member-KO PP (`constrained_median`); y = COG PP.
  retest group: COGs with one member KO (same sequences, same trimmed alignment, new trees, new reconciliation)
  merge group:  COGs with two or more member KOs
  eligible:     every member KO has a PP and every one is < 0.5
  flip / rescue: eligible and y >= 0.75

Blinding: `gate` never pairs a COG's PP with its KOs' PP, except for one three-level answer to "is y a copy
of x in the retest group" (see `copy_check`).  `planted` never reads the COG PP column.  `dryrun` permutes
the COG PP over COGs before any pairing.
"""
import sys, os, csv, json, hashlib
import numpy as np

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t6_moody_ko_cog/scripts/t6_analysis.py"
SEED = 20261126
NDRAW = 4000            # posterior draws for the ratio interval
NREP = 300              # planted replicates per scenario
LOW, HIGH = 0.5, 0.75   # D3: eligible if every member KO PP < LOW; flip or rescue if COG PP >= HIGH
XB = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]          # D5: bins of x
NSIZE = 3                                    # D5: size thirds (cut points from the eligible merge group)
KILL_RATIO, SUP_RATIO, SUP_SHARE = 2.0, 5.0, 0.05
VOID_COPY = 0.95        # D8: void if this share of the retest group has y == x
PRIMARY = "XS"          # D6: the rule that decides (U = plan as written, X = matched on x, XS = on x and size)

F = {
    "sd1": "../t5_wehbi_moody/raw/moody_springer_esm/41559_2024_2461_MOESM4_ESM.tsv",
    "sd2": "../t5_wehbi_moody/raw/moody_springer_esm/41559_2024_2461_MOESM5_ESM.tsv",
    "sd2_repo": "../luca_calib/raw/moody/Supp_data/Genome_Size_Number_estimates/COG_test/COG_LUCA_PP.csv",
    "sets": "data/cog_ko_sets.tsv",
}
SHA = {
    "sd1": "1a769b73b2945f1ff62c175a581b61ee27049b74fa8177fdcf917cd36233c3c0",
    "sd2": "7e1f361a0b88706cb29d2eb3eb1ae19297f26eeea00e0375eb30d2eebfa7cf5a",
    "sd2_repo": "bd7388d9f553330a27448fac6ccc7ef6ed1c6d4d6c9b9e90abaf8a0bf32221ff",
    "sets": "5234bb37261c5c2e0e7bdb4815281289ccefa6d5befea3f6a2e009ad8aea93b6",
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
            if SELF in line:
                named = True
                if line.split()[:1] == [me]:
                    hashed = True
    return {"script_sha256": me, "line_naming_script": named, "line_with_current_hash": hashed,
            "real_allowed": named and hashed}


def num(s):
    try:
        v = float(s)
    except ValueError:
        return np.nan
    return v


# ---------------------------------------------------------------- loading
class Data:
    """KO side and structure.  No COG PP in here."""

    def __init__(self, ko_col="constrained_median", missing_as_low=False):
        ko = list(csv.DictReader(open(path("sd1"), encoding="utf-8"), delimiter="\t"))
        self.n_ko = len(ko)
        self.ko_pp_all = np.array([num(r[ko_col]) for r in ko])
        self.ko_flag_probable_ws = sum(r["Probable_and_sampling_threshold_met"].strip().lower() in ("true", "1", "1.0", "yes")
                                       for r in ko)
        self.ko_flag_values = sorted(set(r["Probable_and_sampling_threshold_met"] for r in ko))
        mem = {}
        for r, v in zip(ko, self.ko_pp_all):
            mem.setdefault(r["COG"], []).append((r["KEGG_ko"], v, num(r["COG_perc"])))
        self.ko_distinct_cogs = len(mem)
        sd2 = list(csv.DictReader(open(path("sd2"), encoding="utf-8"), delimiter="\t"))
        self.cogs = [r["COG"] for r in sd2]
        self.modal_ok = sum(any(k == r["Modal_KEGG_ko"] for k, _, _ in mem.get(r["COG"], [])) for r in sd2)
        self.all_in_sd1 = all(c in mem for c in self.cogs)
        sets = {}
        for l in open(path("sets"), encoding="utf-8"):
            p = l.rstrip("\n").split("\t")
            if p[0] != "cog":
                sets[p[0]] = p[1:]
        self.sets = [sets[c] for c in self.cogs]
        n = len(self.cogs)
        self.nk = np.array([len(mem[c]) for c in self.cogs])
        self.single = self.nk == 1
        self.size = np.array([int(sets[c][1]) for c in self.cogs])
        self.x = np.full(n, np.nan)          # largest member-KO PP among members that have one
        self.any_missing = np.zeros(n, bool)
        self.cog_perc_min = np.zeros(n)
        self.members = []
        for i, c in enumerate(self.cogs):
            v = np.array([m[1] for m in mem[c]])
            self.members.append(v)
            self.any_missing[i] = np.isnan(v).any()
            if (~np.isnan(v)).any():
                self.x[i] = np.nanmax(v)
            self.cog_perc_min[i] = min(m[2] for m in mem[c])
        if missing_as_low:
            self.elig = np.where(np.isnan(self.x), True, self.x < LOW)
        else:
            self.elig = (~self.any_missing) & (self.x < LOW)
        self.xbin = np.clip(np.digitize(np.where(np.isnan(self.x), 0.0, self.x), XB[1:-1]), 0, len(XB) - 2)
        em = self.elig & ~self.single
        self.size_cuts = [float(q) for q in np.quantile(self.size[em], [i / NSIZE for i in range(1, NSIZE)])]
        self.sbin = np.digitize(self.size, self.size_cuts, right=True)


def cog_pp(d):
    """The COG PP column of Supplementary Data 2, in the order of d.cogs.  The outcome side."""
    m = {r["COG"]: num(r["PP"]) for r in csv.DictReader(open(path("sd2"), encoding="utf-8"), delimiter="\t")}
    return np.array([m[c] for c in d.cogs])


# ---------------------------------------------------------------- statistic
def strata(d, variant):
    if variant == "X":
        return d.xbin, len(XB) - 1
    if variant == "XS":
        return d.xbin * NSIZE + d.sbin, (len(XB) - 1) * NSIZE
    return np.zeros(len(d.cogs), int), 1


def ratio(d, y, variant, rng, single=None, elig=None, high=HIGH, ndraw=NDRAW):
    """Rescue rate over flip rate: posterior median and central 95% interval of the ratio.
    Each rate has a Beta posterior with a half count of prior on each side (Jeffreys).
    U:  rates over all COGs of each group (the plan's wording).
    X, XS: rates among eligible COGs; the retest rate is taken per stratum and weighted by the eligible
           merge group's strata, so both groups have the same spread of x (and of size).  The retest
           side's half count is shared out over the strata, so sparse strata do not inflate it."""
    single = d.single if single is None else single
    elig = d.elig if elig is None else elig
    hit = elig & (y >= high)
    s, m = single, ~single
    Nm, Ns = int(m.sum()), int(s.sum())
    Em, Es = int((elig & m).sum()), int((elig & s).sum())
    r, f = int((hit & m).sum()), int((hit & s).sum())
    out = {"variant": variant, "merge_n": Nm, "retest_n": Ns, "merge_eligible": Em, "retest_eligible": Es,
           "rescued": r, "flipped": f, "rescued_share_of_merge_group": r / Nm if Nm else None}
    if variant == "U":
        R = rng.beta(r + 0.5, Nm - r + 0.5, ndraw)
        Fl = rng.beta(f + 0.5, Ns - f + 0.5, ndraw)
        out.update({"rescue_rate": r / Nm, "flip_rate": f / Ns})
    else:
        st, nst = strata(d, variant)
        em = np.bincount(st[elig & m], minlength=nst).astype(float)
        es = np.bincount(st[elig & s], minlength=nst).astype(float)
        fs = np.bincount(st[hit & s], minlength=nst).astype(float)
        w = em / em.sum() if em.sum() else np.full(nst, 1.0 / nst)
        R = rng.beta(r + 0.5, Em - r + 0.5, ndraw)
        a = 0.5 / nst          # the Jeffreys half count, shared out over the strata (see prereg D7)
        Fl = (rng.beta(fs + a, es - fs + a, (ndraw, nst)) * w).sum(1)
        raw = np.where(es > 0, fs / np.where(es > 0, es, 1), np.nan)
        ok = (es > 0) & (w > 0)
        out.update({"rescue_rate": r / Em if Em else None,
                    "flip_rate_matched": float((w[ok] * raw[ok]).sum() / w[ok].sum()) if ok.any() else None,
                    "flip_rate_unmatched": f / Es if Es else None,
                    "strata_with_merge_weight_and_no_retest": int(((w > 0) & (es == 0)).sum())})
    q = R / Fl
    lo, med, hi = np.percentile(q, [2.5, 50, 97.5])
    out.update({"ratio": float(med), "ratio_lo": float(lo), "ratio_hi": float(hi)})
    return out


def verdict(e, void=False):
    if void:
        return "void"
    if e["ratio_lo"] <= KILL_RATIO:
        return "kill"
    if e["ratio"] >= SUP_RATIO and e["rescued_share_of_merge_group"] >= SUP_SHARE:
        return "support"
    return "partly"


def dump(name, obj, sub="scripts_out"):
    os.makedirs(os.path.join(D, sub), exist_ok=True)
    p = os.path.join(D, sub, name)
    json.dump(obj, open(p, "w"), indent=1, sort_keys=True)
    print(json.dumps(obj, indent=1, sort_keys=True))
    print("wrote", p)


def table(d, sel, st, nst):
    return [int(v) for v in np.bincount(st[sel], minlength=nst)]


# ---------------------------------------------------------------- gate
def copy_check(d):
    """One three-level answer, and nothing else, about the pairing of y with x in the retest group:
    is Supplementary Data 2 a copy of the KO value there?  If it were, the retest group would hold no re-run."""
    y = cog_pp(d)
    ok = d.single & ~np.isnan(d.x) & ~np.isnan(y)
    share = float((np.abs(y[ok] - d.x[ok]) < 1e-9).mean())
    return "under_5_percent" if share < 0.05 else ("over_95_percent" if share > VOID_COPY else "between")


def gate():
    d = Data()
    y_tab = cog_pp(d)                                   # used only against the repo copy of the same column
    rep = {r["COG"]: num(r["PP"]) for r in csv.DictReader(open(path("sd2_repo"), encoding="utf-8"))}
    same_as_repo = (len(rep) == len(d.cogs)
                    and max(abs(rep[c] - v) for c, v in zip(d.cogs, y_tab)) < 1e-9)
    S = d.sets                                          # n_kos, n_cog_seqs, n_union, n_shared, sum_ko, trimmed_same
    jac = np.array([int(s[3]) / (int(s[1]) + int(s[2]) - int(s[3])) for s in S])
    exact = np.array([s[1] == s[2] == s[3] for s in S])
    trimmed_same = sum(s[5] == "1" for s in S)
    pub = {
        "sd1_rows": d.n_ko, "sd1_rows_expected": 9365,
        "kos_probable_and_sampled_flag": d.ko_flag_probable_ws, "published_399": 399,
        "kos_recount_pp_ge_0.75": int((d.ko_pp_all >= 0.75).sum()),
        "sd2_rows": len(d.cogs), "sd2_rows_expected": 3088,
        "sd2_pp_equals_repo_COG_LUCA_PP_csv": bool(same_as_repo),
        "sd2_cogs_all_in_sd1_modal_cog_column": bool(d.all_in_sd1),
        "sd2_modal_ko_is_a_member": d.modal_ok,
        "sd1_distinct_modal_cogs": d.ko_distinct_cogs,
    }
    struct = {
        "retest_group": int(d.single.sum()), "merge_group": int((~d.single).sum()),
        "merge_group_by_n_kos": {str(k): int(((d.nk == k)).sum()) for k in (2, 3, 4)},
        "merge_group_5_or_more_kos": int((d.nk >= 5).sum()), "largest_n_kos": int(d.nk.max()),
        "retest_cog_seq_set_equals_ko_set": int((exact & d.single).sum()),
        "retest_trimmed_alignment_identical": trimmed_same,
        "merge_cog_seq_set_equals_union_of_kos": int((exact & ~d.single).sum()),
        "smallest_jaccard": float(jac.min()),
        "merge_cogs_whose_kos_share_sequences": int(sum(int(s[4]) > int(s[2]) for s, one in zip(S, d.single) if not one)),
    }
    st, nst = strata(d, "XS")
    xs, nx = strata(d, "X")
    em, es = d.elig & ~d.single, d.elig & d.single
    blind = {
        "what": "KO-side PP and structure only; no COG PP enters these counts",
        "kos_without_a_pp": int(np.isnan(d.ko_pp_all).sum()),
        "retest_cogs_whose_ko_has_no_pp": int((d.single & d.any_missing).sum()),
        "merge_cogs_with_a_member_without_pp": int((~d.single & d.any_missing).sum()),
        "retest_eligible": int(es.sum()), "merge_eligible": int(em.sum()),
        "merge_eligible_share_of_merge_group": float(em.sum() / (~d.single).sum()),
        "support_needs_rescued_at_least": int(np.ceil(SUP_SHARE * (~d.single).sum())),
        "x_bins": XB, "retest_eligible_by_x_bin": table(d, es, xs, nx), "merge_eligible_by_x_bin": table(d, em, xs, nx),
        "size_cut_points": d.size_cuts,
        "retest_eligible_by_x_bin_and_size_third": table(d, es, st, nst),
        "merge_eligible_by_x_bin_and_size_third": table(d, em, st, nst),
        "retest_eligible_cog_perc_ge_0.9": int((es & (d.cog_perc_min >= 0.9)).sum()),
        "median_size_eligible": {"retest": float(np.median(d.size[es])), "merge": float(np.median(d.size[em]))},
        "retest_group_y_equals_x": copy_check(d),
    }
    a = np.array(blind["retest_eligible_by_x_bin_and_size_third"])
    b = np.array(blind["merge_eligible_by_x_bin_and_size_third"])
    blind["strata_with_merge_and_no_retest"] = int(((b > 0) & (a == 0)).sum())
    blind["smallest_retest_stratum_where_merge_present"] = int(a[b > 0].min())
    res = {"mode": "gate", "published_and_tables": pub, "structure": struct, "blind_counts": blind}
    res["gate_pass"] = bool(
        d.n_ko == 9365 and d.ko_flag_probable_ws == 399 and len(d.cogs) == 3088 and same_as_repo and d.all_in_sd1
        and d.modal_ok == 3088 and struct["retest_cog_seq_set_equals_ko_set"] == int(d.single.sum())
        and trimmed_same == int(d.single.sum()) and jac.min() >= 0.95)
    res["decision_non_empty"] = bool(
        blind["merge_eligible"] >= 2 * blind["support_needs_rescued_at_least"]
        and blind["strata_with_merge_and_no_retest"] == 0
        and blind["retest_group_y_equals_x"] != "over_95_percent")
    dump("t6_gate.json", res)


# ---------------------------------------------------------------- planted (synthetic COG PP only)
def planted():
    rng = np.random.default_rng([SEED, 2])
    d = Data()
    n = len(d.cogs)
    pool = np.sort(d.ko_pp_all[~np.isnan(d.ko_pp_all)])     # KO PP values only, detached from families
    base_max = np.where(np.isnan(d.x), rng.choice(pool, n), d.x)
    em = d.elig & ~d.single
    srank = np.argsort(np.argsort(d.size)) / (n - 1.0)

    def rerun(base, q):
        """A re-run: with probability q the family gets an unrelated PP from the pool; otherwise its own
        value with a small jitter."""
        y = np.clip(base + rng.normal(0, 0.03, n), 0, 1)
        jump = rng.random(n) < q
        y[jump] = rng.choice(pool, int(jump.sum()))
        return y

    def scen(kind, q, p):
        if kind == "null":                 # merged COG behaves as a re-run of its best member KO
            return rerun(base_max, q)
        if kind == "rescue":               # as null, plus a share p of the eligible merge group truly rescued
            y = rerun(base_max, q)
            t = em & (rng.random(n) < p)
            y[t] = rng.uniform(HIGH, 1.0, int(t.sum()))
            return y
        if kind == "noise_by_size":        # no rescue; noise grows with family size in both groups alike
            return rerun(base_max, np.clip(q * 2 * srank, 0, 1))
        if kind == "noisier_merge":        # no rescue; the merge group is p times noisier at any size
            return rerun(base_max, np.where(d.single, q, np.clip(q * p, 0, 1)))
        raise ValueError(kind)

    grid = ([("null", q, 0.0) for q in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4)]
            + [("rescue", 0.1, p) for p in (0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5)]
            + [("rescue", 0.02, 0.1), ("rescue", 0.02, 0.3), ("rescue", 0.4, 0.3), ("rescue", 0.4, 0.5)]
            + [("noise_by_size", q, 0.0) for q in (0.1, 0.2, 0.4)]
            + [("noisier_merge", 0.1, 2.0), ("noisier_merge", 0.1, 4.0)])
    rows = []
    VAR = ("U", "X", "XS")
    for kind, q, p in grid:
        row = {"scenario": kind, "q": q, "p": p, "reps": NREP}
        acc = {v: {"ratio": [], "ratio_lo": [], "ratio_hi": [], "rescued": [], "flipped": []} for v in VAR}
        vd = {v: {"kill": 0, "partly": 0, "support": 0} for v in VAR}
        for _ in range(NREP):
            y = scen(kind, q, p)                       # one synthetic table, scored by all three rules
            for v in VAR:
                e = ratio(d, y, v, rng)
                for k in acc[v]:
                    acc[v][k].append(e[k])
                vd[v][verdict(e)] += 1
        for v in VAR:
            row[v] = {"median_ratio": round(float(np.median(acc[v]["ratio"])), 2),
                      "mean_lo": round(float(np.mean(acc[v]["ratio_lo"])), 2),
                      "mean_hi": round(float(np.mean(acc[v]["ratio_hi"])), 2),
                      "mean_rescued": round(float(np.mean(acc[v]["rescued"])), 1),
                      "mean_flipped": round(float(np.mean(acc[v]["flipped"])), 1),
                      "rates": {k: round(c / NREP, 3) for k, c in vd[v].items()}}
        rows.append(row)
        print(json.dumps(row), flush=True)
    res = {"mode": "planted", "seed": [SEED, 2], "ndraw": NDRAW, "primary": PRIMARY,
           "script_sha256": sha256(os.path.abspath(__file__)), "rows": rows,
           "pool_share_ge_0.75": float((pool >= HIGH).mean()),
           "kill_reachable": all(r[PRIMARY]["rates"]["kill"] >= 0.9 for r in rows if r["scenario"] == "null"),
           "support_reachable": any(r[PRIMARY]["rates"]["support"] >= 0.9 for r in rows if r["scenario"] == "rescue")}
    dump("t6_planted.json", res)


# ---------------------------------------------------------------- real (sealed)
def real(dry=False):
    """dry=True runs the same code on COG PP permuted over COGs (a code check; nothing real is estimated)."""
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    check_inputs()
    rng = np.random.default_rng([SEED, 4 if dry else 3])
    d = Data()
    y = cog_pp(d)
    if dry:
        y = y[rng.permutation(len(y))]
    s, m = d.single, ~d.single
    both = ~np.isnan(d.x) & ~np.isnan(y)
    sb = s & both
    copy_share = float((np.abs(y[sb] - d.x[sb]) < 1e-9).mean())
    void = copy_share > VOID_COPY
    main = ratio(d, y, PRIMARY, rng)
    main["verdict"] = verdict(main, void)
    ex = {"retest_group_share_with_y_equal_x": copy_share}
    for v in ("U", "X", "XS"):
        if v != PRIMARY:
            e = ratio(d, y, v, rng)
            e["verdict_if_it_decided"] = verdict(e, void)
            ex["rule_" + v] = e
    # test-retest reliability of a per-family call, retest group
    dx = y[sb] - d.x[sb]
    ex["retest_reliability"] = {
        "n": int(sb.sum()),
        "call_changes_at_0.5": float(((d.x[sb] >= 0.5) != (y[sb] >= 0.5)).mean()),
        "ko_below_0.5_cog_at_or_above": float(((d.x[sb] < 0.5) & (y[sb] >= 0.5)).mean()),
        "ko_at_or_above_0.5_cog_below": float(((d.x[sb] >= 0.5) & (y[sb] < 0.5)).mean()),
        "abs_change_over_0.5": float((np.abs(dx) > 0.5).mean()),
        "abs_change_over_0.25": float((np.abs(dx) > 0.25).mean()),
        "median_abs_change": float(np.median(np.abs(dx))), "mean_change": float(dx.mean()),
        "pearson_r": float(np.corrcoef(d.x[sb], y[sb])[0, 1]),
        "call_changes_at_0.5_cog_perc_ge_0.9": float(((d.x >= 0.5) != (y >= 0.5))[sb & (d.cog_perc_min >= 0.9)].mean()),
    }
    mb = m & both
    ex["merge_group_change"] = {"n": int(mb.sum()), "mean_change_vs_best_member": float((y[mb] - d.x[mb]).mean()),
                                "abs_change_over_0.5": float((np.abs(y[mb] - d.x[mb]) > 0.5).mean())}
    ex["threshold_0.5_to_0.5"] = ratio(d, y, PRIMARY, rng, high=0.5)
    low25 = (~d.any_missing) & (d.x < 0.25)
    ex["threshold_0.25_to_0.75"] = ratio(d, y, PRIMARY, rng, elig=low25)
    ex["retest_group_cog_perc_ge_0.9"] = ratio(d, y, PRIMARY, rng, elig=d.elig & (m | (d.cog_perc_min >= 0.9)))
    # downward mirror: best member KO >= 0.75 and COG < 0.5.  Extra noise in merged families would show here too.
    top = (~np.isnan(d.x)) & (d.x >= HIGH)
    dn = top & (y < LOW)
    ex["downward_mirror"] = {"retest": [int((dn & s).sum()), int((top & s).sum())],
                             "merge": [int((dn & m).sum()), int((top & m).sum())]}
    for col in ("ML_median", "MEAN_OF_MEDIANS"):
        d2 = Data(ko_col=col)
        ex["ko_column_" + col] = ratio(d2, y, PRIMARY, rng)
    d3 = Data(missing_as_low=True)
    ex["member_without_pp_counts_as_low"] = ratio(d3, y, PRIMARY, rng)
    two = s | (d.nk == 2)
    ex["merge_group_two_kos_only"] = ratio(d, y, PRIMARY, rng, elig=d.elig & two)
    ex["merge_group_three_or_more_kos"] = ratio(d, y, PRIMARY, rng, elig=d.elig & (s | (d.nk >= 3)))
    # second null (KO side only): is "every member below 0.5" rarer in real COG groups than in random KO groups?
    vals = np.concatenate([v for v, one in zip(d.members, s) if not one])
    sizes = d.nk[m]
    cut = np.cumsum(sizes)[:-1]
    sh = []
    for _ in range(1000):
        g = np.split(rng.permutation(vals), cut)
        sh.append(np.mean([(not np.isnan(v).any()) and v.max() < LOW for v in g]))
    ex["random_ko_groups"] = {"eligible_share_real": float((d.elig & m).sum() / m.sum()),
                              "eligible_share_random_mean": float(np.mean(sh)),
                              "eligible_share_random_p2.5": float(np.percentile(sh, 2.5)),
                              "eligible_share_random_p97.5": float(np.percentile(sh, 97.5))}
    hit = d.elig & (y >= HIGH)
    lists = {"rescued_cogs": [c for c, h, one in zip(d.cogs, hit, s) if h and not one],
             "flipped_cogs": [c for c, h, one in zip(d.cogs, hit, s) if h and one]}
    if dry:
        lists = {k: len(v) for k, v in lists.items()}       # permuted: the names would mean nothing
    dump("t6_dryrun_permuted_pp.json" if dry else "t6_real.json",
         {"mode": "dryrun_permuted_pp" if dry else "real", "seed": [SEED, 4 if dry else 3], "seal": st,
          "primary": PRIMARY, "main": main, "void": bool(void), "lists": lists, "reported_only": ex},
         sub="scripts_out" if dry else "results")


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
