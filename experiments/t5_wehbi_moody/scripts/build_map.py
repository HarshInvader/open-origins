#!/usr/bin/env python3
"""T5: stream cog2uniprot2pfam.csv out of the figshare zip (never unpacked to disk)
and write a compact edge list: one row per (COG, Pfam) pair with the number of
distinct UniProt accessions that carry the pair, plus one row per COG with its size.

Run:  python3 -I scripts/build_map.py <zip> <out_edges.tsv> <out_cogsize.tsv>
No PP value is read here.
"""
import sys, io, csv, zipfile, hashlib, collections

def main(zpath, out_edges, out_cogs):
    z = zipfile.ZipFile(zpath)
    name = 'cog2uniprot2pfam.csv'
    pair = collections.defaultdict(set)      # (cog, pfam) -> uniprot accs
    cogprot = collections.defaultdict(set)   # cog -> uniprot accs
    n = 0
    with z.open(name) as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding='utf-8', newline=''))
        header = next(rd)
        assert header == ['cog_id', 'uniprot_acc', 'pfamA_acc'], header
        for cog, acc, pf in rd:
            n += 1
            pair[(cog, pf)].add(acc)
            cogprot[cog].add(acc)
    with open(out_edges, 'w') as f:
        f.write('# source rows: %d ; (cog,pfam) pairs: %d\n' % (n, len(pair)))
        f.write('cog_id\tpfamA_acc\tn_uniprot\n')
        for (cog, pf) in sorted(pair):
            f.write('%s\t%s\t%d\n' % (cog, pf, len(pair[(cog, pf)])))
    with open(out_cogs, 'w') as f:
        f.write('cog_id\tn_uniprot\tn_pfam\n')
        npf = collections.Counter(c for c, _ in pair)
        for cog in sorted(cogprot):
            f.write('%s\t%d\t%d\n' % (cog, len(cogprot[cog]), npf[cog]))
    print('rows', n, 'pairs', len(pair), 'cogs', len(cogprot),
          'pfams', len({p for _, p in pair}))

if __name__ == '__main__':
    main(*sys.argv[1:4])
