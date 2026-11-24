#!/usr/bin/env bash
# OPS-2: reconcile already-finished tree files with the sealed run_ale.py in a side work dir, then copy uml_rec
# into the main work dir so run_k6.sh skips those families. Caller must hold compute.lock.origins.
# Usage: bash k6/ale_from_trees.sh <full simdir> <dir of <fam>.trees files> <main work simdir>
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; EXP="$(cd "$HERE/.." && pwd)"; PY="$HOME/mamba/envs/phylo/bin/python"
FULL="$1"; SRC="$2"; MAIN="$3"; SIDE="$(dirname "$MAIN")/s65_side"
rm -rf "$SIDE"; mkdir -p "$SIDE/sample/fasta" "$SIDE/inferred/trees"
cp "$FULL/sample/species_tree.nwk" "$SIDE/sample/"
fams=(); for t in "$SRC"/*.trees; do f=$(basename "$t" .trees); fams+=("$f"); done
"$PY" -I - "$FULL" "$SRC" "$SIDE" "$EXP/pipeline" "${fams[@]}" <<'PY'
import sys, os, shutil
full, src, side, pipe, fams = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
sys.path.insert(0, pipe)
from infer_trees import check_trees, read_fasta
ok = []
for f in fams:
    fa = os.path.join(full, "sample", "fasta", f + ".fasta")
    want = [n for n, _ in read_fasta(fa)]
    n, err = check_trees(os.path.join(src, f + ".trees"), want)
    if err or n == 0:
        print("SKIP", f, err, n); continue
    shutil.copy(os.path.join(src, f + ".trees"), os.path.join(side, "inferred", "trees", f + ".trees"))
    os.symlink(os.path.abspath(fa), os.path.join(side, "sample", "fasta", f + ".fasta")); ok.append(f)
truth = {l.split("\t")[0]: l for l in open(os.path.join(full, "sample", "truth.tsv")) if not l.startswith("family")}
with open(os.path.join(side, "sample", "truth.tsv"), "w") as fh:
    fh.write("family\tn_genes\n"); [fh.write(truth[f]) for f in ok]
print("ok", len(ok), "of", len(fams))
PY
taskpolicy -b nice -n 20 "$PY" "$EXP/pipeline/run_ale.py" "$SIDE" --trees inferred --workers 3 >> "$MAIN/run_k6.log" 2>&1 || { rc=$?; [ $rc -eq 3 ] || exit $rc; }
n=0; for u in "$SIDE"/ale_inferred/uml_rec/*.uml_rec; do [ -e "$u" ] || continue; cp "$u" "$MAIN/ale_inferred/uml_rec/"; n=$((n+1)); done
echo "[$(date '+%F %T')] OPS-2 salvage from $SRC: $n uml_rec copied" | tee -a "$MAIN/run_k6.log"
rm -rf "$SIDE"
