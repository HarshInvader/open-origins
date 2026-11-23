"""Recompute Wehbi 2024 LUCA/post-LUCA ratio from Dataset S2 (clan table) to get unrounded values.
Mirrors AncientAminoAcidUsageAnalysis.R lines 96-101 (colWeightedMeans weighted by Clan_Conlength).
Stdlib only. Touches only the code-order side; no abundance data is read here.
Usage: python -I wehbi_recompute.py sd02.csv out.tsv"""
import sys, csv, collections
rows = list(csv.DictReader(open(sys.argv[1])))
print(collections.Counter(r['Clan_ancestor'] for r in rows))
aa = list('ARNDCQEGHILKMFPSTWYV')
def wm(lab):
    s = [r for r in rows if r['Clan_ancestor'] == lab]
    W = sum(float(r['Clan_Conlength']) for r in s)
    return {a: sum(float(r[a]) * float(r['Clan_Conlength']) for r in s) / W for a in aa}, len(s)
L, nL = wm('LUCA'); P, nP = wm('postLUCA'); pre, npre = wm('preLUCA')
print('n clans LUCA', nL, 'postLUCA', nP, 'preLUCA', npre)
with open(sys.argv[2], 'w') as f:
    f.write('aa\tLUCA_over_postLUCA_recomputed\tpreLUCA_over_postLUCA_recomputed\n')
    for a in aa:
        f.write(f'{a}\t{L[a]/P[a]:.6f}\t{pre[a]/P[a]:.6f}\n')
print(open(sys.argv[2]).read())
