#!/usr/bin/env bash
# K7 full planted test on a free GitHub-hosted Linux runner (coordinator approval 2026-11-26: no spend,
# public repo only, no secrets on the runner, hash check first, small artefacts, each job resumable).
# Run from the repo root. Needs LUCA_ALE_BIN (Linux ALE build) and python3 with numpy + ete3.
#   run_job.sh verify            code hashes against runner/code.sha256 (every job runs this first)
#   run_job.sh alecheck          Linux ALE reproduces 12 stored AWS Linux seed-3 reconciliations byte for byte
#   run_job.sh bg1               Linux re-run of seed 1's kept background families (prereg: "present or re-run")
#   run_job.sh rung <seed> <m>   build one rung (checked against expected_build.sha256), then ALE on all of it
#   run_job.sh report <seed>     merge the downloaded parts and write report_s<seed>.json
set -euo pipefail
E=experiments; R=$E/k7_realism_bound/runner; W=${K7_WORK:-k7work}; PY=${PY:-python3}
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
NW=$(nproc 2>/dev/null || echo 2)

verify() { (cd $E && sha256sum -c ../$R/code.sha256) || { echo "CODE HASH MISMATCH: stop"; exit 2; }; }

build() {  # build <seed> <m...> into $W/s<seed>, then check the result against the laptop build
  local s=$1; shift
  $PY -I $E/k7_realism_bound/k7_planted.py build $R/inputs/s$s $W/s$s --seed $s --m "$@" --n 250 --cap 0
  (cd $W && sha256sum -c --ignore-missing <(grep -v '/trees$' ../$R/expected_build.sha256 | grep " s$s/")) \
    || { echo "BUILD MISMATCH: stop"; exit 3; }
  for m in "$@"; do
    got=$(cd $W/s$s/m$m/trees && ls | LC_ALL=C sort | while read f; do printf '%s ' "$f"; sha256sum "$f" | cut -c1-64; done | sha256sum | cut -c1-64)
    want=$(grep " s$s/m$m/trees$" $R/expected_build.sha256 | cut -c1-64)
    [ "$got" = "$want" ] || { echo "TREE DIGEST MISMATCH s$s m$m: stop"; exit 3; }
  done
  echo "build s$s $* matches the laptop build"
}

case "${1:-}" in
  verify) verify ;;
  alecheck)
    verify; d=$W/alecheck; rm -rf $d; mkdir -p $d/out/uml_rec; cp $R/inputs/s3/alecheck/S.nwk $d/out/S.nwk
    $PY -I - "$R/inputs/s3/alecheck" "$d/out" <<'EOF'
import sys, os
sys.path.insert(0, "experiments/luca_calib/pipeline")
from run_ale import run_family
src, out = sys.argv[1], sys.argv[2]
for f in sorted(os.listdir(os.path.join(src, "true_trees"))):
    fam = f[:-4]
    print(run_family(fam, os.path.join(src, "true_trees", f), out, 100, 1, []), flush=True)
EOF
    (cd $d/out/uml_rec && while read h f; do echo "$h  S.nwk_ale_fam_$f.ale.uml_rec"; done < "$OLDPWD/$R/inputs/s3/alecheck/expected_uml_rec.sha256" | sha256sum -c) \
      || { echo "LINUX ALE DOES NOT REPRODUCE THE STORED K3 RECONCILIATIONS: stop"; exit 4; }
    echo "alecheck: 12 of 12 identical" ;;
  bg1)
    verify; src=$W/src_s1; mkdir -p $src; cp -R $R/inputs/s1/. $src/
    tar xzf $R/inputs/s1/kept_true_trees.tgz -C $src/sample
    mkdir -p $src/ale_true/uml_rec
    $PY -I - "$src" <<'EOF'
import sys, os
sys.path.insert(0, "experiments/luca_calib/pipeline")
from run_ale import run_family, write_species_tree
from concurrent.futures import ThreadPoolExecutor
src = sys.argv[1]; out = os.path.join(src, "ale_true")
write_species_tree(src, out)
fams = [l.strip() for l in open(os.path.join(src, "kept_multi.txt")) if l.strip()]
with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as ex:
    res = list(ex.map(lambda f: run_family(f, os.path.join(src, "sample", "true_trees", f + ".nwk"), out, 100, 1, []), fams))
bad = [r for r in res if r[1] not in ("ok", "done")]
print("bg1 families", len(res), "failed", len(bad), bad[:10], flush=True)
EOF
    $PY -I $E/k7_realism_bound/k7_planted.py background $src $W/s1 --seed 1
    mkdir -p parts/bg1; cp $W/s1/background.jsonl $W/s1/background_meta.json parts/bg1/ ;;
  rung)
    verify; s=$2; m=$3; build $s $m
    # resumable: records already returned by an earlier attempt of this job are reused
    [ -f parts/s$s-m$m/records.jsonl ] && cp parts/s$s-m$m/records.jsonl $W/s$s/m$m/records.jsonl || true
    $PY -I $E/k7_realism_bound/k7_planted.py ale $W/s$s --m $m --workers $NW --budget ${BUDGET:-18000}
    mkdir -p parts/s$s-m$m; cp $W/s$s/m$m/records.jsonl parts/s$s-m$m/ ;;
  report)
    verify; s=$2; build $s 1 10 50 150 600
    if [ "$s" = 3 ]; then cp $R/inputs/s3/background.jsonl $R/inputs/s3/background_meta.json $W/s3/;
    else cp parts/bg1/background.jsonl parts/bg1/background_meta.json $W/s1/; fi
    for m in 1 10 50 150 600; do cp parts/s$s-m$m/records.jsonl $W/s$s/m$m/records.jsonl; done
    mkdir -p out; $PY -I $E/k7_realism_bound/k7_planted.py report $W/s$s out/report_s$s.json ;;
  *) echo "usage: $0 verify|alecheck|bg1|rung <seed> <m>|report <seed>"; exit 1 ;;
esac
