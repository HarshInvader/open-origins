#!/usr/bin/env bash
# K5 (prereg v6) on the AWS machine, from ~/luca_calib. Builds each world from the Linux K3 true-tree
# run, runs ALE on the new families only (kept families reuse their uml_rec), refits O_R and scores.
# Usage: CELLS="1:0:N 1:1:N 3:4:N ..." W=8 bash k5/run_k5.sh      (seed:lambda:N, matched cells only)
set -uo pipefail
PY=~/mamba/envs/phylo/bin/python; P=~/luca_calib/pipeline; K=~/luca_calib/k5; R=~/luca_calib/results/k5
mkdir -p "$R"; W=${W:-8}
src() { case $1 in 1) echo ~/luca_calib/results/k2/n80_t0.4/sim ;; *) echo ~/luca_calib/results/k3/s$1/sim ;; esac; }
step() { local name=$1; shift; [ -f "$R/$name.done" ] && return 0
  echo "[$(date '+%F %T')] start $name" >> "$R/k5.log"; local t0=$SECONDS
  nice -n 10 "$@" >> "$R/$name.log" 2>&1; local rc=$?
  if [ $rc -eq 0 ] || { [ $rc -eq 3 ] && [[ $name == *ale* ]]; }; then
    echo -e "$name\t$((SECONDS-t0))\trc$rc" >> "$R/timings.tsv"; touch "$R/$name.done"
    echo "[$(date '+%F %T')] done $name $((SECONDS-t0))s rc$rc" >> "$R/k5.log"
  else echo "[$(date '+%F %T')] FAILED $name rc$rc" >> "$R/k5.log"; return 1; fi; }
world() { local tag=$1 s0=$2; shift 2; local d=$R/$tag
  step ${tag}_build $PY -I $K/stemsim.py build $s0 $d "$@" &&
  step ${tag}_ale $PY $P/run_ale.py $d --trees true --workers $W --no-nice &&
  step ${tag}_score $PY $P/score.py $d --run ale_true --out-dir $R/score_$tag --quiet; }
# seed 1's Linux ale_true was lost with the first K3 machine (DEVIATIONS 14): redo it here (same inputs, Linux ALE)
d1=$(src 1); [ -f $d1/ale_true/.linux ] || { step s1_src_ale_true $PY $P/run_ale.py $d1 --trees true --workers $W --no-nice &&
  touch $d1/ale_true/.linux && step s1_src_score_true $PY $P/score.py $d1 --run ale_true --out-dir $R/score_s1_src --quiet; }
for s in ${CTRL_SEEDS:-1 3}; do world s${s}_ctrl $(src $s) --n-stem 0 --lam 0 --seed $s; done
world s1_rootctrl $(src 1) --n-stem 0 --lam 0 --seed 1 --rootctrl
for c in ${CELLS:-}; do IFS=: read s lam n <<< "$c"; world s${s}_lam${lam} $(src $s) --n-stem $n --lam $lam --seed $s; done
echo "[$(date '+%F %T')] K5 ALL DONE" >> "$R/k5.log"
