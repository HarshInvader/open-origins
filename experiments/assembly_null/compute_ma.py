"""Compute MA (assembly-theory 0.7.0), MW, HA, LZ for D2 molecules + validation sets.
Resumable: appends to out/ma_cache.jsonl keyed by canonical SMILES.
Usage: .venv/bin/python -I compute_ma.py <raw_dir> <out_dir>
"""
import sys, os, json, zlib, glob, random, multiprocessing as mp
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors
RDLogger.DisableLog('rdApp.*')

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
CACHE = os.path.join(OUT, 'ma_cache.jsonl')
ALLOWED = {'C', 'N', 'O', 'S', 'P', 'F', 'Cl', 'Br', 'I'}
WINDOW = set(range(4, 11)) | set(range(14, 18))
TIMEOUT_MS = 60000


def clean(mol):
    if mol is None:
        return None
    if len(Chem.GetMolFrags(mol)) != 1:
        return None
    syms = {a.GetSymbol() for a in mol.GetAtoms()}
    if not syms <= ALLOWED or 'C' not in syms:
        return None
    for a in mol.GetAtoms():
        a.SetIsotope(0)
    Chem.RemoveStereochemistry(mol)
    return mol


def feats(mol):
    smi = Chem.MolToSmiles(mol, isomericSmiles=False)
    return dict(smiles=smi, HA=mol.GetNumHeavyAtoms(),
                MW=Descriptors.ExactMolWt(mol),
                LZ=len(zlib.compress(smi.encode(), 9)))


def ma_job(smi):
    import assembly_theory as at
    m = Chem.MolFromSmiles(smi)
    mb = Chem.MolToMolBlock(m)
    try:
        r = at.index_search(mb, timeout=TIMEOUT_MS, parallel_str='none')
        return smi, int(r[0]), r[2] is None
    except Exception as e:  # noqa
        return smi, None, False


def main():
    rows = []
    # biotic: Rhea
    rh = pd.read_csv(os.path.join(RAW, 'rhea/rhea-chebi-smiles.tsv'), sep='\t', header=None, names=['id', 'smi'])
    for cid, s in zip(rh.id, rh.smi):
        if not isinstance(s, str) or '*' in s:
            continue
        m = clean(Chem.MolFromSmiles(s))
        if m is None:
            continue
        f = feats(m)
        if f['HA'] in WINDOW:
            rows.append(dict(set='rhea', label=1, id=cid, ref_ma=None, **f))
    # abiotic: GDB13/17 (+ validation sets)
    for setname, lab in [('gdb13_1201', 0), ('gdb17_200', 0), ('coconut_55', -1), ('checks', -1)]:
        d = os.path.join(RAW, 'daymude/data', setname)
        ref = pd.read_csv(os.path.join(d, 'ma-index.csv'))
        for fn, ma in zip(ref.file_name, ref.assembly_idx):
            m = Chem.MolFromMolFile(os.path.join(d, fn), sanitize=True)
            if m is None:
                print('unparsed', setname, fn); continue
            m0 = m
            f = feats(m0)
            # validation: compute MA on the ORIGINAL mol block (no cleaning) to compare with reference
            rows.append(dict(set=setname, label=lab, id=fn, ref_ma=int(ma),
                             keep=clean(Chem.Mol(m)) is not None, **f))
    # Marshall Reaxys subsample (validation only): 300 random with HA<=25
    rx = pd.read_csv(os.path.join(RAW, 'marshall/Figure_2-_MA_in_Chemical_Space/ma_mw_subsampled_by_mw.csv'))
    cand = []
    for sid, inchi, pa in zip(rx.substanceid, rx.inchi, rx.pa):
        m = Chem.MolFromInchi(inchi) if isinstance(inchi, str) else None
        if m is None or m.GetNumHeavyAtoms() > 25 or len(Chem.GetMolFrags(m)) != 1:
            continue
        Chem.RemoveStereochemistry(m)
        cand.append(dict(set='reaxys', label=-1, id=sid, ref_ma=int(pa), **feats(m)))
    random.Random(0).shuffle(cand)
    rows += cand[:300]
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, 'molecules.csv'), index=False)
    print(df.groupby('set').size())

    done = {}
    if os.path.exists(CACHE):
        for line in open(CACHE):
            r = json.loads(line); done[r['smiles']] = r
    todo = sorted(set(df.smiles) - set(done), key=len)
    print('MA to compute:', len(todo), 'cached:', len(done), flush=True)
    with mp.Pool(2) as pool, open(CACHE, 'a') as fh:
        for i, (smi, ma, to) in enumerate(pool.imap_unordered(ma_job, todo, chunksize=8)):
            fh.write(json.dumps(dict(smiles=smi, MA=ma, timeout=to)) + '\n')
            if i % 500 == 0:
                fh.flush(); print(i, flush=True)


if __name__ == '__main__':
    main()
