"""Summary statistics of Moody et al. 2024's real data that the simulation is fitted to (task #32).
None of these use root presence probabilities. Usage: python -I real_stats.py <raw/moody/Supp_data> <out.json>"""
import sys, os, json, glob, random, collections
import numpy as np

D, OUT = sys.argv[1], sys.argv[2]
tax = {}
for line in open(os.path.join(D, "Taxonomy/ArcBacEuk_names.csv")).read().splitlines()[1:]:
    k, t = line.split("\t")[:2]
    tax[k] = t.split("_")[0]
fams = sorted(glob.glob(os.path.join(D, "Gene_Fastas/Pure_sequences/K*.fasta")))
copies = collections.defaultdict(dict)  # fam -> genome -> copies
for f in fams:
    k = os.path.basename(f).split(".")[0]
    for line in open(f):
        if line.startswith(">"):
            g = line[1:].split("-", 1)[0].strip()
            copies[k][g] = copies[k].get(g, 0) + 1
genomes = sorted({g for c in copies.values() for g in c})
dom = {g: tax.get(g, "unknown") for g in genomes}
n = collections.Counter(dom.values())
A = [g for g in genomes if dom[g] == "Archaea"]; B = [g for g in genomes if dom[g] == "Bacteria"]
occA, occB, mcopy = [], [], []
for k, c in copies.items():
    occA.append(sum(g in c for g in A) / max(1, len(A)))
    occB.append(sum(g in c for g in B) / max(1, len(B)))
    mcopy.append(np.mean(list(c.values())))
occA, occB, mcopy = map(np.array, (occA, occB, mcopy))
occ = (occA * len(A) + occB * len(B)) / (len(A) + len(B))
gsize = collections.Counter(g for c in copies.values() for g in c)
# alignment length and divergence on a fixed random subset (seed 0) of trimmed alignments
random.seed(0)
alns = sorted(glob.glob(os.path.join(D, "Gene_Fastas/Trimmed_Alignments/*")))
L, pd_ = [], []
for f in random.sample(alns, min(300, len(alns))):
    seqs, cur = [], []
    for line in open(f):
        if line.startswith(">"):
            if cur: seqs.append("".join(cur))
            cur = []
        else:
            cur.append(line.strip())
    if cur: seqs.append("".join(cur))
    if len(seqs) < 4: continue
    L.append(len(seqs[0]))
    s = random.sample(seqs, min(30, len(seqs)))
    d = []
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            m = [(a, b) for a, b in zip(s[i], s[j]) if a != "-" and b != "-"]
            if len(m) >= 30: d.append(sum(a != b for a, b in m) / len(m))
    if d: pd_.append(float(np.mean(d)))
q = lambda x: [float(v) for v in np.quantile(x, [0.1, 0.25, 0.5, 0.75, 0.9])]
res = dict(n_families=len(copies), n_genomes=len(genomes), domains=dict(n), n_archaea=len(A), n_bacteria=len(B),
           occupancy_quantiles=q(occ), occupancy_hist=np.histogram(occ, bins=10, range=(0, 1))[0].tolist(),
           frac_both_domains=float(np.mean((occA > 0) & (occB > 0))),
           frac_both_domains_1pct=float(np.mean((occA > 0.01) & (occB > 0.01))),
           mean_copies_quantiles=q(mcopy), genome_size_families_quantiles=q(list(gsize.values())),
           trimmed_aln_length_quantiles=q(L), mean_pdistance_quantiles=q(pd_), n_aln_sampled=len(L))
json.dump(res, open(OUT, "w"), indent=1)
print(json.dumps(res, indent=1))
