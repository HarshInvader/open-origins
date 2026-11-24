"""T10 (prereg docs/prereg/t10_luca_age_prior.md, DRAFT): is LUCA's ~4.2 Ga age in Moody et al. 2024
set by the sequences, or by the 4.52 Ga hard maximum and the rate prior?

Usage (single process; run under nice):
  python3 -I t10_analysis.py <experiments/t10_luca_age_prior dir> inputs    # sha256 of inputs and of the MCMCtree binary
  python3 -I t10_analysis.py <dir> planted   # synthetic chains only: checks the convergence code and the verdict logic
  python3 -I t10_analysis.py <dir> twins     # prior-only twins (usedata = 0): the LUCA prior under R0 and P1
  python3 -I t10_analysis.py <dir> dryrun    # the `real` code with every posterior run replaced by its prior twin
  python3 -I t10_analysis.py <dir> sealcheck # says whether `real` would run
  python3 -I t10_analysis.py <dir> real      # gate + kill/support verdict; refuses without a seal

Runs live in <dir>/cache/runs/<variant>_<clock>_ud<usedata>_c<chain>/mcmc.txt, made by make_run.py and
run by MCMCtree 4.10.7.  The LUCA node is t_n248 (driver; t_n368 is its cross-braced mirror).
mcmc.txt holds only post-burn-in samples, so no further burn-in is removed.

Variants: R0 published settings; P1 root and LUCA maximum 4.52 -> 6.0 Ga; P2h rate prior mean halved,
Gamma(2, 5); P2d rate prior mean doubled, Gamma(2, 1.25).  Clocks: GBM (clock = 3), ILN (clock = 2).
Twins: usedata = 0 under clock = 1.  With no data the prior on times does not involve the rates, so the
R0 twin is also the twin of P2h and P2d, and one twin serves both clocks.

Blinding: nothing except `real` reads a posterior (usedata = 2) mcmc.txt.  `twins` and `dryrun` read only
usedata = 0 runs.  `planted` reads nothing.
"""
import sys, os, json, hashlib
import numpy as np

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t10_luca_age_prior/scripts/t10_analysis.py"
SEED = 20261124

LUCA, ROOT = "t_n248", "t_n247"
CLOCKS = ["GBM", "ILN"]
VARIANTS = ["R0", "P1", "P2h", "P2d"]
TWIN_OF = {"R0": "R0", "P1": "P1", "P2h": "R0", "P2d": "R0"}
NCHAIN = 2

# --- decision constants (draft; fixed at the seal) --------------------------------------------------
CLAIM_WINDOW = (4.09, 4.33)   # the claim's interval (Moody 2024 abstract)
EARTH_MAX = 4.52              # the published hard maximum
GATE_TOL = 0.05               # R0 2.5% and 97.5% quantiles within this of the published ones
# Published 95% interval for LUCA, CONCATENATED dataset, cross-bracing A (R0 uses the concatenated in.BV).
# NOT FILLED: the 4.09-4.33 Ga of the abstract is the PARTITIONED dataset.  Fill from Moody 2024
# Supplementary Data 6 (or the repo's sum_files_post/*_all_mean_est.tsv) before the seal.
PUB_CONCAT = {"GBM": None, "ILN": None}
RHAT_MAX = 1.05               # Moody 2024 Methods
ESS_MIN = 100                 # bulk-ESS and tail-ESS, Moody 2024 Methods
ESS_MIN_DECIDE = 200          # pooled bulk-ESS for the LUCA node needed for a verdict (stricter than 100)
CHAIN_MEDIAN_TOL = 0.02       # medians of the two chains must agree within this (Ga)

INPUT_SHA = {
    "raw/01_PAML__00_CODEML__out_CODEML__Hessian__1__in.BV":
        "551789b8986c5ea4f909e0d9d56585a77cdd2289b714fdbd159ca2757a8cf672",
    "raw/00_data_formatting__01_inp_data__LUCAdup_246sp_allcb_calib_MCMCtree.tree":
        "825e294e14bb31a35bfad914f6bc945275e0d9747b64b88fe25f79717a108009",
    "raw/01_PAML__02_MCMCtree__calib_files__Calibnodes.csv":
        "9c42775d23c37db2fe8a2842f5c1bc7a14f1660e25faeccb4c252247b2a92e25",
    "raw/01_PAML__02_MCMCtree__dummy_aln__dummy_aln.aln":
        "281865574bb3d1cc45b94f14509c32cad577c843b5f571fb75b8acc2e083b3ed",
    "cache/paml/paml-4.10.7-src.tar.gz":
        "0f29e768b3797b69eadc6332c3d046d8727702052d56c3b729883626c0a5a4e3",
    "cache/paml/paml-4.10.7/src/mcmctree":
        "15244a2a3e40a804a36c8b85d430e0f1c9de0253632b955434351bdcc07f2ae6",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def check_inputs():
    out = {}
    for rel, want in INPUT_SHA.items():
        got = sha256(os.path.join(D, rel))
        if got != want:
            sys.exit("input hash mismatch for %s: %s" % (rel, got))
        out[rel] = got
    return out


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
    p = os.path.join(D, sub, name)
    json.dump(obj, open(p, "w"), indent=1, sort_keys=True)
    print(json.dumps(obj, indent=1, sort_keys=True))
    print("wrote", p)


# --- reading runs -----------------------------------------------------------------------------------
def run_dir(variant, clock, usedata, chain):
    return os.path.join(D, "cache", "runs", "%s_%s_ud%d_c%d" % (variant, clock, usedata, chain))


def read_column(path, col):
    with open(path) as f:
        head = f.readline().rstrip("\n").split("\t")
        j = head.index(col)
        vals = []
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == len(head):
                vals.append(float(parts[j]))
    return np.asarray(vals)


def chains_for(variant, clock, usedata):
    out = []
    for c in range(1, NCHAIN + 1):
        p = os.path.join(run_dir(variant, clock, usedata, c), "mcmc.txt")
        if not os.path.exists(p):
            sys.exit("missing run: %s" % p)
        out.append(read_column(p, LUCA))
    n = min(len(x) for x in out)
    return np.vstack([x[:n] for x in out])  # chains x draws (equal length)


# --- convergence (rank-normalised split R-hat, bulk- and tail-ESS; Vehtari et al. 2021) --------------
def _autocov(x):
    n = len(x)
    x = x - x.mean()
    f = np.fft.rfft(x, 2 * n)
    ac = np.fft.irfft(f * np.conj(f))[:n] / n
    return ac


def ess(chains):
    m, n = chains.shape
    if n < 4:
        return 0.0
    acov = np.vstack([_autocov(c) for c in chains])
    cmean = chains.mean(axis=1)
    w = acov[:, 0].mean() * n / (n - 1)
    b = n * cmean.var(ddof=1) if m > 1 else 0.0
    var_plus = w * (n - 1) / n + b / n
    if var_plus <= 0:
        return 0.0
    rho = 1 - (w - acov.mean(axis=0)) / var_plus
    rho[0] = 1.0
    # Geyer initial positive and monotone sequence
    t, s, prev = 0, 0.0, np.inf
    while t + 1 < n:
        p = rho[t] + rho[t + 1]
        if p < 0:
            break
        p = min(p, prev)
        s += p
        prev = p
        t += 2
    tau = -1 + 2 * s
    return float(m * n / max(tau, 1e-12))


def _split(chains):
    n = chains.shape[1] // 2
    return np.vstack([chains[:, :n], chains[:, n:2 * n]])


def _ranknorm(chains):
    from statistics import NormalDist
    flat = chains.ravel()
    r = flat.argsort().argsort() + 1.0
    z = np.array([NormalDist().inv_cdf(v) for v in (r - 0.375) / (len(flat) + 0.25)])
    return z.reshape(chains.shape)


def rhat(chains):
    s = _ranknorm(_split(chains))
    m, n = s.shape
    w = s.var(axis=1, ddof=1).mean()
    b = n * s.mean(axis=1).var(ddof=1)
    return float(np.sqrt(((n - 1) / n * w + b / n) / w))


def diagnostics(chains):
    sp = _split(chains)
    q_lo, q_hi = np.quantile(chains, [0.025, 0.975])
    tail = min(ess((sp <= q_lo).astype(float)), ess((sp <= q_hi).astype(float)))
    meds = [float(np.median(c)) for c in chains]
    return {"rhat": rhat(chains), "bulk_ess": ess(_ranknorm(sp)), "tail_ess": tail,
            "chain_medians_spread": float(max(meds) - min(meds)), "n_draws_per_chain": int(chains.shape[1])}


def converged(dg):
    return (dg["rhat"] <= RHAT_MAX and dg["bulk_ess"] >= ESS_MIN_DECIDE and dg["tail_ess"] >= ESS_MIN
            and dg["chain_medians_spread"] <= CHAIN_MEDIAN_TOL)


def summarise(chains):
    flat = chains.ravel()
    lo, med, hi = np.quantile(flat, [0.025, 0.5, 0.975])
    return {"median": float(med), "q025": float(lo), "q975": float(hi), "width": float(hi - lo),
            "share_above_4p52": float((flat > EARTH_MAX).mean())}


# --- verdict ----------------------------------------------------------------------------------------
def verdict(post, prior, pub=None):
    """post[(variant, clock)] and prior[variant] are summaries with diagnostics; pub = PUB_CONCAT."""
    lo_w, hi_w = CLAIM_WINDOW
    notes = []
    if pub is not None:
        for c in CLOCKS:
            r = post[("R0", c)]
            if pub[c] is None:
                return {"verdict": "void", "reason": "published concatenated interval not filled"}
            if abs(r["q025"] - pub[c][0]) > GATE_TOL or abs(r["q975"] - pub[c][1]) > GATE_TOL:
                return {"verdict": "void", "reason": "gate failed for %s" % c}
    for k, s in post.items():
        if not s["converged"]:
            return {"verdict": "undecided", "reason": "not converged: %s %s" % k}
    p1 = {c: post[("P1", c)]["median"] > EARTH_MAX for c in CLOCKS}
    p2 = {c: (post[("P2h", c)]["median"] > hi_w) or (post[("P2d", c)]["median"] < lo_w) for c in CLOCKS}
    kill = all(p1.values()) or all(p2.values())
    support = all(
        post[("P1", c)]["median"] <= EARTH_MAX
        and post[("P1", c)]["q025"] <= hi_w and post[("P1", c)]["q975"] >= lo_w
        and lo_w <= post[("P2h", c)]["median"] <= hi_w
        and lo_w <= post[("P2d", c)]["median"] <= hi_w
        for c in CLOCKS)
    gain = {"%s_%s" % k: 1 - s["width"] / prior[TWIN_OF[k[0]]]["width"] for k, s in post.items()}
    v = "kill" if kill else ("support" if support else "partly")
    return {"verdict": v, "p1_above_4p52": p1, "p2_out_in_direction": p2, "info_gain": gain, "notes": notes}


# --- modes ------------------------------------------------------------------------------------------
def twins():
    check_inputs()
    out = {}
    for v in ["R0", "P1"]:
        ch = chains_for(v, "CLK", 0)
        s = summarise(ch)
        s.update(diagnostics(ch))
        out[v] = s
    dump("t10_twins.json", {"mode": "twins", "luca_prior": out})


def collect(dry):
    prior = {}
    for v in ["R0", "P1"]:
        ch = chains_for(v, "CLK", 0)
        prior[v] = summarise(ch)
    post = {}
    for v in VARIANTS:
        for c in CLOCKS:
            ch = chains_for(TWIN_OF[v], "CLK", 0) if dry else chains_for(v, c, 2)
            s = summarise(ch)
            dg = diagnostics(ch)
            s.update(dg)
            s["converged"] = converged(dg)
            post[(v, c)] = s
    return post, prior


def real(dry=False):
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    ins = check_inputs()
    post, prior = collect(dry)
    v = verdict(post, prior, pub=None if dry else PUB_CONCAT)
    dump("t10_dryrun_twins_as_posterior.json" if dry else "t10_real.json",
         {"mode": "dryrun" if dry else "real", "seal": st, "inputs": ins, "verdict": v,
          "posterior": {"%s_%s" % k: s for k, s in post.items()}, "prior": prior},
         sub="scripts_out" if dry else "results")


def planted():
    """Synthetic AR(1) chains with known medians.  Checks that the diagnostics flag a stuck chain and that
    each verdict is reachable.  Reads no file."""
    rng = np.random.default_rng([SEED, 2])

    def chain(mu, sd=0.06, n=4000, phi=0.9):
        e = rng.normal(0, sd * np.sqrt(1 - phi ** 2), n)
        x = np.empty(n)
        x[0] = mu
        for i in range(1, n):
            x[i] = mu + phi * (x[i - 1] - mu) + e[i]
        return x

    def make(meds, bad=None):
        post = {}
        for (v, c), m in meds.items():
            ch = np.vstack([chain(m), chain(m + (0.15 if bad == (v, c) else 0.0))])
            s = summarise(ch)
            dg = diagnostics(ch)
            s.update(dg)
            s["converged"] = converged(dg)
            post[(v, c)] = s
        return post

    prior = {"R0": {"width": 1.0}, "P1": {"width": 2.0}}
    base = {("R0", c): 4.2 for c in CLOCKS}
    scen = {
        "support": {**base, **{("P1", c): 4.25 for c in CLOCKS}, **{("P2h", c): 4.28 for c in CLOCKS},
                    **{("P2d", c): 4.14 for c in CLOCKS}},
        "kill_by_P1": {**base, **{("P1", c): 4.9 for c in CLOCKS}, **{("P2h", c): 4.3 for c in CLOCKS},
                       **{("P2d", c): 4.12 for c in CLOCKS}},
        "kill_by_P2": {**base, **{("P1", c): 4.4 for c in CLOCKS}, **{("P2h", c): 4.45 for c in CLOCKS},
                       **{("P2d", c): 4.15 for c in CLOCKS}},
        "partly_one_clock": {**base, ("P1", "GBM"): 4.9, ("P1", "ILN"): 4.4,
                             **{("P2h", c): 4.3 for c in CLOCKS}, **{("P2d", c): 4.12 for c in CLOCKS}},
    }
    res = {}
    for name, meds in scen.items():
        res[name] = verdict(make(meds), prior)["verdict"]
    res["stuck_chain"] = verdict(make(scen["support"], bad=("P1", "ILN")), prior)["verdict"]
    expect = {"support": "support", "kill_by_P1": "kill", "kill_by_P2": "kill",
              "partly_one_clock": "partly", "stuck_chain": "undecided"}
    dump("t10_planted.json", {"mode": "planted", "seed": [SEED, 2], "got": res, "expected": expect,
                              "all_as_expected": res == expect})


if __name__ == "__main__":
    if MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "inputs":
        dump("t10_inputs.json", {"mode": "inputs", "sha256": check_inputs()})
    elif MODE == "real":
        real()
    elif MODE == "dryrun":
        real(dry=True)
    else:
        {"planted": planted, "twins": twins}[MODE]()
