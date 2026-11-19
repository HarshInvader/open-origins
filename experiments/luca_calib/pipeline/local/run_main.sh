#!/usr/bin/env bash
# LUCA calibration main grid, arm L and arm H on this laptop (prereg v2 change 3, v3, v4 A-D).
# Checkpointed and idempotent: every step writes results/main/<step>.done and is skipped when present.
#
# Usage: N_PER_DOMAIN=40 WORKERS=3 run_main.sh
#   N_PER_DOMAIN  required: 40 or 30, the coordinator's v3 decision from the timing pilot.
#   WORKERS       default 3, capped at 3 (Origins cap).
# Needs results/fit/fit.json and results/seqscale/pilot_config.json from run_pilot.sh.
# Same lock rule as run_pilot.sh: runs only while
#   $COMPUTE_LOCK/owner (default: the Origins lock, open-citizen-science/.local/compute.lock.origins) starts with "origins",
# re-checked before every step; never takes or removes the lock. Heavy commands: taskpolicy -b nice -n 20.
#
# Simulations (results/main/sims/<name>/):
#   main_t{0.5,1,2}_s{1,2,3}  transfer = factor * T* at L*, seeds 1-3 (9 simulations)
#       simulate, stem_transfers, infer_trees, run_ale inferred, run_ale true, score
#   control_s1                planted control: transfer 0, no family/lineage rate heterogeneity,
#       simulate, stem_transfers, run_ale true, score
#   armL_s{11,12,13}          arm L (v4 A): Zombi Gu, loss x1.6 in the fast clade, transfer T*,
#       simulate, stem_transfers, infer_trees, run_ale inferred, score
#   arm H (v4 B)              run_alerax_h.py --trees inferred on armL_s11-13 and main_t1_s1-3, score
# Log results/main/run_main.log, status results/main/status.txt, times results/main/timings.tsv.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPE="$(cd "$HERE/.." && pwd)"
EXP="$(cd "$PIPE/.." && pwd)"
RES="${RESULTS_DIR:-$EXP/results}"
OUT="$RES/main"
LOCK_OWNER="${COMPUTE_LOCK:-$EXP/../../../open-citizen-science/.local/compute.lock.origins}/owner"
PY="$HOME/mamba/envs/phylo/bin/python"
NICE=(taskpolicy -b nice -n 20)

WORKERS="${WORKERS:-3}"
case "$WORKERS" in ''|*[!0-9]*) echo "WORKERS must be a positive integer" >&2; exit 2;; esac
[ "$WORKERS" -lt 1 ] && { echo "WORKERS must be >= 1" >&2; exit 2; }
[ "$WORKERS" -gt 3 ] && WORKERS=3
case "${N_PER_DOMAIN:-}" in 40|30) ;; *) echo "set N_PER_DOMAIN to 40 or 30 (v3 rule, decided from the pilot)" >&2; exit 2;; esac

mkdir -p "$OUT/sims" "$OUT/configs"
LOG="$OUT/run_main.log"; STATUS="$OUT/status.txt"; TIMES="$OUT/timings.tsv"
[ -f "$TIMES" ] || printf "step\tseconds\tworkers\tfinished\n" > "$TIMES"
mem_wait() {  # laptop rule: wait while free memory < 20% before starting a chunk
  local p
  while p=$(memory_pressure 2>/dev/null | tail -1 | sed -E 's/[^0-9]*([0-9]+)%.*/\1/') && [ -n "$p" ] && [ "$p" -lt 20 ]; do
    echo "[$(date '+%H:%M:%S')] free memory ${p}% < 20%; waiting" >&2; sleep 60
  done
}
say() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
lock_ok() { [ -f "$LOCK_OWNER" ] && head -c 7 "$LOCK_OWNER" | grep -q '^origins'; }
status() { { echo "updated $(date '+%Y-%m-%d %H:%M:%S') workers $WORKERS n_per_domain $N_PER_DOMAIN: $1";
             ls "$OUT"/*.done 2>/dev/null | wc -l | xargs echo "steps done:"; } > "$STATUS"; }

# step <name> <command...>: skip if done; else check lock, run (log), time, mark done; stop on failure
step() {
  local name="$1"; shift
  [ -f "$OUT/$name.done" ] && return 0
  if ! lock_ok; then say "lock not held by origins; stopping before $name"; status "stopped (lock) before $name"; exit 3; fi
  mem_wait; say "start $name"; status "running $name"
  local t0=$SECONDS
  echo "+ $*" >> "$LOG"
  if "$@" >> "$LOG" 2>&1; then
    local dt=$((SECONDS - t0))
    printf "%s\t%d\t%d\t%s\n" "$name" "$dt" "$WORKERS" "$(date '+%Y-%m-%d %H:%M:%S')" >> "$TIMES"
    echo "${dt}s" > "$OUT/$name.done"; say "done $name in ${dt}s"; status "after $name"
  else
    say "FAILED $name (see $LOG)"; status "FAILED $name"; exit 1
  fi
}

# mkconfig <out.json> <key=value>... : pilot_config.json with overrides (dotted keys, JSON values)
mkconfig() {
  "$PY" - "$RES/seqscale/pilot_config.json" "$RES/fit/fit.json" "$@" <<'EOF'
import json, sys
cfg = json.load(open(sys.argv[1])); fit = json.load(open(sys.argv[2])); out = sys.argv[3]
env = {"TSTAR": fit["T_star"], "LSTAR": fit["L_star"],
       "NREF": next(p for p in fit["points"] if p["i"] == fit["best_point"])["stats"]["median_genome_families"]}
for kv in sys.argv[4:]:
    k, v = kv.split("=", 1)
    for name, val in env.items():
        v = v.replace(name, repr(val))
    v = json.loads(v) if not any(c in v for c in "*+") else eval(v, {})
    d = cfg
    for p in k.split(".")[:-1]:
        d = d.setdefault(p, {})
    d[k.split(".")[-1]] = v
json.dump(cfg, open(out, "w"), indent=2, sort_keys=True)
EOF
}

# ---- preflight
lock_ok || { say "compute lock not held by origins; not starting"; exit 3; }
for f in "$RES/fit/fit.json" "$RES/seqscale/pilot_config.json"; do [ -f "$f" ] || { say "missing $f (run run_pilot.sh first)"; exit 2; }; done
say "run_main: workers $WORKERS, n_per_domain $N_PER_DOMAIN, results $OUT"
bash "$HERE/verify.sh" "$LOG" > /dev/null || { say "verify FAILED; stopping"; status "FAILED verify"; exit 1; }

sim_steps() {  # sim_steps <name> <config> <inferred:0/1> <true:0/1>
  local n="$1" c="$2" inf="$3" tru="$4" s="$OUT/sims/$1"
  step "${n}_simulate" "${NICE[@]}" "$PY" "$PIPE/simulate.py" "$s" "$c" --su-workers "$WORKERS" --force
  step "${n}_stem" "$PY" "$PIPE/stem_transfers.py" "$s"
  if [ "$inf" = 1 ]; then
    step "${n}_infer" "${NICE[@]}" "$PY" "$PIPE/infer_trees.py" "$s" --workers "$WORKERS"
    step "${n}_ale_inferred" "${NICE[@]}" "$PY" "$PIPE/run_ale.py" "$s" --trees inferred --workers "$WORKERS"
  fi
  [ "$tru" = 1 ] && step "${n}_ale_true" "${NICE[@]}" "$PY" "$PIPE/run_ale.py" "$s" --trees true --workers "$WORKERS"
  step "${n}_score" "$PY" "$PIPE/score.py" "$s"
}

# ---- main grid (9) and planted control
for f in 0.5 1 2; do
  for seed in 1 2 3; do
    n="main_t${f}_s${seed}"; c="$OUT/configs/$n.json"
    [ -f "$c" ] || mkconfig "$c" "seed=$seed" "sampling.n_per_domain=$N_PER_DOMAIN" "genome.transfer=$f*TSTAR"
    sim_steps "$n" "$c" 1 1
  done
done
c="$OUT/configs/control_s1.json"
[ -f "$c" ] || mkconfig "$c" "seed=1" "sampling.n_per_domain=$N_PER_DOMAIN" "genome.transfer=0" \
  "genome.family_rate_sigma=0" "sequence.lineage_sigma=0" "sequence.family_sigma=0"
sim_steps control_s1 "$c" 0 1

# ---- arm L (v4 A)
for seed in 11 12 13; do
  n="armL_s${seed}"; c="$OUT/configs/$n.json"
  [ -f "$c" ] || mkconfig "$c" "seed=$seed" "sampling.n_per_domain=$N_PER_DOMAIN" "genome.transfer=1*TSTAR" \
    'genome.mode="Gu"' "genome.gu_reference_genes=1*NREF" "lineage_loss.multiplier=1.6"
  sim_steps "$n" "$c" 1 0
done

# ---- arm H (v4 B)
for n in armL_s11 armL_s12 armL_s13 main_t1_s1 main_t1_s2 main_t1_s3; do
  step "${n}_alerax_H" "${NICE[@]}" "$PY" "$PIPE/run_alerax_h.py" "$OUT/sims/$n" --trees inferred --np "$WORKERS"
  step "${n}_score_H" "$PY" "$PIPE/score.py" "$OUT/sims/$n" --run alerax_H_inferred
done
say "all steps done"; status "all done"
