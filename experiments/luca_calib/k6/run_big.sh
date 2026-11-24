#!/usr/bin/env bash
# OPS-2: large families, same IQ-TREE command as pipeline/infer_trees.py minus -redo, so a run cut off by the
# time budget resumes from IQ-TREE's checkpoint next call. Caller holds compute.lock.origins.
# Usage: bash k6/run_big.sh <full simdir> <family list> <main work simdir> <budget seconds>
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; EXP="$(cd "$HERE/.." && pwd)"
IQ="$HOME/mamba/envs/phylo/bin/iqtree3"; FULL="$1"; LIST="$2"; MAIN="$3"; BUDGET="$4"
BIG="$(dirname "$MAIN")/big"; DONE="$BIG/trees"; mkdir -p "$DONE"; S=$SECONDS
while read -r f; do
  [ -z "$f" ] && continue
  [ -f "$MAIN/ale_inferred/uml_rec/S.nwk_ale_fam_${f}.ale.uml_rec" ] && continue
  [ -f "$DONE/$f.trees" ] && continue
  left=$((BUDGET - (SECONDS - S))); [ $left -lt 300 ] && { echo "budget used; stop before $f"; break; }
  mkdir -p "$BIG/$f"
  echo "[$(date '+%F %T')] big $f start (budget ${left}s)" | tee -a "$MAIN/run_k6.log"
  perl -e 'alarm shift; exec @ARGV' "$left" taskpolicy -b nice -n 20 "$IQ" -s "$FULL/sample/fasta/$f.fasta" -m LG+F+G4 -B 1000 --wbtl -T 1 \
     --prefix "$BIG/$f/$f" -seed 1 -quiet; rc=$?
  if [ $rc -eq 0 ] && [ -f "$BIG/$f/$f.contree" ] && [ -f "$BIG/$f/$f.ufboot" ]; then
    cp "$BIG/$f/$f.ufboot" "$DONE/$f.trees"; echo "[$(date '+%F %T')] big $f done" | tee -a "$MAIN/run_k6.log"
  else
    echo "[$(date '+%F %T')] big $f stopped rc=$rc (resumes from checkpoint)" | tee -a "$MAIN/run_k6.log"; break
  fi
done < "$LIST"
