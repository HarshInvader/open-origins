"""Task #9: planted LUCA recovery under loss + horizontal transfer. See docs/prereg/luca_planted_recovery.md.
Usage: .venv/bin/python -I sim.py <out_dir> [quick]
Resumable: one JSON line per (mu, ratio, seed) in out/runs.jsonl.
"""
import sys, os, json
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import expm

OUT = sys.argv[1]; QUICK = len(sys.argv) > 2
os.makedirs(OUT, exist_ok=True)
RUNS = os.path.join(OUT, 'runs.jsonl')
NTIP_DOM, CROWN, DT = 32, 0.8, 0.002
N_LUCA, N_LATE = 500, 1500
MUS, RATIOS, SEEDS = [1.0, 2.0], [0.0, 0.1, 0.3, 1.0, 3.0], range(10)
if QUICK:
    MUS, RATIOS, SEEDS, DT = [1.0], [0.0, 1.0], range(1), 0.005


# ---------------- species tree: nodes with parent, start, end time; tips at t=1
def yule_crown(rng, n, t0):
    """Yule crown tree from t0 to 1 with n tips; returns list of (parent_local, start, end) edges"""
    lam = np.log(n / 2) / (1 - t0) if n > 2 else 1.0
    # simulate by successive splitting of random lineages at sampled times, conditioned on n tips (rescale times)
    times = np.sort(rng.exponential(1.0, n - 2).cumsum())
    times = t0 + (1 - t0) * (np.r_[0, times] / (times[-1] * 1.0001 + 1e-9) if n > 2 else np.array([0.0]))
    nodes = [dict(parent=None, start=t0, end=None, kids=[])]
    alive = []
    # crown root splits at t0 into two lineages
    for _ in range(2):
        nodes.append(dict(parent=0, start=t0, end=None, kids=[])); nodes[0]['kids'].append(len(nodes) - 1); alive.append(len(nodes) - 1)
    nodes[0]['end'] = t0
    for t in times[1:]:
        i = alive.pop(rng.integers(len(alive)))
        nodes[i]['end'] = t
        for _ in range(2):
            nodes.append(dict(parent=i, start=t, end=None, kids=[])); nodes[i]['kids'].append(len(nodes) - 1); alive.append(len(nodes) - 1)
    for i in alive:
        nodes[i]['end'] = 1.0
    return nodes


def species_tree(rng):
    """global node list: 0 = root (t=0); 1,2 = domain stems ending at CROWN; crowns below"""
    nodes = [dict(parent=None, start=0.0, end=0.0, kids=[], dom=-1)]
    for d in (0, 1):
        sub = yule_crown(rng, NTIP_DOM, CROWN)
        off = len(nodes)
        for k, nd in enumerate(sub):
            p = 0 if nd['parent'] is None else nd['parent'] + off
            nodes.append(dict(parent=p, start=0.0 if nd['parent'] is None else nd['start'], end=nd['end'],
                              kids=[c + off for c in nd['kids']], dom=d))
            if nd['parent'] is None:
                nodes[0]['kids'].append(off)
    # subclade label: child of the crown root within each domain
    for i, nd in enumerate(nodes):
        nd['sub'] = -1
    for d_root in nodes[0]['kids']:
        for c in nodes[d_root]['kids']:
            stack = [c]
            while stack:
                j = stack.pop(); nodes[j]['sub'] = c; stack += nodes[j]['kids']
    return nodes


# ---------------- family simulation (vectorised over families)
def simulate(rng, nodes, mu, tau):
    nn = len(nodes)
    tips = [i for i, nd in enumerate(nodes) if not nd['kids']]
    # origination: LUCA families at root; late families at a uniform point on total branch length
    blen = np.array([nd['end'] - nd['start'] for nd in nodes])
    p = blen / blen.sum()
    F = N_LUCA + N_LATE
    orig_edge = np.r_[np.full(N_LUCA, -1), rng.choice(nn, N_LATE, p=p)]
    orig_time = np.r_[np.zeros(N_LUCA), [rng.uniform(nodes[e]['start'], nodes[e]['end']) for e in orig_edge[N_LUCA:]]]
    pres = np.zeros((F, nn), bool)   # presence on each edge (current state while edge is alive)
    pres[:N_LUCA, nodes[0]['kids']] = True
    # monophyly tracking: which domain a family first entered from root (LUCA: both); 'foreign' flags inter-domain receipt
    foreign = np.zeros((F, nn), bool)
    started = np.zeros(nn, bool); started[nodes[0]['kids']] = True
    pending_split = sorted([(nd['end'], i) for i, nd in enumerate(nodes) if nd['kids'] and i != 0])
    pending_orig = sorted(zip(orig_time[N_LUCA:], range(N_LUCA, F), orig_edge[N_LUCA:]))
    alive = list(nodes[0]['kids'])
    t = 0.0; si = oi = 0
    dom = np.array([nd['dom'] for nd in nodes])
    while t < 1.0 - 1e-12:
        t1 = min(t + DT, 1.0)
        while oi < len(pending_orig) and pending_orig[oi][0] <= t1:
            _, f, e = pending_orig[oi]; pres[f, e] = True; oi += 1
        A = np.array(alive)
        P = pres[:, A]
        # loss
        P &= ~(rng.random(P.shape) < mu * (t1 - t))
        # transfer: each carrying lineage sends with prob tau*dt to a random alive lineage
        if tau > 0:
            send = P & (rng.random(P.shape) < tau * (t1 - t))
            fs, ks = np.nonzero(send)
            if len(fs):
                rk = rng.integers(len(A), size=len(fs))
                newly = ~P[fs, rk]
                P[fs, rk] = True
                inter = dom[A[ks]] != dom[A[rk]]
                fo = foreign[:, A]
                fo[fs[inter & newly], rk[inter & newly]] = True
                foreign[:, A] = fo
        pres[:, A] = P
        while si < len(pending_split) and pending_split[si][0] <= t1:
            _, i = pending_split[si]; si += 1
            alive.remove(i)
            for c in nodes[i]['kids']:
                pres[:, c] = pres[:, i]; foreign[:, c] = foreign[:, i]; alive.append(c)
        t = t1
    tipP = pres[:, tips]
    tipF = foreign[:, tips]
    return tips, tipP, tipF


# ---------------- ML two-state gain/loss on species tree (Felsenstein pruning, vectorised over families)
def make_pruner(nodes, tips):
    order = []
    def post(i):
        for c in nodes[i]['kids']:
            post(c)
        order.append(i)
    post(0)
    tipidx = {n: k for k, n in enumerate(tips)}
    def loglik(params, X, return_pp=False):
        g, l, pi = np.exp(params[0]), np.exp(params[1]), 1 / (1 + np.exp(-params[2]))
        Q = np.array([[-g, g], [l, -l]])
        F = X.shape[0]
        Lk = {}
        for i in order:
            nd = nodes[i]
            if not nd['kids']:
                x = X[:, tipidx[i]]
                v = np.stack([~x, x], 1).astype(float)
            else:
                v = np.ones((F, 2))
                for c in nd['kids']:
                    Pm = expm(Q * (nodes[c]['end'] - nodes[c]['start']))
                    v = v * (Lk[c] @ Pm.T)
            Lk[i] = v
        root = Lk[0]
        lik = (1 - pi) * root[:, 0] + pi * root[:, 1]
        # P(all tips absent) for conditioning on observability
        z = np.zeros((1, X.shape[1]), bool)
        if return_pp:
            return pi * root[:, 1] / lik
        lz = loglik_empty(params)
        return -(np.log(lik + 1e-300).sum() - F * np.log(1 - lz + 1e-300))
    def loglik_empty(params):
        g, l, pi = np.exp(params[0]), np.exp(params[1]), 1 / (1 + np.exp(-params[2]))
        Q = np.array([[-g, g], [l, -l]]); Lk = {}
        for i in order:
            nd = nodes[i]
            if not nd['kids']:
                v = np.array([[1.0, 0.0]])
            else:
                v = np.ones((1, 2))
                for c in nd['kids']:
                    v = v * (Lk[c] @ expm(Q * (nodes[c]['end'] - nodes[c]['start'])).T)
            Lk[i] = v
        return float((1 - pi) * Lk[0][0, 0] + pi * Lk[0][0, 1])
    return loglik


def evaluate(nodes, tips, tipP, tipF, truth):
    dom = np.array([nodes[t]['dom'] for t in tips]); sub = np.array([nodes[t]['sub'] for t in tips])
    inA, inB = tipP[:, dom == 0], tipP[:, dom == 1]
    R1 = inA.any(1) & inB.any(1)
    def breadth(M, s):
        return np.array([len(set(s[r])) for r in M]) if len(M) else np.array([])
    subA = np.array([len(set(sub[dom == 0][row])) for row in inA])
    subB = np.array([len(set(sub[dom == 1][row])) for row in inB])
    R2 = (inA.sum(1) >= 2) & (inB.sum(1) >= 2) & (subA >= 2) & (subB >= 2)
    # oracle monophyly: no tip copy acquired via inter-domain transfer
    R6 = R2 & ~(tipF & tipP).any(1)
    ll = make_pruner(nodes, tips)
    fit = minimize(ll, x0=np.array([0.0, 0.0, 0.0]), args=(tipP,), method='L-BFGS-B',
                   bounds=[(-8, 4), (-8, 4), (-8, 8)])
    pp = ll(fit.x, tipP, return_pp=True)
    R3, R5 = pp >= 0.75, pp >= 0.5
    R4 = R3 & R1
    out = dict(n_obs=int(len(truth)), n_true=int(truth.sum()), size_est=float(pp.sum()),
               fit=dict(gain=float(np.exp(fit.x[0])), loss=float(np.exp(fit.x[1])), pi=float(1 / (1 + np.exp(-fit.x[2])))))
    out['size_relerr'] = (out['size_est'] - out['n_true']) / out['n_true']
    for name, R in dict(R1=R1, R2=R2, R3=R3, R4=R4, R5=R5, R6=R6).items():
        tp = int((R & truth).sum()); fp = int((R & ~truth).sum())
        out[name] = dict(called=int(R.sum()), precision=tp / max(1, tp + fp), recall=tp / max(1, int(truth.sum())))
    return out


def main():
    done = set()
    if os.path.exists(RUNS):
        for line in open(RUNS):
            r = json.loads(line); done.add((r['mu'], r['ratio'], r['seed']))
    with open(RUNS, 'a') as fh:
        for mu in MUS:
            for ratio in RATIOS:
                for seed in SEEDS:
                    if (mu, ratio, seed) in done:
                        continue
                    rng = np.random.default_rng(1000 * seed + int(10 * ratio) + int(100 * mu))
                    nodes = species_tree(rng)
                    tips, tipP, tipF = simulate(rng, nodes, mu, ratio * mu)
                    keep = tipP.any(1)
                    truth = np.r_[np.ones(N_LUCA, bool), np.zeros(N_LATE, bool)][keep]
                    r = evaluate(nodes, tips, tipP[keep], tipF[keep], truth)
                    r.update(mu=mu, ratio=ratio, seed=seed)
                    fh.write(json.dumps(r) + '\n'); fh.flush()
                    print(mu, ratio, seed, {k: (round(r[k]['precision'], 2), round(r[k]['recall'], 2)) for k in ['R1', 'R2', 'R4', 'R6']},
                          'size', round(r['size_relerr'], 2), flush=True)


if __name__ == '__main__':
    main()
