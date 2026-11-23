#!/usr/bin/env bash
# K6 (prereg v8): gene trees + ALE + Moody reweighting on a seeded family sample of a simdir, in batches,
# deleting tree files after each batch (laptop disk is small). Calls the sealed pipeline scripts unchanged.
# Resumable: finished families keep their uml_rec in <work>/ale_inferred/uml_rec and are skipped.
# Takes and releases compute.lock.origins itself; refuses to start if the lock is held by someone else.
# Usage: bash k6/run_k6.sh <full simdir> <family list file> <work simdir> [batch size, default 30]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP="$(cd "$HERE/.." && pwd)"
PIPE="$EXP/pipeline"
PY="$HOME/mamba/envs/phylo/bin/python"
LOCK="$EXP/../../../open-citizen-science/.local/compute.lock.origins"
NICE=(taskpolicy -b nice -n 20)
FULL="$1"; LIST="$2"; WORK="$3"; B="${4:-30}"
mkdir -p "$WORK/sample/fasta" "$WORK/ale_inferred/uml_rec"
LOG="$WORK/run_k6.log"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

if [ "${K6_HAVE_LOCK:-0}" != 1 ]; then
  mkdir "$LOCK" 2>/dev/null || { echo "compute.lock.origins is held: $(cat "$LOCK/owner" 2>/dev/null)" >&2; exit 3; }
  echo "origins luca_calib K6 $(basename "$WORK") $(date -u +%FT%TZ)" > "$LOCK/owner"
  trap 'rm -rf "$LOCK"' EXIT
fi

cp "$FULL/sample/species_tree.nwk" "$WORK/sample/"
disk_ok() {
  local free
  while free=$(df -g /System/Volumes/Data | awk 'NR==2{print $4}') && [ "$free" -lt 2 ]; do
    say "free disk ${free} GB < 2 GB; waiting 10 min"; sleep 600
  done
}
write_truth() {  # write_truth <family ids...>
  { printf "family\tn_genes\n"; for f in "$@"; do awk -F'\t' -v f="$f" '$1==f' "$FULL/sample/truth.tsv"; done; } > "$WORK/sample/truth.tsv"
}

ALL=(); while read -r f; do case "$f" in ""|\#*) ;; *) ALL+=("$f");; esac; done < "$LIST"
todo=()
for f in "${ALL[@]}"; do
  [ -f "$WORK/ale_inferred/uml_rec/S.nwk_ale_fam_${f}.ale.uml_rec" ] || [ -f "$WORK/done_single/$f" ] || grep -qx "$f" "$WORK/tree_failed.txt" 2>/dev/null || todo+=("$f")
done
say "families in list ${#ALL[@]}, to do ${#todo[@]}, batch $B"

for ((i = 0; i < ${#todo[@]}; i += B)); do
  batch=("${todo[@]:i:B}")
  disk_ok
  rm -rf "$WORK/sample/fasta" "$WORK/inferred" "$WORK/ale_inferred/fams"; mkdir -p "$WORK/sample/fasta"
  for f in "${batch[@]}"; do ln -s "$(cd "$FULL/sample/fasta" && pwd)/$f.fasta" "$WORK/sample/fasta/$f.fasta"; done
  write_truth "${batch[@]}"
  t0=$SECONDS
  infer() { "${NICE[@]}" "$PY" "$PIPE/infer_trees.py" "$WORK" --workers 3 --model LG+F+G4 --bootstraps 1000 --seed 1 >> "$LOG" 2>&1; }
  infer
  cp "$WORK/inferred/status.tsv" "$WORK/status_batch_$i.tsv" 2>/dev/null
  # IQ-TREE can fail on a transient full disk ("Cannot write to file"); retry failed families twice.
  # infer_trees.py clears inferred/ on start, so earlier trees are set aside and merged back.
  for attempt in 1 2; do
    failed=$(awk -F'\t' 'NR>1 && $2=="failed"{print $1}' "$WORK/inferred/status.tsv")
    [ -z "$failed" ] && break
    say "retry $attempt for families: $(echo $failed)"
    rm -rf "$WORK/inferred_keep"; mv "$WORK/inferred" "$WORK/inferred_keep"
    disk_ok; write_truth $failed; infer
    cp "$WORK/inferred/trees/"* "$WORK/inferred_keep/trees/" 2>/dev/null
    awk -F'\t' 'NR>1' "$WORK/inferred/status.tsv" | sed "s/^/retry$attempt\t/" >> "$WORK/status_batch_$i.tsv"
    rm -rf "$WORK/inferred_keep/iqtree"; mv "$WORK/inferred/status.tsv" "$WORK/inferred_keep/status.tsv"
    rm -rf "$WORK/inferred"; mv "$WORK/inferred_keep" "$WORK/inferred"
  done
  failed=$(awk -F'\t' 'NR>1 && $2=="failed"{print $1}' "$WORK/inferred/status.tsv")
  ok=(); for f in "${batch[@]}"; do case " $(echo $failed) " in *" $f "*) echo "$f" >> "$WORK/tree_failed.txt";; *) ok+=("$f");; esac; done
  [ -n "$failed" ] && say "tree inference failed after retries: $(echo $failed) (counted under G2)"
  write_truth "${ok[@]}"
  rm -rf "$WORK/inferred/iqtree"
  "${NICE[@]}" "$PY" "$PIPE/run_ale.py" "$WORK" --trees inferred --workers 3 >> "$LOG" 2>&1; rc=$?
  [ $rc -eq 0 ] || [ $rc -eq 3 ] || { say "run_ale failed rc=$rc on batch at $i"; exit 1; }
  mkdir -p "$WORK/done_single"
  if [ -f "$WORK/inferred/skipped_single_gene.txt" ]; then
    while read -r f; do [ -n "$f" ] && touch "$WORK/done_single/$f"; done < "$WORK/inferred/skipped_single_gene.txt"
  fi
  cp "$WORK/ale_inferred/run_meta.json" "$WORK/ale_meta_batch_$i.json"
  rm -rf "$WORK/inferred" "$WORK/ale_inferred/fams"
  say "batch $((i / B + 1)) (${#batch[@]} families) done in $((SECONDS - t0))s; uml_rec $(ls "$WORK/ale_inferred/uml_rec" | wc -l)"
done

# final reweighting over every uml_rec, with truth = the whole list
write_truth "${ALL[@]}"
mkdir -p "$WORK/inferred/trees"; for f in "${ALL[@]}"; do : > "$WORK/inferred/trees/$f.trees"; done  # run_ale checks existence only; --reweight-only reads uml_rec
"$PY" "$PIPE/run_ale.py" "$WORK" --trees inferred --reweight-only >> "$LOG" 2>&1
say "K6 $(basename "$WORK") finished: $(grep -c . "$WORK/ale_inferred/root_pp.tsv") lines in root_pp.tsv"
