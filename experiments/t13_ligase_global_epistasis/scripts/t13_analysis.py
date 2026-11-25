"""T13 (prereg docs/prereg/t13_ligase_global_epistasis.md): does the ligase neutral network need
higher-order epistasis, or does an additive latent score through one monotone curve do?

Claim under test: Rotrattanadumrong & Yokobayashi 2022, Nat Commun 13:4847, doi:10.1038/s41467-022-32538-z
(PMC9385714), Results: "In generation 8, almost all neutral mutants identified were expected to be
deleterious under the epistasis-free model.  This indicated that the neural network was able to learn
higher-order, nonlinear mutational effects".  "Epistasis-free" there is the authors' log-additive model on
the measured scale.  An additive latent score passed through one saturating curve carries no specific
interaction either, and predicts exactly the pattern the authors read as higher-order epistasis.

Usage (single process, single thread; run under nice, with OMP/OPENBLAS threads = 1):
  python -I t13_analysis.py <experiments/t13_ligase_global_epistasis dir> gate
  python -I t13_analysis.py <dir> planted [NREP] [SCENARIO_INDICES]   # simulation only
  python -I t13_analysis.py <dir> planted_merge
  python -I t13_analysis.py <dir> sealcheck
  python -I t13_analysis.py <dir> dryrun                              # `real` code, gen 7/8 labels permuted
  python -I t13_analysis.py <dir> real                                # sealed; refuses without the seal

Inputs: members of the authors' Zenodo archive (doi:10.5281/zenodo.6945203), pulled one by one by HTTP
range request with scripts/zip_fetch.py into raw/zenodo/ (gitignored).  Every input's sha256 is checked
here and the run stops on a mismatch.  The sampled_paths*.txt members are Python pickles and are never
read by anything in this study.

Models (D-numbers refer to the prereg):
  G    additive latent score phi = b0 + sum of per-mutation terms, through one monotone curve
       g(phi) = lo + (hi - lo) * sigmoid(phi).  Fitted by least squares on the measured RA of the
       authors' own generation 1-6 training split (D3).  No pair or higher-order term.
  GP   G plus pairwise mutation terms, ridge-fitted on the latent scale (D5).
  NET  a small multilayer perceptron on the one-hot sequence, trained on the same rows and the same
       neutral/deleterious labels as the authors' MLP (D6).  numpy only.
  LA   the authors' own log-additive model on the measured scale, their code's definition (gate).

Blinding: `gate` reads generation 7 and 8 outcomes only through the authors' own published numbers
(Fig. 3b fractions, Fig. 5a fractions).  No model is fitted to generation 7 or 8 outcomes anywhere.
`planted` simulates activities from the real genotypes and the real replicate noise.  `dryrun` permutes
the generation 7 and 8 labels within Hamming-distance bins before anything is scored.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np
from scipy import optimize, stats

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t13_ligase_global_epistasis/scripts/t13_analysis.py"

SEED = 20261125
WT = "TATCACTTGTCGTAAGACACTTTGGATGGGTTGAA"       # Generate_Figure_3.ipynb, cell 5
BASES = "ACGT"
NPOS = 35
RT = 0.2                 # the paper's neutrality threshold on RA
TEST_FRAC = 0.30         # the authors' train_test_split(test_size=0.30, random_state=0)
SPLIT_SEED = 0

# D7 decision rules
KILL_RECALL = 0.80       # kill: G calls at least this share of measured gen-8 neutral variants neutral
KILL_AP_GAP = 0.05       # kill: AP(G) within this of the best learner on the same data
SUP_RECALL = 0.50        # support: G calls fewer than this share of them neutral
SUP_LIFT = 0.10          # support: pair terms or the network lift AP by at least this much

MIN_CO = 100             # D5: a pair term needs this many co-occurrences in the training split
RIDGE = 1.0              # D5: ridge penalty on pair terms (latent scale)
NET_HID = (128, 64, 32)  # D6: the authors' own hidden layer sizes
NET_EPOCHS, NET_BATCH, NET_LR = 100, 1024, 0.005
NET_RESTARTS = 3         # D6: the best of this many seeds (the authors also picked the best of
#                          five model families), so one bad draw cannot hide a learnable interaction

NREP = int(sys.argv[3]) if MODE == "planted" and len(sys.argv) > 3 else 10

RAW = "raw/zenodo/"
GEN16 = ["Filtered_Lib1_R1_R2_QS20.csv", "Filtered_Lib6_R1_R2_QS20.csv", "Filtered_Lib4_R1_R2_QS20.csv",
         "Filtered_Lib3_R1_R2_QS20.csv", "Filtered_Lib2_R1_R2_QS20.csv", "Filtered_Lib5_R1_R2_QS20.csv",
         "Filtered_Lib4B_R1_R2_QS20.csv"]      # the authors' own file order (Machine_Learning_Models.ipynb)
GEN7 = ["Filtered_Lib7_R1_R2_QS20.csv", "Filtered_Lib7_MLP_R1_R2_QS20.csv",
        "Filtered_Lib7_MLP_xtra_R1_R2_QS20.csv"]
GEN8 = ["Filtered_Lib8_R1_R2_QS20.csv"]
WTMUT = "Filtered_LibWT_Mut_R1_R2_QS20_tolerance_1.csv"

SHA = {
    "Filtered_Lib1_R1_R2_QS20.csv": "a29b42c04261e65f38c0aa03eb26e507d44bc3fdc35e0d11003dc2ea683b78fd",
    "Filtered_Lib2_R1_R2_QS20.csv": "8902261dab6e351585046fabc6379910e8ce26c3ee054b2a932af3400fa372b2",
    "Filtered_Lib3_R1_R2_QS20.csv": "cf2c6864ff2344ffee296d89f31e1d309bb4ac7a9286c2b998a79d3f358f881b",
    "Filtered_Lib4_R1_R2_QS20.csv": "becdcb169e4f1a0271772427a3406d5b7f8fbc71822914bf80a12642d1fcf8e2",
    "Filtered_Lib4B_R1_R2_QS20.csv": "cededa1da23a69f781fbefac3e44cb28ace0b59981b41c26a3bef7865d0b06ff",
    "Filtered_Lib5_R1_R2_QS20.csv": "3ef6fe0fa17140df32baa272cd47129cadc1b616756be62d0f8dc37bb9d2aa6e",
    "Filtered_Lib6_R1_R2_QS20.csv": "dcc7d3f20ab2232637eeb11096bc15529e09ace35196ea57943672dc0ec8aeee",
    "Filtered_Lib7_R1_R2_QS20.csv": "abd1604c01108b0fb6c64338d66308ec38aaa07f88642a3d9b2410c292b3ae0d",
    "Filtered_Lib7_MLP_R1_R2_QS20.csv": "15c7b43d324a1d96e5196483893638a4c551682f2c5ed3853c55b24272308206",
    "Filtered_Lib7_MLP_xtra_R1_R2_QS20.csv": "9011f86759474291860f0ed485ebc4cea55001b6c01ebefbcc3eac41812b7b4e",
    "Filtered_Lib8_R1_R2_QS20.csv": "924925f8ec55120cb27fb0fb296b4bd5340275e95553916a31aaff7da3c8001a",
    WTMUT: "09de9febd525d57b06d2122426fe3fc5099a2d4dfae043d24f589ce2003a8ba0",
    "Models_scores.csv": "4180a76550502390b39bb0d3c97b6e3dd9e8f7cee786647b83946fc629b6fb8e",
    "README.txt": "a66ef96f582a81008e3a4ad3181f259a40e7d696adc803ddeb3b74eac263cfec",
}

# published numbers used by the gate (paper text and figures; see the prereg for verbatim quotes)
PUB = {"train": 20920, "test": 8967, "gen8_neutral_frac": 0.28, "gen7a": 0.74, "gen7b": 0.89,
       "wtmut_neutral_frac": 0.60, "gen1_neutral_frac": 0.11, "gen1_LA_predictable": 0.755}


# ---------------------------------------------------------------- small helpers
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def check_inputs(names):
    for n in names:
        p = os.path.join(D, RAW, n)
        got = sha256(p)
        if got != SHA[n]:
            sys.exit("input hash mismatch for %s: %s" % (n, got))


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


def dump(name, obj):
    os.makedirs(os.path.join(D, "scripts_out"), exist_ok=True)
    with open(os.path.join(D, "scripts_out", name), "w") as f:
        json.dump(obj, f, indent=1, default=float)
    print("wrote scripts_out/" + name)


def read_csv(path):
    """Minimal CSV reader for the authors' files.  Returns a dict of numpy arrays."""
    with open(path, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split(",")
        rows = [ln.rstrip("\n").split(",") for ln in f if ln.strip()]
    cols = {}
    for i, name in enumerate(head):
        vals = [r[i] for r in rows]
        if name in ("Sequences", "Algorithm", "Generation"):
            cols[name] = np.array(vals, dtype=object)
        else:
            cols[name] = np.array([float(v) if v not in ("", "NA") else np.nan for v in vals])
    return cols


def load(names):
    parts = [read_csv(os.path.join(D, RAW, n)) for n in names]
    out = {}
    for k in parts[0]:
        out[k] = np.concatenate([p[k] for p in parts])
    return out


# ---------------------------------------------------------------- encoding
MUTS = [(p, b) for p in range(NPOS) for b in BASES if b != WT[p]]      # 105 mutations
MUT_IX = {m: i for i, m in enumerate(MUTS)}


def mut_matrix(seqs):
    """n x 105 binary matrix: 1 if the sequence carries that mutation (relative to the WT)."""
    X = np.zeros((len(seqs), len(MUTS)), dtype=np.float64)
    for r, s in enumerate(seqs):
        for p in range(NPOS):
            if s[p] != WT[p]:
                X[r, MUT_IX[(p, s[p])]] = 1.0
    return X


def onehot(seqs):
    """n x 140 one-hot over ACGT at each of the 35 positions (fixed alphabet)."""
    X = np.zeros((len(seqs), NPOS * 4), dtype=np.float64)
    for r, s in enumerate(seqs):
        for p in range(NPOS):
            j = BASES.find(s[p])
            if j >= 0:
                X[r, p * 4 + j] = 1.0
    return X


def author_split(n):
    """Reproduces sklearn train_test_split(test_size=0.30, random_state=0) index order."""
    perm = np.random.RandomState(SPLIT_SEED).permutation(n)
    n_test = int(math.ceil(TEST_FRAC * n))
    n_train = int(math.floor((1.0 - TEST_FRAC) * n))
    return perm[n_test:n_test + n_train], perm[:n_test]


# ---------------------------------------------------------------- metrics
def average_precision(score, label):
    """Area under the precision-recall curve, the step ('average precision') form."""
    label = np.asarray(label, dtype=bool)
    if label.sum() == 0 or label.sum() == len(label):
        return float("nan")
    o = np.argsort(-np.asarray(score, dtype=float), kind="mergesort")
    lab = label[o]
    tp = np.cumsum(lab)
    prec = tp / np.arange(1, len(lab) + 1)
    return float((prec * lab).sum() / lab.sum())


def spearman(a, b):
    return float(stats.spearmanr(a, b).statistic)


def recall_at(score, label, thr):
    label = np.asarray(label, dtype=bool)
    if label.sum() == 0:
        return float("nan")
    return float((np.asarray(score) >= thr)[label].mean())


def hamming_bins(hd):
    """Bins for the null and the dry run: each Hamming distance is its own bin, small ones merged."""
    hd = np.asarray(hd, dtype=int)
    bins = hd.copy()
    for v in np.unique(hd):
        if (hd == v).sum() < 30:                     # merge thin tails into the nearest big bin
            bins[hd == v] = -1
    return bins


def shuffle_in_bins(values, bins, rng):
    out = np.array(values, copy=True)
    for b in np.unique(bins):
        m = bins == b
        idx = np.flatnonzero(m)
        out[idx] = values[rng.permutation(idx)]
    return out


# ---------------------------------------------------------------- model G
def _sig(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))


def g_curve(phi, lo, hi):
    return lo + (hi - lo) * _sig(phi)


def pack(theta):
    return theta[0], theta[0] + np.exp(theta[1]), theta[2], theta[3:]


def fit_G(X, ra, maxfev=200):
    """Least squares on the measured scale for lo, log(hi-lo), b0 and the 105 mutation terms."""
    n, p = X.shape
    # start: lo at the measured floor, hi above the measured ceiling, additive terms from a
    # ridge fit of the logit of the clipped RA
    lo0 = float(np.percentile(ra, 1))
    hi0 = float(max(np.percentile(ra, 99), lo0 + 1e-3))
    y = np.clip((ra - lo0) / (hi0 - lo0), 1e-3, 1 - 1e-3)
    t = np.log(y / (1 - y))
    A = np.concatenate([np.ones((n, 1)), X], axis=1)
    beta0 = np.linalg.solve(A.T @ A + 1.0 * np.eye(p + 1), A.T @ t)
    th0 = np.concatenate([[lo0, math.log(hi0 - lo0)], beta0])

    def resid(th):
        lo, hi, b0, beta = pack(th)
        return g_curve(b0 + X @ beta, lo, hi) - ra

    def jac(th):
        lo, hi, b0, beta = pack(th)
        phi = b0 + X @ beta
        s = _sig(phi)
        d = (hi - lo) * s * (1 - s)
        J = np.empty((n, p + 3))
        J[:, 0] = 1.0 - s                     # d/d lo
        J[:, 1] = s * (hi - lo)               # d/d log(hi-lo)
        J[:, 2] = d
        J[:, 3:] = d[:, None] * X
        return J

    # the top of the curve is only weakly identified (few variants sit near it), so the upper
    # asymptote is held between half and three times the largest measured activity (D3)
    mx = float(np.max(ra))
    lob = np.full(p + 3, -np.inf)
    upb = np.full(p + 3, np.inf)
    lob[0], upb[0] = -0.2, 0.3
    lob[1], upb[1] = math.log(0.5 * mx), math.log(3.0 * mx)
    th0[0] = min(max(th0[0], lob[0] + 1e-6), upb[0] - 1e-6)
    th0[1] = min(max(th0[1], lob[1] + 1e-6), upb[1] - 1e-6)
    r = optimize.least_squares(resid, th0, jac=jac, method="trf", bounds=(lob, upb),
                               max_nfev=maxfev, xtol=1e-10, ftol=1e-10, gtol=1e-10)
    lo, hi, b0, beta = pack(r.x)
    return {"lo": float(lo), "hi": float(hi), "b0": float(b0), "beta": beta, "nfev": int(r.nfev),
            "cost": float(r.cost)}


def predict_G(m, X):
    return g_curve(m["b0"] + X @ m["beta"], m["lo"], m["hi"])


def latent(m, ra):
    """g inverse of a measured RA, clipped just inside the curve's range."""
    y = np.clip((ra - m["lo"]) / (m["hi"] - m["lo"]), 1e-3, 1 - 1e-3)
    return np.log(y / (1 - y))


# ---------------------------------------------------------------- model GP (G + pair terms)
def pair_list(X, min_co=MIN_CO):
    C = X.T @ X
    iu = np.triu_indices(X.shape[1], 1)
    keep = C[iu] >= min_co
    return list(zip(iu[0][keep], iu[1][keep]))


def pair_matrix(X, pairs):
    if not pairs:
        return np.zeros((X.shape[0], 0))
    i = np.array([a for a, _ in pairs])
    j = np.array([b for _, b in pairs])
    return X[:, i] * X[:, j]


def fit_GP(m, X, ra, pairs):
    """Ridge on the latent scale: t = b0 + X beta + P gamma, with beta and b0 refitted freely and
    gamma penalised.  Keeps model G's curve, so GP differs from G only by the pair terms."""
    P = pair_matrix(X, pairs)
    A = np.concatenate([np.ones((X.shape[0], 1)), X, P], axis=1)
    t = latent(m, ra)
    pen = np.zeros(A.shape[1])
    pen[1 + X.shape[1]:] = RIDGE
    pen[:1 + X.shape[1]] = 1e-6
    w = np.linalg.solve(A.T @ A + np.diag(pen), A.T @ t)
    return {"w": w, "pairs": pairs, "lo": m["lo"], "hi": m["hi"]}


def predict_GP(gp, X):
    A = np.concatenate([np.ones((X.shape[0], 1)), X, pair_matrix(X, gp["pairs"])], axis=1)
    return g_curve(A @ gp["w"], gp["lo"], gp["hi"])


# ---------------------------------------------------------------- the small network
def fit_net(Xoh, label, rng, epochs=NET_EPOCHS, hid=NET_HID):
    """Small MLP (ReLU, sigmoid output, Adam, binary cross-entropy).  numpy only."""
    n, d = Xoh.shape
    sizes = [d] + list(hid) + [1]
    W, b = [], []
    for a, c in zip(sizes[:-1], sizes[1:]):
        W.append(rng.normal(0, math.sqrt(2.0 / a), size=(a, c)))
        b.append(np.zeros(c))
    mW = [np.zeros_like(x) for x in W]
    vW = [np.zeros_like(x) for x in W]
    mb = [np.zeros_like(x) for x in b]
    vb = [np.zeros_like(x) for x in b]
    y = label.astype(np.float64).reshape(-1, 1)
    step = 0
    for ep in range(epochs):
        order = rng.permutation(n)
        for s in range(0, n, NET_BATCH):
            ix = order[s:s + NET_BATCH]
            xb, yb = Xoh[ix], y[ix]
            acts = [xb]
            for k in range(len(W) - 1):
                acts.append(np.maximum(acts[-1] @ W[k] + b[k], 0.0))
            z = acts[-1] @ W[-1] + b[-1]
            out = _sig(z)
            dz = (out - yb) / len(ix)
            gW = [None] * len(W)
            gb = [None] * len(W)
            for k in range(len(W) - 1, -1, -1):
                gW[k] = acts[k].T @ dz
                gb[k] = dz.sum(0)
                if k:
                    dz = (dz @ W[k].T) * (acts[k] > 0)
            step += 1
            for k in range(len(W)):
                mW[k] = 0.9 * mW[k] + 0.1 * gW[k]
                vW[k] = 0.999 * vW[k] + 0.001 * gW[k] ** 2
                mb[k] = 0.9 * mb[k] + 0.1 * gb[k]
                vb[k] = 0.999 * vb[k] + 0.001 * gb[k] ** 2
                mh = mW[k] / (1 - 0.9 ** step)
                vh = vW[k] / (1 - 0.999 ** step)
                W[k] -= NET_LR * mh / (np.sqrt(vh) + 1e-8)
                mh = mb[k] / (1 - 0.9 ** step)
                vh = vb[k] / (1 - 0.999 ** step)
                b[k] -= NET_LR * mh / (np.sqrt(vh) + 1e-8)
    return {"W": W, "b": b}


def predict_net(net, Xoh):
    a = Xoh
    for k in range(len(net["W"]) - 1):
        a = np.maximum(a @ net["W"][k] + net["b"][k], 0.0)
    return _sig(a @ net["W"][-1] + net["b"][-1]).ravel()


# ---------------------------------------------------------------- replicate noise (real)
class NoiseBank:
    """The real replicate noise.  For a variant measured twice, the deviation of one replicate from the
    mean of the two has the same spread as the error of that mean around the truth.  So the empirical
    distribution of (RA_rep - Mean_RA), binned by level and by read depth, is used as the error that a
    simulated true activity picks up when it is 'measured'."""

    NLEV = 12

    def __init__(self, ra_mean, ra1, ra2, depth):
        ok = np.isfinite(ra1) & np.isfinite(ra2) & np.isfinite(ra_mean)
        self.edges = np.quantile(ra_mean[ok], np.linspace(0, 1, self.NLEV + 1))
        self.edges[0] -= 1e-9
        self.edges[-1] += 1e-9
        dev = np.concatenate([ra1[ok] - ra_mean[ok], ra2[ok] - ra_mean[ok]])
        lev = np.concatenate([ra_mean[ok], ra_mean[ok]])
        self.bank = []
        ix = np.clip(np.digitize(lev, self.edges) - 1, 0, self.NLEV - 1)
        for k in range(self.NLEV):
            d = dev[ix == k]
            self.bank.append(d if len(d) >= 50 else dev)

    def measure(self, true_ra, rng):
        ix = np.clip(np.digitize(true_ra, self.edges) - 1, 0, self.NLEV - 1)
        out = np.empty(len(true_ra))
        for k in range(self.NLEV):
            m = ix == k
            if m.any():
                d = self.bank[k]
                out[m] = true_ra[m] + d[rng.integers(0, len(d), m.sum())]
        return np.maximum(out, 0.0)


# ---------------------------------------------------------------- data object
class Data:
    def __init__(self, with_wtmut=False):
        self.g16 = load(GEN16)
        self.g7 = load(GEN7)
        self.g8 = load(GEN8)
        self.X16 = mut_matrix(self.g16["Sequences"])
        self.O16 = onehot(self.g16["Sequences"])
        self.X7 = mut_matrix(self.g7["Sequences"])
        self.O7 = onehot(self.g7["Sequences"])
        self.X8 = mut_matrix(self.g8["Sequences"])
        self.O8 = onehot(self.g8["Sequences"])
        self.tr, self.te = author_split(len(self.X16))
        self.wtmut = read_csv(os.path.join(D, RAW, WTMUT)) if with_wtmut else None


# ---------------------------------------------------------------- the authors' log-additive model
def log_additive(pool_seq, pool_ra, seqs):
    """The authors' own 'epistasis-free' model (Generate_Figure_3.ipynb, cell 5): sum the ln(RA) of the
    constituent single mutants, measured in generation 1, and exponentiate."""
    ix = {s: i for i, s in enumerate(pool_seq)}
    sm = np.full(len(MUTS), np.nan)
    for k, (p, bse) in enumerate(MUTS):
        v = WT[:p] + bse + WT[p + 1:]
        if v in ix:
            with np.errstate(divide="ignore"):
                sm[k] = math.log(pool_ra[ix[v]]) if pool_ra[ix[v]] > 0 else -np.inf
    X = mut_matrix(seqs)
    use = np.nan_to_num(sm, nan=0.0, neginf=-50.0)
    with np.errstate(over="ignore"):
        return np.exp(X @ use), np.isnan(sm).sum()


# ---------------------------------------------------------------- scoring one fitted world
def score_world(ra16, ra7, ra8, d, rng, net_seeds=NET_RESTARTS, want_ceiling=None):
    """Fit G, GP and the network on the generation 1-6 training split of the activities handed in, then
    score every model on generations 7 and 8.  `ra16/ra7/ra8` are measured activities (real or simulated).
    Nothing here reads generation 7 or 8 activities before they are scored."""
    Xtr, ytr = d.X16[d.tr], ra16[d.tr]
    G = fit_G(Xtr, ytr)
    pairs = pair_list(Xtr)
    GP = fit_GP(G, Xtr, ytr, pairs)
    lab_tr = (ytr >= RT)
    nets = [fit_net(d.O16[d.tr], lab_tr, np.random.default_rng([int(rng.integers(1 << 30)), s]))
            for s in range(net_seeds)]

    out = {"n_pairs": len(pairs), "G": {"lo": G["lo"], "hi": G["hi"], "b0": G["b0"],
                                        "beta_sd": float(np.std(G["beta"]))}}
    for tag, X, O, ra in (("gen7", d.X7, d.O7, ra7), ("gen8", d.X8, d.O8, ra8),
                          ("gen16_test", d.X16[d.te], d.O16[d.te], ra16[d.te])):
        lab = ra >= RT
        pg, pgp = predict_G(G, X), predict_GP(GP, X)
        pn = [predict_net(nt, O) for nt in nets]
        ap_n = float(np.max([average_precision(p, lab) for p in pn]))
        hd = (d.g7 if tag == "gen7" else d.g8 if tag == "gen8" else d.g16)["HD_WT"]
        if tag == "gen16_test":
            hd = hd[d.te]
        bins = hamming_bins(hd)
        null_ap = float(np.median([average_precision(shuffle_in_bins(pg, bins, rng), lab)
                                   for _ in range(20)]))
        out[tag] = {
            "n": int(len(ra)), "neutral_frac": float(lab.mean()),
            "ap_G": average_precision(pg, lab), "ap_GP": average_precision(pgp, lab), "ap_net": ap_n,
            "ap_null_shuffled_in_hd_bins": null_ap,
            "rho_G": spearman(pg, ra), "rho_GP": spearman(pgp, ra),
            "recall_G": recall_at(pg, lab, RT), "recall_GP": recall_at(pgp, lab, RT),
            "lift": float(max(average_precision(pgp, lab), ap_n) - average_precision(pg, lab)),
        }
    if want_ceiling is not None:
        out["ceiling"] = want_ceiling
    return out


def verdict(o):
    """D7.  Kill: model G both recovers the measured generation-8 neutral variants and is not beaten by
    a model that carries specific interactions.  Support: G is beaten by at least SUP_LIFT in average
    precision and does not recover them.  The plan's rule as written is reported next to it."""
    g8 = o["gen8"]
    kill = (g8["recall_G"] >= KILL_RECALL) and (g8["lift"] <= KILL_AP_GAP)
    support = (not kill) and (g8["lift"] >= SUP_LIFT)
    plan_kill = (g8["recall_G"] >= KILL_RECALL) and (g8["ap_G"] >= g8["ap_net"] - KILL_AP_GAP)
    plan_support = (g8["recall_G"] < SUP_RECALL) and (g8["lift"] >= SUP_LIFT)
    v = "kill" if kill else ("support" if support else "partly")
    return {"verdict": v, "kill": bool(kill), "support": bool(support),
            "plan_as_written": "kill" if plan_kill else ("support" if plan_support else "partly"),
            "recall_G_gen8": g8["recall_G"], "ap_G_gen8": g8["ap_G"], "ap_net_gen8": g8["ap_net"],
            "lift_gen8": g8["lift"]}


# ---------------------------------------------------------------- gate
def gate():
    check_inputs(list(SHA))
    d = Data(with_wtmut=True)
    n16 = len(d.X16)
    pool = {"seq": np.concatenate([d.g16["Sequences"], d.g7["Sequences"], d.g8["Sequences"]]),
            "ra": np.concatenate([d.g16["Mean_RA"], d.g7["Mean_RA"], d.g8["Mean_RA"]])}
    la8, missing = log_additive(pool["seq"], pool["ra"], d.g8["Sequences"])
    la7, _ = log_additive(pool["seq"], pool["ra"], d.g7["Sequences"])
    la1, _ = log_additive(pool["seq"], pool["ra"], d.g16["Sequences"])

    neutral8 = d.g8["Mean_RA"] >= RT
    exp8 = la8 >= RT
    g7alg = d.g7["Algorithm"]
    rows7 = {}
    for a in np.unique(g7alg):
        m = g7alg == a
        lab = d.g7["Mean_RA"][m] >= RT
        rows7[str(a)] = {"n": int(m.sum()), "observed_neutral_frac": float(lab.mean()),
                         "also_expected_neutral_frac": float(((la7[m] >= RT) & lab).mean())}

    gen1 = np.array([str(x) == "1" for x in d.g16["Generation"]])
    hd1 = d.g16["HD_WT"][gen1]
    dt = gen1 & (d.g16["HD_WT"] > 1)          # Generate_Figure_2.ipynb, cell 11
    obs, pred = d.g16["Mean_RA"][dt], la1[dt]
    r2_fig2c = float(1.0 - ((obs - pred) ** 2).sum() / ((obs - obs.mean()) ** 2).sum())
    wm = d.wtmut
    wm_neutral = float((wm["Mean_RA"] >= RT).mean())
    ceil = {"n": int(len(wm["RA_1"])),
            "ap_rep1_for_rep2": average_precision(wm["RA_1"], wm["RA_2"] >= RT),
            "rho_rep1_rep2": spearman(wm["RA_1"], wm["RA_2"]),
            "recall_rep1_for_rep2": recall_at(wm["RA_1"], wm["RA_2"] >= RT, RT),
            "neutral_frac_mean": wm_neutral}

    g = {
        "mode": "gate", "script_sha256": sha256(os.path.abspath(__file__)),
        "rows_gen1_6": int(n16), "unique_sequences_gen1_6": int(len(set(d.g16["Sequences"]))),
        "authors_split": {"train": int(len(d.tr)), "test": int(len(d.te)),
                          "published_train": PUB["train"], "published_test": PUB["test"],
                          "match": bool(len(d.tr) == PUB["train"] and len(d.te) == PUB["test"])},
        "rows_gen7": int(len(d.X7)), "rows_gen8": int(len(d.X8)),
        "single_mutants_missing_from_data": int(missing),
        "gen8": {"n": int(len(neutral8)), "observed_neutral_frac": float(neutral8.mean()),
                 "published_fig3b_observed": PUB["gen8_neutral_frac"],
                 "also_expected_neutral_frac": float((exp8 & neutral8).mean()),
                 "share_of_neutral_called_neutral_by_log_additive": float(exp8[neutral8].mean())},
        "gen7_by_algorithm": rows7,
        "gen1": {"n": int(gen1.sum()), "neutral_frac": float((d.g16["Mean_RA"][gen1] >= RT).mean()),
                 "published_fig5a": PUB["gen1_neutral_frac"],
                 "r2_fig2c_log_additive_hd_gt1": r2_fig2c,
                 "published_text_75_5_percent": PUB["gen1_LA_predictable"],
                 "n_hd_gt1": int(dt.sum()), "hd_range": [int(hd1.min()), int(hd1.max())]},
        "wt_mut_library": {"rows": int(len(wm["RA_1"])), "neutral_frac": wm_neutral,
                           "published_fig5a": PUB["wtmut_neutral_frac"]},
        "replicate_ceiling": ceil,
    }
    g["gate_pass"] = bool(
        g["authors_split"]["match"]
        and abs(g["gen8"]["observed_neutral_frac"] - PUB["gen8_neutral_frac"]) <= 0.02
        and g["gen8"]["share_of_neutral_called_neutral_by_log_additive"] <= 0.10
        and abs(r2_fig2c - PUB["gen1_LA_predictable"]) <= 0.02
        and abs(g["wt_mut_library"]["neutral_frac"] - PUB["wtmut_neutral_frac"]) <= 0.02)
    print(json.dumps(g, indent=1, default=float))
    dump("t13_gate.json", g)


# ---------------------------------------------------------------- planted check
# name, kind, size
SCEN = [                               # name, planted interaction kind, size (1.0 = flips ~30% of calls)
    ("null_global_curve_pin16", "none_pin16", 0.0),
    ("null_global_curve_pin8", "none", 0.0),
    ("pairs_flip30", "pair", 1.0),
    ("third_order_flip30", "triple", 1.0),
    ("pairs_flip15", "pair", 0.5),
    ("pairs_flip45", "pair", 1.5),
]

TARGET_GEN8_NEUTRAL = 0.28      # published, Fig. 3b / Results ("the fraction of neutral mutants in
#                                 generation 8 was only 0.28"); a published marginal, not a fit


def calibrate_truth(d, truth, target16, target8, pin="gen16"):
    """The H0 world: a pure global-curve truth in which the mutations the algorithm chose really are
    additively near-neutral.

    Model G fitted to generations 1-6 alone sends the latent score so low at Hamming distance 13 that a
    simulated generation 8 would hold no neutral variant at all and no metric could be computed.  No
    rescaling of the fitted terms can fix that, because every generation-8 genotype sits below the whole
    generation 1-6 distribution.  So the H0 world shrinks the per-mutation effects of the mutations that
    generation 8 actually uses, by one factor k, and shifts the intercept by a:

        beta*_m = beta_m * (1 - (1 - k) * min(1, f_m / f95)),  phi = b0 + a + X beta*

    where f_m is how often mutation m appears among the generation-8 genotypes and f95 is the 95th
    percentile of f.  a is set so the noise-free generation 1-6 neutral fraction equals the real one; k is
    set so the noise-free generation 8 fraction equals the published 0.28.  Only genotypes, one training
    marginal and one published marginal enter.  No generation 7 or 8 per-variant outcome is read.  The
    truth stays additive-latent through one monotone curve, with no interaction of any order: it is
    exactly the hypothesis the study puts up against the authors' reading.
    """
    f = d.X8.mean(axis=0)
    f95 = float(np.percentile(f, 95)) or 1.0
    shrink = np.minimum(1.0, f / f95)
    z16raw, z8raw = d.X16, d.X8

    def beta_of(k):
        return truth["beta"] * (1.0 - (1.0 - k) * shrink)

    def frac(a, bet, X):
        return float((g_curve(truth["b0"] + a + X @ bet, truth["lo"], truth["hi"]) >= RT).mean())

    def solve_a(bet):
        la, ha = -40.0, 40.0
        for _ in range(100):
            m = 0.5 * (la + ha)
            if frac(m, bet, z16raw) < target16:
                la = m
            else:
                ha = m
        return 0.5 * (la + ha)

    best = None
    if pin == "gen16":
        # keep the real generation 1-6 marginal; get as close to target8 as that allows
        for k in np.linspace(0.0, 1.0, 201):
            bet = beta_of(float(k))
            a = solve_a(bet)
            e = abs(frac(a, bet, z8raw) - target8)
            if best is None or e < best[0]:
                best = (e, float(k), a, bet)
    else:
        # hit target8 exactly, and among the (k, a) that do, keep the generation 1-6 marginal closest
        for k in np.linspace(0.0, 1.0, 101):
            bet = beta_of(float(k))
            for a in np.linspace(-6.0, 6.0, 481):
                if abs(frac(float(a), bet, z8raw) - target8) <= 0.01:
                    e = abs(frac(float(a), bet, z16raw) - target16)
                    if best is None or e < best[0]:
                        best = (e, float(k), float(a), bet)
    if best is None:
        raise SystemExit("no pure global-curve world reaches the targets; see the prereg")
    err, k, a, bet = best
    return {"lo": truth["lo"], "hi": truth["hi"], "b0": truth["b0"] + a, "beta": bet,
            "pin": pin, "shrink_k": k, "shift_a": a, "target_error": err,
            "frac16": frac(a, bet, z16raw), "frac8": frac(a, bet, z8raw),
            "frac7": frac(a, bet, d.X7)}


def simulate(d, truth, pin16, nb, rng, kind, size, pairs):
    """True activity from a pure global-curve world, optionally with planted specific interactions of a
    given order, then measured with the real replicate noise."""
    out = []
    for X in (d.X16, d.X7, d.X8):
        t = pin16 if kind == "none_pin16" else truth
        phi = t["b0"] + X @ t["beta"]
        if kind == "pair" and size > 0:
            P = pair_matrix(X, pairs["pairs"])
            phi = phi + size * (P @ pairs["gamma"])
        if kind == "triple" and size > 0:
            T = pairs["triple_mat"](X)
            phi = phi + size * (T @ pairs["gamma3"])
        true_ra = g_curve(phi, t["lo"], t["hi"])
        out.append(nb.measure(true_ra, rng))
    return out


def planted():
    check_inputs(list(SHA))
    d = Data()
    rng = np.random.default_rng([SEED, 2])
    nb = NoiseBank(d.g16["Mean_RA"], d.g16["RA_1"], d.g16["RA_2"], d.g16["TR_1"] + d.g16["TR_2"])
    raw = fit_G(d.X16[d.tr], d.g16["Mean_RA"][d.tr])
    t16 = float((d.g16["Mean_RA"] >= RT).mean())
    pin16 = calibrate_truth(d, raw, t16, TARGET_GEN8_NEUTRAL, pin="gen16")
    truth = calibrate_truth(d, raw, t16, TARGET_GEN8_NEUTRAL, pin="gen8")
    keys = ("pin", "shrink_k", "shift_a", "target_error", "frac16", "frac7", "frac8", "lo", "hi", "b0")
    print(json.dumps({"worlds": [{k: w[k] for k in keys} for w in (pin16, truth)],
                      "real_gen16_neutral_frac": t16}, default=float), flush=True)

    # planted interaction terms: drawn once, on pairs and triples of mutations that actually co-occur
    plist = pair_list(d.X16[d.tr], MIN_CO)
    gamma = rng.normal(0, 1.0, size=len(plist))
    tri = [(plist[i][0], plist[i][1], (plist[i][0] + 7) % len(MUTS)) for i in range(0, len(plist), 3)]

    def triple_mat(X):
        if not tri:
            return np.zeros((X.shape[0], 0))
        a = np.array([t[0] for t in tri]); b = np.array([t[1] for t in tri]); c = np.array([t[2] for t in tri])
        return X[:, a] * X[:, b] * X[:, c]

    pk = {"pairs": plist, "gamma": gamma, "gamma3": rng.normal(0, 1.0, size=len(tri)),
          "triple_mat": triple_mat}

    # scale each planted kind so that about 30% of the generation-8 calls flip against the pure curve
    base8 = g_curve(truth["b0"] + d.X8 @ truth["beta"], truth["lo"], truth["hi"]) >= RT  # calibrated
    scales = {}
    for name, kind, size in SCEN:
        if kind in ("none", "none_steep"):
            continue
        lo, hi = 0.0, 40.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if kind == "pair":
                phi = truth["b0"] + d.X8 @ truth["beta"] + mid * (pair_matrix(d.X8, plist) @ gamma)
            else:
                phi = truth["b0"] + d.X8 @ truth["beta"] + mid * (triple_mat(d.X8) @ pk["gamma3"])
            flip = (g_curve(phi, truth["lo"], truth["hi"]) >= RT) != base8
            if flip.mean() < 0.30:
                lo = mid
            else:
                hi = mid
        scales[name] = 0.5 * (lo + hi)

    which = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else list(range(len(SCEN)))
    rows = []
    for si in which:
        name, kind, size = SCEN[si]
        sc = scales.get(name, 0.0) * (size if size else 1.0)
        reps = []
        for r in range(NREP):
            rr = np.random.default_rng([SEED, 2, si, r])
            ra16, ra7, ra8 = simulate(d, truth, pin16, nb, rr, kind, sc, pk)
            o = score_world(ra16, ra7, ra8, d, rr, net_seeds=2)
            v = verdict(o)
            v["gen8_neutral_frac"] = o["gen8"]["neutral_frac"]
            v["ap_GP_gen8"] = o["gen8"]["ap_GP"]
            v["ap_null_gen8"] = o["gen8"]["ap_null_shuffled_in_hd_bins"]
            v["rho_G_gen8"] = o["gen8"]["rho_G"]
            v["recall_G_gen7"] = o["gen7"]["recall_G"]
            v["ap_G_gen7"] = o["gen7"]["ap_G"]
            v["lift_gen7"] = o["gen7"]["lift"]
            reps.append(v)
            print(json.dumps({"scenario": name, "rep": r, **v}, default=float), flush=True)
        agg = {"scenario": name, "kind": kind, "scale": sc, "nrep": len(reps)}
        for k in ("kill", "support"):
            agg[k + "_rate"] = float(np.mean([x[k] for x in reps]))
        for k in ("recall_G_gen8", "ap_G_gen8", "ap_net_gen8", "ap_GP_gen8", "lift_gen8",
                  "ap_null_gen8", "gen8_neutral_frac", "rho_G_gen8", "recall_G_gen7", "lift_gen7"):
            agg[k + "_mean"] = float(np.mean([x[k] for x in reps]))
        agg["lift_gen8_max"] = float(np.max([x["lift_gen8"] for x in reps]))
        agg["lift_gen8_min"] = float(np.min([x["lift_gen8"] for x in reps]))
        agg["recall_G_gen8_min"] = float(np.min([x["recall_G_gen8"] for x in reps]))
        agg["recall_G_gen8_max"] = float(np.max([x["recall_G_gen8"] for x in reps]))
        agg["verdicts"] = {v: int(sum(1 for x in reps if x["verdict"] == v))
                           for v in ("kill", "partly", "support")}
        agg["verdicts_plan_as_written"] = {v: int(sum(1 for x in reps if x["plan_as_written"] == v))
                                           for v in ("kill", "partly", "support")}
        rows.append(agg)
        print(json.dumps(agg, indent=1, default=float), flush=True)
    res = {"mode": "planted", "seed": [SEED, 2], "nrep": NREP,
           "script_sha256": sha256(os.path.abspath(__file__)), "scales": scales, "rows": rows}
    tag = "" if len(sys.argv) <= 4 else "_part_" + sys.argv[4].replace(",", "-")
    dump("t13_planted%s.json" % tag, res)


def planted_merge():
    import glob
    parts = sorted(glob.glob(os.path.join(D, "scripts_out", "t13_planted_part_*.json")))
    rows, meta = [], None
    for p in parts:
        j = json.load(open(p))
        meta = meta or j
        if j["script_sha256"] != meta["script_sha256"] or j["nrep"] != meta["nrep"]:
            sys.exit("parts disagree on script hash or nrep: " + p)
        rows += j["rows"]
    meta["rows"] = rows
    meta["merged_from"] = [os.path.basename(p) for p in parts]
    dump("t13_planted.json", meta)


# ---------------------------------------------------------------- real / dry run
def real(dry=False):
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    check_inputs(list(SHA))
    d = Data(with_wtmut=True)
    rng = np.random.default_rng([SEED, 4 if dry else 3])
    ra16 = d.g16["Mean_RA"]
    ra7, ra8 = d.g7["Mean_RA"].copy(), d.g8["Mean_RA"].copy()
    if dry:
        ra7 = shuffle_in_bins(ra7, hamming_bins(d.g7["HD_WT"]), rng)
        ra8 = shuffle_in_bins(ra8, hamming_bins(d.g8["HD_WT"]), rng)
    wm = d.wtmut
    ceil = {"n": int(len(wm["RA_1"])),
            "ap_rep1_for_rep2": average_precision(wm["RA_1"], wm["RA_2"] >= RT),
            "rho_rep1_rep2": spearman(wm["RA_1"], wm["RA_2"]),
            "recall_rep1_for_rep2": recall_at(wm["RA_1"], wm["RA_2"] >= RT, RT)}
    o = score_world(ra16, ra7, ra8, d, rng, net_seeds=NET_RESTARTS, want_ceiling=ceil)
    pool_seq = np.concatenate([d.g16["Sequences"], d.g7["Sequences"], d.g8["Sequences"]])
    pool_ra = np.concatenate([ra16, ra7, ra8])
    la8, _ = log_additive(pool_seq, pool_ra, d.g8["Sequences"])
    lab8 = ra8 >= RT
    o["gen8"]["log_additive_recall"] = recall_at(la8, lab8, RT)
    o["gen8"]["log_additive_ap"] = average_precision(la8, lab8)
    res = {"mode": "dryrun_labels_permuted_in_hd_bins" if dry else "real",
           "seed": [SEED, 4 if dry else 3], "script_sha256": st["script_sha256"],
           "verdict": verdict(o), "detail": o}
    print(json.dumps(res, indent=1, default=float))
    dump("t13_dryrun_permuted_labels.json" if dry else "t13_real.json", res)


if __name__ == "__main__":
    np.seterr(invalid="ignore", divide="ignore", over="ignore")
    if MODE == "gate":
        gate()
    elif MODE == "planted":
        planted()
    elif MODE == "planted_merge":
        planted_merge()
    elif MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "dryrun":
        real(dry=True)
    elif MODE == "real":
        real(dry=False)
    else:
        sys.exit("unknown mode")
