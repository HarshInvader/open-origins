#!/usr/bin/env bash
# LUCA calibration pilot on this laptop (prereg v3). Checkpointed and idempotent: each stage writes
# results/<stage>.done and is skipped when the marker exists; rerun the script to resume.
#
# Usage: WORKERS=3 run_pilot.sh            (WORKERS: default 3, capped at 3 (Origins cap))
#
# Refuses to start (and stops between stages) unless the shared compute lock is held by us:
#   $COMPUTE_LOCK/owner (default: the Origins lock, open-citizen-science/.local/compute.lock.origins) exists and starts
#   with "origins". This script never takes or removes the lock.
# Every heavy command runs under `taskpolicy -b nice -n 20`.
#
# Stages (outputs under experiments/luca_calib/results/):
#   build_ale   ext/ale -> ext/ale_build/bin/{ALEobserve,ALEml_undated}   (local/build_ale.sh, make -j1)
#   verify      local/verify.sh: prereg hashes vs HASHES.txt, pipeline vs MANIFEST.sha256 (every run)
#   ale_smoke   smoke_a-sized simulation (configs/smoke_a.json), run_ale.py --trees true, scored (printed)
#   fit         fit.py (stage F) on configs/v3_base.json -> fit/fit.json, fit/fit_config.json
#   seqscale    seqscale.py on fit_config.json -> seqscale/seqscale.json, seqscale/pilot_config.json
#   pilot       timing pilot at (L*, T*), seed 1: simulate, infer_trees, run_ale (inferred, true), score.
#               Scores go to results/pilot_unopened/ and are NOT printed. Wall time per sub-stage in
#               results/timings.tsv.
# Log: results/run_pilot.log. Progress: results/status.txt (rewritten after every stage).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPE="$(cd "$HERE/.." && pwd)"
EXP="$(cd "$PIPE/.." && pwd)"
RES="${RESULTS_DIR:-$EXP/results}"
LOCK_OWNER="${COMPUTE_LOCK:-$EXP/../../../open-citizen-science/.local/compute.lock.origins}/owner"
PY="$HOME/mamba/envs/phylo/bin/python"
NICE=(taskpolicy -b nice -n 20)

WORKERS="${WORKERS:-3}"
case "$WORKERS" in ''|*[!0-9]*) echo "WORKERS must be a positive integer" >&2; exit 2;; esac
[ "$WORKERS" -lt 1 ] && { echo "WORKERS must be >= 1" >&2; exit 2; }
[ "$WORKERS" -gt 3 ] && WORKERS=3

mkdir -p "$RES"
LOG="$RES/run_pilot.log"
STATUS="$RES/status.txt"
TIMES="$RES/timings.tsv"
[ -f "$TIMES" ] || printf "stage\tseconds\tworkers\tfinished\n" > "$TIMES"

mem_wait() {  # laptop rule: wait while free memory < 20% before starting a chunk
  local p
  while p=$(memory_pressure 2>/dev/null | tail -1 | sed -E 's/[^0-9]*([0-9]+)%.*/\1/') && [ -n "$p" ] && [ "$p" -lt 20 ]; do
    echo "[$(date '+%H:%M:%S')] free memory ${p}% < 20%; waiting" >&2; sleep 60
  done
}
say() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

lock_ok() { [ -f "$LOCK_OWNER" ] && head -c 7 "$LOCK_OWNER" | grep -q '^origins'; }
need_lock() {
  if ! lock_ok; then
    say "compute lock not held by origins ($LOCK_OWNER); stopping before stage '$1'"
    write_status "stopped: lock not held (before $1)"
    exit 3
  fi
}

STAGES=(build_ale verify ale_smoke fit seqscale pilot)
write_status() {
  {
    echo "updated $(date '+%Y-%m-%d %H:%M:%S')  workers $WORKERS  $1"
    for s in "${STAGES[@]}"; do
      if [ -f "$RES/$s.done" ]; then echo "$s done $(cat "$RES/$s.done")"; else echo "$s pending"; fi
    done
  } > "$STATUS"
}

# run_stage <name> <function>: skip if done, else check lock, time it, mark done
run_stage() {
  local name="$1" fn="$2"
  if [ -f "$RES/$name.done" ]; then say "skip $name (done)"; return 0; fi
  need_lock "$name"; mem_wait
  say "start $name"
  write_status "running $name"
  local t0=$SECONDS
  if "$fn" >> "$LOG" 2>&1; then
    local dt=$((SECONDS - t0))
    printf "%s\t%d\t%d\t%s\n" "$name" "$dt" "$WORKERS" "$(date '+%Y-%m-%d %H:%M:%S')" >> "$TIMES"
    echo "${dt}s $(date '+%Y-%m-%d %H:%M:%S')" > "$RES/$name.done"
    say "done $name in ${dt}s"
    write_status "after $name"
  else
    say "FAILED $name (see $LOG)"
    write_status "FAILED $name"
    exit 1
  fi
}

# timed sub-step inside a stage (own marker so a rerun resumes inside the stage)
sub() {
  local name="$1"; shift
  if [ -f "$RES/sub_$name.done" ]; then echo "skip sub-step $name"; return 0; fi
  need_lock "$name"; mem_wait
  local t0=$SECONDS
  echo "+ $*"
  "$@" || return 1
  local dt=$((SECONDS - t0))
  printf "%s\t%d\t%d\t%s\n" "$name" "$dt" "$WORKERS" "$(date '+%Y-%m-%d %H:%M:%S')" >> "$TIMES"
  echo "${dt}s" > "$RES/sub_$name.done"
}

# ---------------------------------------------------------------- stages
st_build_ale() { bash "$HERE/build_ale.sh" build; }

st_verify() { bash "$HERE/verify.sh" "$LOG"; }

st_ale_smoke() {
  local d="$RES/ale_smoke"
  mkdir -p "$d"
  sub ale_smoke_simulate "${NICE[@]}" "$PY" "$PIPE/simulate.py" "$d/sim" "$PIPE/configs/smoke_a.json" --force || return 1
  sub ale_smoke_run_ale "${NICE[@]}" "$PY" "$PIPE/run_ale.py" "$d/sim" --trees true --workers "$WORKERS" || return 1
  "$PY" "$PIPE/score.py" "$d/sim" --run ale_true | tee "$d/score.txt"
  "$PY" - "$d/sim/ale_true/or_fit.json" <<'EOF'
import json, sys
f = json.load(open(sys.argv[1]))
print("ALE smoke: O_R %.3f, %d families, %s" % (f["O_R"], f["n_families"], f["root_check"]))
EOF
}

st_fit() {
  "${NICE[@]}" "$PY" "$PIPE/fit.py" "$RES/fit" --config "$PIPE/configs/v3_base.json" --workers "$WORKERS"
}

st_seqscale() {
  "${NICE[@]}" "$PY" "$PIPE/seqscale.py" "$RES/seqscale" --config "$RES/fit/fit_config.json"
}

st_pilot() {
  local d="$RES/pilot" sim="$RES/pilot/sim"
  mkdir -p "$d" "$RES/pilot_unopened"
  cp "$RES/seqscale/pilot_config.json" "$d/config.json"
  sub pilot_simulate "${NICE[@]}" "$PY" "$PIPE/simulate.py" "$sim" "$d/config.json" --set seed=1 --su-workers "$WORKERS" --force || return 1
  sub pilot_infer_trees "${NICE[@]}" "$PY" "$PIPE/infer_trees.py" "$sim" --workers "$WORKERS" || return 1
  sub pilot_run_ale_inferred "${NICE[@]}" "$PY" "$PIPE/run_ale.py" "$sim" --trees inferred --workers "$WORKERS" || return 1
  sub pilot_run_ale_true "${NICE[@]}" "$PY" "$PIPE/run_ale.py" "$sim" --trees true --workers "$WORKERS" || return 1
  # sealed: written to pilot_unopened/, nothing printed
  sub pilot_score "$PY" "$PIPE/score.py" "$sim" --run ale_inferred --run ale_true --quiet --out-dir "$RES/pilot_unopened" || return 1
  echo "pilot scores written to $RES/pilot_unopened (not opened)"
}

# ---------------------------------------------------------------- main
need_lock "start"
say "run_pilot: workers $WORKERS, results $RES, lock owner: $(head -1 "$LOCK_OWNER")"
run_stage build_ale st_build_ale
need_lock verify
say "verify (runs every time)"
if ! st_verify >> "$LOG" 2>&1; then say "verify FAILED; stopping"; write_status "FAILED verify"; exit 1; fi
[ -f "$RES/verify.done" ] || echo "pass $(date '+%Y-%m-%d %H:%M:%S')" > "$RES/verify.done"
write_status "after verify"
run_stage ale_smoke st_ale_smoke
run_stage fit st_fit
run_stage seqscale st_seqscale
run_stage pilot st_pilot
say "all stages done"
write_status "all done"
