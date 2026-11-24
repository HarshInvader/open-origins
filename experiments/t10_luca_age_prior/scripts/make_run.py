#!/usr/bin/env python3
"""Build one MCMCtree run directory for T10 (LUCA age vs maximum bound and rate prior).

Writes cache/runs/<name>/ with a control file, a tree file and (for usedata=2) a
copy of in.BV. Inputs come from raw/ (untrusted; read as text, never executed).

Variants (see docs/prereg/t10_luca_age_prior.md):
  R0   published settings
  P1   root maximum U(4.520) and LUCA maximum B{3.347,4.520,...} -> 6.0 (the plan's wording);
       with --p1-scope all, also the two other 4.520 maxima (TG-OXYPHOTOBACTERIA, TG-EUKARYA-MITO)
  P2h  rate prior mean halved:  rgene_gamma 2 2.5 -> 2 5
  P2d  rate prior mean doubled: rgene_gamma 2 2.5 -> 2 1.25

Usage:
  python3 -I make_run.py --variant R0 --clock GBM --usedata 2 --chain 1 \
      [--burnin 100000 --sampfreq 1000 --nsample 20000] [--seed N]

Nothing here reads MCMCtree output.
"""
import argparse
import hashlib
import pathlib
import re
import shutil

HERE = pathlib.Path(__file__).resolve().parent.parent  # experiments/t10_luca_age_prior
RAW = HERE / "raw"
PAML = HERE / "cache" / "paml" / "paml-4.10.7"

TREE = RAW / "00_data_formatting__01_inp_data__LUCAdup_246sp_allcb_calib_MCMCtree.tree"
INBV = RAW / "01_PAML__00_CODEML__out_CODEML__Hessian__1__in.BV"
ALN = RAW / "01_PAML__02_MCMCtree__dummy_aln__dummy_aln.aln"

CLOCK = {"GBM": 3, "ILN": 2, "CLK": 1}
RGENE = {"R0": "2 2.5", "P1": "2 2.5", "P2h": "2 5", "P2d": "2 1.25"}
P1_MAX = "6.0"

EXPECT_SHA = {  # pinned at LUCA-divtimes a2bf515fe3dddfc006b6d19e5444259857c62557
    INBV.name: "551789b8986c5ea4f909e0d9d56585a77cdd2289b714fdbd159ca2757a8cf672",
    TREE.name: "825e294e14bb31a35bfad914f6bc945275e0d9747b64b88fe25f79717a108009",
}


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_inputs():
    for p in (TREE, INBV):
        if sha256(p) != EXPECT_SHA[p.name]:
            raise SystemExit(f"sha256 mismatch: {p.name}")


def tree_text(variant, scope="luca_root"):
    t = TREE.read_text()
    # sanity: exactly four 4.520 maxima (root U + three B{...,4.520,...}) in the published tree
    n_root = t.count("'U(4.520,1e-300)'")
    n_b = len(re.findall(r"B\{[0-9.]+,4\.520,", t))
    if (n_root, n_b) != (1, 3):
        raise SystemExit(f"unexpected tree: root U count {n_root}, 4.520 B-maxima {n_b}")
    if variant == "P1":
        t = t.replace("'U(4.520,1e-300)'", f"'U({P1_MAX},1e-300)'")
        luca = "[#1 B{3.347,4.520,1e-300,1e-300}]"
        if t.count(luca) != 1:
            raise SystemExit("LUCA calibration string not found exactly once")
        t = t.replace(luca, luca.replace("4.520", P1_MAX))
        if scope == "all":
            t = re.sub(r"(B\{[0-9.]+,)4\.520,", rf"\g<1>{P1_MAX},", t)
            assert "4.520" not in t
    return t


CTL = """          seed = {seed}
       seqfile = {aln}
      treefile = tree.tree
      mcmcfile = mcmc.txt
       outfile = out.txt

         ndata = 1
       seqtype = 2
       usedata = {usedata_line}
         clock = {clock}

         model = 3
         alpha = 0.5
         ncatG = 4
    aaRatefile = {lgdat}

     cleandata = 0

       BDparas = 1 1 0.1
   rgene_gamma = {rgene}
  sigma2_gamma = 1 10

         print = 1
        burnin = {burnin}
      sampfreq = {sampfreq}
       nsample = {nsample}

duplication = 1
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=sorted(RGENE), required=True)
    ap.add_argument("--clock", choices=sorted(CLOCK), required=True)
    ap.add_argument("--usedata", type=int, choices=[0, 2], required=True)
    ap.add_argument("--chain", type=int, default=1)
    ap.add_argument("--burnin", type=int, default=100000)
    ap.add_argument("--sampfreq", type=int, default=1000)
    ap.add_argument("--nsample", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--tag", default="")
    ap.add_argument("--p1-scope", choices=["luca_root", "all"], default="luca_root")
    a = ap.parse_args()
    check_inputs()

    name = f"{a.variant}_{a.clock}_ud{a.usedata}_c{a.chain}{a.tag}"
    out = HERE / "cache" / "runs" / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "tree.tree").write_text(tree_text(a.variant, a.p1_scope))
    if a.usedata == 2:
        shutil.copyfile(INBV, out / "in.BV")
        usedata_line = "2 in.BV"
    else:
        usedata_line = "0"
    seed = a.seed if a.seed is not None else 1000 + 97 * a.chain
    (out / "mcmctree.ctl").write_text(CTL.format(
        seed=seed, aln=ALN, usedata_line=usedata_line, clock=CLOCK[a.clock],
        lgdat=PAML / "dat" / "lg.dat", rgene=RGENE[a.variant],
        burnin=a.burnin, sampfreq=a.sampfreq, nsample=a.nsample))
    print(out)


if __name__ == "__main__":
    main()
