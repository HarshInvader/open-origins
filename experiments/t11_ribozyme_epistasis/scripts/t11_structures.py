"""T11 structure gate (prereg docs/prereg/t11_ribozyme_epistasis.md).  Reads PDB coordinates only.

Builds, for each ribozyme, the map from mutational-scan positions (1-based on the deposit's wild type) to
residues of one structure, and from that the contact labels:

  canonical pair   cis Watson-Crick G-C, A-U or G-U wobble, by an H-bond geometry rule (CANON below)
  helical          not canonical, but within index distance 2 of a canonical pair (|i-a| + |j-b| <= 2)
  tertiary contact any heavy atoms within 4.0 A, |i - j| >= 4, not canonical, not helical
  non-contact      no heavy atoms within 4.0 A, |i - j| >= 4, not canonical, not helical

No activity value, count or epistasis value is read here.

Usage:  python -I t11_structures.py <experiments/t11_ribozyme_epistasis dir>
Writes data/t11_contacts.json and prints the gate table.
"""
import sys, os, json, shlex, hashlib
import numpy as np

D = os.path.abspath(sys.argv[1])
CONTACT_A = 4.0
MIN_SEP = 4
MIN_CONTACTS = 15

# Wild types: the deposit's most-read sequence in each counts pickle (equal to the per-position consensus; see gate)
WT = {
    "CPEB3": "GGGGGCCACAGCAGAAGCGTTCACGTCGCGGCCCCTGTCAGATTCTGGTGAATCTGCGAATTCTGCTGT",
    "HDV": "GGCCGGCATGGTCCCAGCCTCCTCGCTGGCGCCGGCTGGGCAACATTCCGAGGGGACCGTCCCCTCGGTAATGGCGAATGGGACCCA",
    "Hammerhead": "ACCGGATGTGCTTTCCGGTCTGATGAGTCCGTGAGGACGAAACAG",
    "Hairpin": "GTCCTCTTTCACGTGCGCGTGAAAGAGAGAAGTGAACCAGAGAAACACACGTTGTGGTATATTACCTGGTA",
    "Hatchet": "TTACTGATATCAGTGACAAACATGTGGGGCTTATATCTAATCTTCGGATTAGTATTAGTGCAGACGTTAAAACCATGT",
    "Twister": "AACACTGCCAATGCCGGTCCCAAGCCCGGATAAAAGTGGAGGGGGCGG",
}

# One structure per ribozyme.  blocks = (wt_from, wt_to, auth_asym_id, auth_seq_id of wt_from): wt position
# p maps to residue auth_from + (p - wt_from) of that chain.  Blocks were read off the sequences by hand (prereg,
# "Structures"); only positions whose structure residue has the same base are mapped, the rest are dropped.
STRUCT = {
    # 1DRZ: product of the genomic HDV ribozyme; P4 is shortened and capped by a U1A-binding loop (146-159)
    "HDV": {"pdb": "1DRZ", "blocks": [(1, 45, "B", 101), (72, 84, "B", 160)]},
    # 2QUW chain B: 3' product of the full-length sTRSV hammerhead; G12A (our 39) is a mismatch and is dropped
    "Hammerhead": {"pdb": "2QUW", "blocks": [(1, 45, "B", 13)]},
    # 1M5K: four-way-junction hairpin; chain A is the substrate strand (G+1 = A13), chain B the ribozyme strand;
    # our hairpin loop 51-53 is the U1A arm B30-51 in the crystal
    "Hairpin": {"pdb": "1M5K", "blocks": [(1, 7, "A", 13), (24, 50, "B", 3), (54, 71, "B", 52)]},
    # 6JQ5: product dimer that swaps 3' ends at C68/G69 (Zheng et al. 2019); the authors' monomer A' is chain A
    # up to auth 68 plus chain B from auth 69.  Our 7-9 have no clear partner in the crystal's 7-12 and are left out;
    # our UUCG loop 43-46 is GAAA in 6JQ5.  Our 64-67 (auth 67-70, the palindromic ACGU of L2) form the crystal's
    # intermolecular duplex across the swap point, so they are not in a monomer conformation and are left out
    "Hatchet": {"pdb": "6JQ5", "blocks": [(1, 6, "A", 1), (10, 46, "A", 13), (47, 63, "A", 50), (68, 78, "B", 71)]},
    # 4OJI: O. sativa twister; auth 17-18 (our 11-12) are not modelled
    "Twister": {"pdb": "4OJI", "blocks": [(1, 48, "A", 7)]},
    # 7QR3 chain C: chimpanzee CPEB3; P4 capped by a U1A loop (42-56).  Reported only (see DECIDING)
    "CPEB3": {"pdb": "7QR3", "blocks": [(1, 41, "C", 1), (55, 67, "C", 57)]},
}
DECIDING = ["HDV", "Hammerhead", "Hairpin", "Hatchet", "Twister"]   # CPEB3 is reported only (prereg D2)

PARENT = {"A": "A", "C": "C", "G": "G", "U": "U", "GTP": "G", "A2M": "A", "IU": "U", "CCC": "C",
          "5BU": "U", "OMG": "G", "OMC": "C", "OMU": "U", "PSU": "U", "UMS": "U", "CBV": "C", "GDP": "G",
          "MIA": "A", "1MA": "A", "DA": "A", "DC": "C", "DG": "G", "DT": "U", "DU": "U", "A23": "A",
          "C2E": "G", "G46": "G", "CSL": "C", "5MC": "C", "2MG": "G", "M2G": "G", "7MG": "G", "H2U": "U",
          "AP7": "A", "6MZ": "A", "U8U": "U", "UR3": "U", "RSQ": "C", "0C": "C", "0G": "G", "0U": "U", "0A": "A"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_atom_site(path):
    """Minimal mmCIF reader for the _atom_site loop (one-line rows).  Returns list of dicts."""
    lines = open(path, encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "loop_" and i + 1 < len(lines) and lines[i + 1].startswith("_atom_site."):
            i += 1
            cols = []
            while lines[i].startswith("_atom_site."):
                cols.append(lines[i].split(".", 1)[1].strip())
                i += 1
            rows = []
            while i < len(lines) and not lines[i].startswith(("#", "loop_", "_")):
                t = shlex.split(lines[i], posix=True) if '"' in lines[i] or "'" in lines[i] else lines[i].split()
                if len(t) == len(cols):
                    rows.append(dict(zip(cols, t)))
                i += 1
            return rows
        i += 1
    raise SystemExit("no _atom_site loop in " + path)


def residues(path, parts):
    """Ordered residues of the chosen molecule: list of (auth_asym, auth_seq, ins, base, {atom: xyz})."""
    rows = read_atom_site(path)
    model = min(int(r.get("pdbx_PDB_model_num", "1")) for r in rows)
    out = []
    for asym, lo, hi in parts:
        cur, order = {}, []
        for r in rows:
            if int(r.get("pdbx_PDB_model_num", "1")) != model or r["auth_asym_id"] != asym:
                continue
            if r["type_symbol"] in ("H", "D"):
                continue
            if r["label_alt_id"] not in (".", "?", "A"):
                continue
            comp = r["auth_comp_id"]
            if comp not in PARENT:
                continue
            s = int(r["auth_seq_id"])
            if not lo <= s <= hi:
                continue
            key = (asym, s, r["pdbx_PDB_ins_code"])
            if key not in cur:
                cur[key] = (PARENT[comp], comp, {})
                order.append(key)
            cur[key][2][r["auth_atom_id"].strip('"')] = np.array([float(r["Cartn_x"]), float(r["Cartn_y"]), float(r["Cartn_z"])])
        for k in order:
            if "C1'" in cur[k][2]:                     # a nucleotide with its sugar modelled
                out.append((k[0], k[1], k[2], cur[k][0], cur[k][1], cur[k][2]))
    return out


CANON = {  # (purine-ish first base, second base): list of (atom on first, atom on second); all must be <= HB_A
    ("G", "C"): [("N1", "N3"), ("O6", "N4"), ("N2", "O2")],
    ("A", "U"): [("N1", "N3"), ("N6", "O4")],
    ("G", "U"): [("N1", "O2"), ("O6", "N3")],
}
HB_A = 3.5


RING = ("N1", "C2", "N3", "C4", "C5", "C6", "N7", "C8", "N9")
MAX_STAGGER = 2.0      # A; stacked neighbours sit about 3.4 A apart along the base normal


def plane(r):
    x = np.array([r[5][a] for a in RING if a in r[5]])
    c = x.mean(0)
    n = np.linalg.svd(x - c)[2][-1]
    return c, n


def is_canonical(r1, r2):
    """cis Watson-Crick G-C, A-U or G-U wobble: every listed H-bond <= HB_A, and the base centroids offset
    by < MAX_STAGGER along each base normal (excludes stacked bases whose atoms happen to be close)."""
    for (x, y), bonds in CANON.items():
        for p, q in ((r1, r2), (r2, r1)):
            if p[3] == x and q[3] == y:
                if all(a in p[5] and b in q[5] and np.linalg.norm(p[5][a] - q[5][b]) <= HB_A for a, b in bonds):
                    (c1, n1), (c2, n2) = plane(p), plane(q)
                    if abs(np.dot(c2 - c1, n1)) < MAX_STAGGER and abs(np.dot(c2 - c1, n2)) < MAX_STAGGER:
                        return True
    return False


def build(name):
    cfg = STRUCT[name]
    path = os.path.join(D, "raw", "pdb", cfg["pdb"] + ".cif")
    chains = sorted({b[2] for b in cfg["blocks"]})
    res = residues(path, [(c, -999, 9999) for c in chains])
    byid = {(r[0], r[1]): r for r in res if r[2] in (".", "?", "")}
    wt = WT[name].replace("T", "U")
    mapping, mism, unmod = {}, [], []
    for a, b, ch, af in cfg["blocks"]:
        for p in range(a, b + 1):
            r = byid.get((ch, af + p - a))
            if r is None:
                unmod.append(p)
            elif r[3] != wt[p - 1]:
                mism.append((p, wt[p - 1], ch, r[1], r[4]))
            else:
                if p in mapping:
                    raise SystemExit("%s: position %d mapped twice" % (name, p))
                mapping[p] = r
    pos = sorted(mapping)
    # mapped stretches, for the record
    runs, start = [], pos[0]
    for a, b in zip(pos, pos[1:] + [None]):
        if b != a + 1:
            runs.append((start, a, mapping[start][0], mapping[start][1], mapping[a][1])); start = b
    # distances
    xyz = {p: np.array(list(mapping[p][5].values())) for p in pos}
    L = len(wt)
    dmin = np.full((L + 1, L + 1), np.nan)
    for a in pos:
        for b in pos:
            if a < b:
                dd = np.sqrt(((xyz[a][:, None, :] - xyz[b][None, :, :]) ** 2).sum(-1)).min()
                dmin[a, b] = dmin[b, a] = dd
    canon = [(a, b) for a in pos for b in pos if a < b and is_canonical(mapping[a], mapping[b])]
    cset = set(canon)
    helical = set()
    for a in pos:
        for b in pos:
            if a < b and (a, b) not in cset and any(abs(a - x) + abs(b - y) <= 2 for x, y in canon):
                helical.add((a, b))
    tert, non = [], []
    for a in pos:
        for b in pos:
            if a < b and b - a >= MIN_SEP and (a, b) not in cset and (a, b) not in helical:
                (tert if dmin[a, b] <= CONTACT_A else non).append((a, b))
    return {
        "pdb": cfg["pdb"], "blocks": cfg["blocks"], "block_mismatches": mism, "block_unmodelled": unmod, "cif_sha256": sha256(path), "wt": WT[name], "length": L,
        "n_mapped": len(pos), "unmapped": [p for p in range(1, L + 1) if p not in mapping],
        "mapped_runs": [{"wt_from": r[0], "wt_to": r[1], "chain": r[2], "auth_from": r[3], "auth_to": r[4]} for r in runs],
        "canonical_pairs": canon, "helical_pairs": sorted(helical),
        "tertiary_contacts": tert, "non_contacts": non,
        "canonical_pairs_sep_ge4": [p for p in canon if p[1] - p[0] >= MIN_SEP],
        "mindist": {"%d-%d" % (a, b): round(float(dmin[a, b]), 3) for a in pos for b in pos if a < b},
    }


def main():
    out, table = {}, []
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import safe_pickle
    stems = safe_pickle.load(os.path.join(D, "raw", "gitlab", "files", "Data_Structures_ribo_structures.p"))
    for name in ["HDV", "Hammerhead", "Hairpin", "Hatchet", "Twister", "CPEB3"]:
        r = build(name)
        key = {"Hammerhead": "Hammerhead"}.get(name, name)
        dep = sorted({tuple(p) for k, v in stems.items() if k[:-2] == key for p in v})
        found = set(map(tuple, r["canonical_pairs"]))
        mapped = set(range(1, r["length"] + 1)) - set(r["unmapped"])
        dep_mapped = [p for p in dep if p[0] in mapped and p[1] in mapped]
        r["deposit_stem_pairs"] = dep
        r["deposit_stem_pairs_mapped"] = len(dep_mapped)
        r["deposit_stem_pairs_recovered"] = sum(p in found for p in dep_mapped)
        r["canonical_not_in_deposit_stems"] = sorted(found - set(dep))
        r["deciding"] = name in DECIDING
        r["kept"] = name in DECIDING and len(r["tertiary_contacts"]) >= MIN_CONTACTS
        out[name] = r
        table.append((name, r["pdb"], r["length"], r["n_mapped"], len(r["canonical_pairs"]), len(r["canonical_pairs_sep_ge4"]),
                      len(r["helical_pairs"]), len(r["tertiary_contacts"]), len(r["non_contacts"]),
                      "%d/%d" % (r["deposit_stem_pairs_recovered"], r["deposit_stem_pairs_mapped"]), r["kept"]))
    os.makedirs(os.path.join(D, "data"), exist_ok=True)
    with open(os.path.join(D, "data", "t11_contacts.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("ribozyme pdb len mapped canon canon_sep>=4 helical tertiary noncontact deposit_stems_recovered kept")
    for t in table:
        print(*t)
    for name, r in out.items():
        print("\n==", name, r["pdb"], "runs:", [(x["wt_from"], x["wt_to"], x["chain"], x["auth_from"], x["auth_to"]) for x in r["mapped_runs"]])
        print("   block mismatches (dropped):", r["block_mismatches"], " unmodelled:", r["block_unmodelled"])
        print("   unmapped:", r["unmapped"])
        print("   canonical pairs not in deposit stems:", r["canonical_not_in_deposit_stems"])


if __name__ == "__main__":
    main()
