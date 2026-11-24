"""T6 helper: compare the deposited COG sequence sets with the KO sequence sets (structure only; no PP is read).

Usage (single process; run under nice):
  python -I build_sets.py <experiments/t6_moody_ko_cog dir>

Reads, without unpacking, experiments/luca_calib/raw/moody/Supp_data.zip (Moody et al. 2024 deposit,
doi:10.6084/m9.figshare.24428659) and the KO -> modal COG column of Supplementary Data 1.
For each COG of Supplementary Data 2 it writes one row to data/cog_ko_sets.tsv:
  cog, n_kos, n_cog_seqs, n_union_ko_seqs, n_shared, sum_ko_seqs, trimmed_same
`trimmed_same` (single-KO COGs only) is 1 when the COG's trimmed alignment holds exactly the same
(sequence id, aligned sequence) pairs as the KO's trimmed alignment, else 0; "." for multi-KO COGs.
"""
import sys, os, csv, zipfile, collections

D = os.path.abspath(sys.argv[1])
EXP = os.path.dirname(D)
ZIP = os.path.join(EXP, "luca_calib", "raw", "moody", "Supp_data.zip")
SD1 = os.path.join(EXP, "t5_wehbi_moody", "raw", "moody_springer_esm", "41559_2024_2461_MOESM4_ESM.tsv")
SD2 = os.path.join(EXP, "t5_wehbi_moody", "raw", "moody_springer_esm", "41559_2024_2461_MOESM5_ESM.tsv")
G = "Supp_data/Gene_Fastas/"


def records(text):
    out, name, buf = {}, None, []
    for l in text.split("\n"):
        if l.startswith(">"):
            if name is not None:
                out[name] = "".join(buf)
            name, buf = l[1:].split()[0], []
        elif name is not None:
            buf.append(l.strip())
    if name is not None:
        out[name] = "".join(buf)
    return out


members = collections.defaultdict(list)
for r in csv.DictReader(open(SD1, encoding="utf-8"), delimiter="\t"):
    members[r["COG"]].append(r["KEGG_ko"])            # only the id columns are used
cogs = [r["COG"] for r in csv.DictReader(open(SD2, encoding="utf-8"), delimiter="\t")]
z = zipfile.ZipFile(ZIP)
rows = []
for c in cogs:
    cs = set(records(z.read(G + "COG_analysis/fasta/%s_duprem.fas" % c).decode()))
    u, tot = set(), 0
    for k in members[c]:
        ks = set(records(z.read(G + "Pure_sequences/%s.fasta" % k).decode()))
        tot += len(ks)
        u |= ks
    same = "."
    if len(members[c]) == 1:
        a = records(z.read(G + "COG_analysis/trimmed/%s_duprem_mafft_blsm30.fa" % c).decode())
        b = records(z.read(G + "Trimmed_Alignments/%s.fasta.mafft.blsm30_default" % members[c][0]).decode())
        same = "1" if a == b else "0"
    rows.append((c, len(members[c]), len(cs), len(u), len(cs & u), tot, same))
os.makedirs(os.path.join(D, "data"), exist_ok=True)
with open(os.path.join(D, "data", "cog_ko_sets.tsv"), "w", encoding="utf-8") as f:
    f.write("cog\tn_kos\tn_cog_seqs\tn_union_ko_seqs\tn_shared\tsum_ko_seqs\ttrimmed_same\n")
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
print("wrote", len(rows), "rows")
