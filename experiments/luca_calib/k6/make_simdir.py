"""K6 (prereg v8): convert Moody et al.'s Subsample_test inputs into our pipeline's simdir layout.

Usage:
  python -I make_simdir.py <Subsample_test dir> <ArcBacEuk_names.csv> <out simdir> [--half-seed S]

Writes <out>/sample/species_tree.nwk (tips renamed GCA_000123 -> GCA000123, so ALE's "_" separator
works), <out>/sample/fasta/<i>.fasta (genes <species>_<n>, gaps kept: these are alignments, which
IQ-TREE reads directly), <out>/sample/truth.tsv (family, n_genes; no truth column: real data),
<out>/ko_map.tsv (i -> KO) and <out>/tips.tsv (tip, domain).
--half-seed S keeps a random half of the archaeal and half of the bacterial tips (jackknife draw).
"""
import sys, os, random, hashlib
from ete3 import Tree

SUB, TAX, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
half = int(sys.argv[sys.argv.index("--half-seed") + 1]) if "--half-seed" in sys.argv else None

dom = {}
for line in open(TAX).read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) >= 2:
        dom[p[0]] = p[1].split("_")[0]

t = Tree(os.path.join(SUB, "subsampled_tree.tre.rooted"), format=1)
tips = [l.name for l in t.get_leaves()]
assert all(n in dom for n in tips), [n for n in tips if n not in dom][:5]
keep = set(tips)
if half is not None:
    rng = random.Random(half)
    A = sorted(n for n in tips if dom[n] == "Archaea")
    B = sorted(n for n in tips if dom[n] == "Bacteria")
    keep = set(rng.sample(A, len(A) // 2) + rng.sample(B, len(B) // 2))
    t.prune(list(keep), preserve_branch_length=True)
ren = lambda n: n.replace("_", "")
for l in t.get_leaves():
    l.name = ren(l.name)
os.makedirs(os.path.join(OUT, "sample", "fasta"), exist_ok=True)
with open(os.path.join(OUT, "sample", "species_tree.nwk"), "w") as f:
    f.write(t.write(format=5) + "\n")
with open(os.path.join(OUT, "tips.tsv"), "w") as f:
    f.write("tip\tdomain\n")
    for n in sorted(keep):
        f.write("%s\t%s\n" % (ren(n), dom[n]))

adir = os.path.join(SUB, "gene_family_trimmed_for_sampling")
files = sorted(os.listdir(adir))
man = hashlib.sha256()
truth, kmap = [], []
i = 0
for fn in files:
    raw = open(os.path.join(adir, fn), "rb").read()
    man.update(fn.encode() + b"\0" + hashlib.sha256(raw).digest())
    ko = fn.split(".")[0]
    seqs, cur = [], None
    for line in raw.decode().splitlines():
        if line.startswith(">"):
            sp = line[1:].split("-", 1)[0].strip()
            cur = [sp, []]
            seqs.append(cur)
        elif cur is not None:
            cur[1].append(line.strip())
    seqs = [(sp, "".join(s)) for sp, s in seqs if sp in keep]
    if not seqs:
        continue
    if half is not None and all(set(s) <= set("-X?") for _, s in seqs):
        continue
    i += 1
    cnt = {}
    with open(os.path.join(OUT, "sample", "fasta", "%d.fasta" % i), "w") as f:
        for sp, s in seqs:
            cnt[sp] = cnt.get(sp, 0) + 1
            f.write(">%s_%d\n%s\n" % (ren(sp), cnt[sp], s))
    truth.append((str(i), len(seqs)))
    kmap.append((str(i), ko))
with open(os.path.join(OUT, "sample", "truth.tsv"), "w") as f:
    f.write("family\tn_genes\n")
    for fam, n in truth:
        f.write("%s\t%d\n" % (fam, n))
with open(os.path.join(OUT, "ko_map.tsv"), "w") as f:
    f.write("family\tko\n")
    for fam, ko in kmap:
        f.write("%s\t%s\n" % (fam, ko))
print("tips", len(keep), "A", sum(dom[n] == "Archaea" for n in keep), "B", sum(dom[n] == "Bacteria" for n in keep),
      "families", len(truth), ">=2 genes", sum(n >= 2 for _, n in truth), ">=4", sum(n >= 4 for _, n in truth),
      ">=100", sum(n >= 100 for _, n in truth), "manifest_sha256", man.hexdigest())
