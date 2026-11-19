"""Stem-to-stem transfer diagnostic (prereg v4 C), from Zombi's event files.

Usage: python stem_transfers.py <simdir>

The two stems are the complete-tree lineage paths from the sampled MRCA (exclusive) down to each
domain's sampled crown (the MRCA of that domain's sampled tips; the crown's own branch included).
A family is flagged when Zombi recorded its origination (O) on a lineage of one stem and a transfer
(T) whose donor lineage is on that stem and whose recipient lineage is on the other stem. Lineages on
a stem end at or before that stem's crown, so such a transfer is always before the recipient stem's
first sampled speciation. Lineage names and times come from zombi/T/Events.tsv; family events from
zombi/G/Gene_families/<fam>_events.tsv (T rows: donor;gene;donor;gene;recipient;gene).

Writes <simdir>/sample/stem_transfers.tsv: family, origin_stem (A/B/-), stem_to_stem (0/1).
score.py reports the share of false T50d calls that are flagged.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, read_tsv
from ete3 import Tree


def stems(sim):
    sp = Tree(open(os.path.join(sim, "sample", "species_tree.nwk")).readline().strip(), format=1)
    root = sp.get_tree_root()
    crowns = [c.name for c in root.get_children()]
    parent = {}
    for line in open(os.path.join(sim, "zombi", "T", "Events.tsv")).readlines()[1:]:
        t, ev, nodes = line.rstrip("\n").split("\t")
        if ev == "S":
            p, c1, c2 = nodes.split(";")
            parent[c1] = parent[c2] = p
    paths = []
    for c in crowns:
        path, x = [], c
        while x != root.name:
            path.append(x)
            if x not in parent:
                raise RuntimeError("lineage %s has no parent below MRCA %s" % (x, root.name))
            x = parent[x]
        paths.append(set(path))
    return crowns, paths


def main():
    sim = os.path.abspath(sys.argv[1])
    crowns, (pa, pb) = stems(sim)
    famdir = os.path.join(sim, "zombi", "G", "Gene_families")
    rows = []
    for r in read_tsv(os.path.join(sim, "sample", "truth.tsv")):
        fam = r["family"]
        origin, flag = "-", 0
        evs = [l.rstrip("\n").split("\t") for l in open(os.path.join(famdir, fam + "_events.tsv")).readlines()[1:]]
        for t, ev, nodes in evs:
            if ev == "O":
                origin = "A" if nodes in pa else "B" if nodes in pb else "-"
        if origin != "-":
            src, dst = (pa, pb) if origin == "A" else (pb, pa)
            for t, ev, nodes in evs:
                if ev == "T":
                    h = nodes.split(";")
                    if h[0] in src and h[4] in dst:
                        flag = 1
                        break
        rows.append((fam, origin, flag))
    with open(os.path.join(sim, "sample", "stem_transfers.tsv"), "w") as f:
        f.write("family\torigin_stem\tstem_to_stem\n")
        for r in rows:
            f.write("%s\t%s\t%d\n" % r)
    log("stems %s (%d, %d lineages): %d families originated on a stem, %d stem-to-stem transferred"
        % (crowns, len(pa), len(pb), sum(r[1] != "-" for r in rows), sum(r[2] for r in rows)))


if __name__ == "__main__":
    main()
