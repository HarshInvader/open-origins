#!/usr/bin/env bash
# K2 (prereg v5 + v5a): ALE on true gene trees across tip counts, at T* and 2T*.
# Calls the sealed pipeline scripts unchanged. Resumable: each step writes <out>/<step>.done.
# Takes and releases compute.lock.origins itself; refuses to start if the lock is held.
# Usage: WORKERS=3 bash k2/run_k2.sh   (v5b: K2_ORIG=40 K2_NS="20 40 80")
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXP="$(cd "$HERE/.." && pwd)"
PIPE="$EXP/pipeline"
OUT="$EXP/results/k2"
PY="$HOME/mamba/envs/phylo/bin/python"
LOCK="$EXP/../../../open-citizen-science/.local/compute.lock.origins"
NICE=(taskpolicy -b nice -n 20)
WORKERS="${WORKERS:-3}"; [ "$WORKERS" -gt 3 ] && WORKERS=3
NS="${K2_NS:-20 40 80}"
TS="${K2_TS:-0.2 0.4}"
mkdir -p "$OUT"; LOG="$OUT/run_k2.log"; TIMES="$OUT/timings.tsv"
[ -f "$TIMES" ] || printf "step\tseconds\tfinished\n" > "$TIMES"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

mkdir "$LOCK" 2>/dev/null || { echo "compute.lock.origins is held: $(cat "$LOCK/owner" 2>/dev/null)" >&2; exit 3; }
echo "origins luca_calib K2 true-tree scaling (task#32) $(date -u +%FT%TZ)" > "$LOCK/owner"
trap 'rm -rf "$LOCK"' EXIT

mem_wait() {
  local p
  while p=$(memory_pressure 2>/dev/null | tail -1 | sed -E 's/[^0-9]*([0-9]+)%.*/\1/') && [ -n "$p" ] && [ "$p" -lt 20 ]; do
    say "free memory ${p}% < 20%; waiting"; sleep 60
  done
}
step() {  # step <name> <cmd...>
  local name="$1"; shift
  [ -f "$OUT/$name.done" ] && { say "skip $name"; return 0; }
  mem_wait; say "start $name"; echo "+ $*" >> "$LOG"
  local t0=$SECONDS
  if "$@" >> "$LOG" 2>&1; then
    printf "%s\t%d\t%s\n" "$name" $((SECONDS - t0)) "$(date '+%F %T')" >> "$TIMES"
    echo "$((SECONDS - t0))s" > "$OUT/$name.done"; say "done $name in $((SECONDS - t0))s"
  else
    say "FAILED $name"; exit 1
  fi
}

bash "$PIPE/local/verify.sh" >> "$LOG" 2>&1 || { say "verify failed"; exit 1; }

COMMON=(--set genome.initial_genome_size=200 --set genome.loss=1.0 --set genome.duplication=0.2)

# 1. origination, fitted once on a small tree (genome sizes only)
step orig_fit "${NICE[@]}" "$PY" "$PIPE/fit.py" "$OUT/orig_fit" --config "$PIPE/configs/v3_base.json" \
  --L 1 --TL 0.2 --o-start 2 --workers 1 "${COMMON[@]}" \
  --set species_tree.total_lineages=100 --set sampling.n_per_domain=20
if [ -n "${K2_ORIG:-}" ]; then ORIG="$K2_ORIG"; else ORIG=$("$PY" -c "import json,sys; print(json.load(open(sys.argv[1]))['origination_star'])" "$OUT/orig_fit/fit.json"); fi
say "origination (per genome per unit time) = $ORIG"

# 2. cells, smallest first
for n in $NS; do
  for t in $TS; do
    c="n${n}_t${t}"; d="$OUT/$c/sim"
    step "${c}_simulate" "${NICE[@]}" "$PY" "$PIPE/simulate.py" "$d" "$PIPE/configs/v3_base.json" --force \
      --su-workers "$WORKERS" "${COMMON[@]}" --set genome.transfer="$t" --set genome.origination="$ORIG" \
      --set sampling.n_per_domain="$n" --set species_tree.total_lineages=$((5 * n)) --set seed=1
    step "${c}_ale_true" "${NICE[@]}" "$PY" "$PIPE/run_ale.py" "$d" --trees true --workers "$WORKERS"
    step "${c}_score" "$PY" "$PIPE/score.py" "$d" --run ale_true --out-dir "$OUT/$c/score" --quiet
  done
done
say "K2 finished"
