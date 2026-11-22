#!/usr/bin/env bash
# K3 (prereg v5c) on the AWS machine: 4 lanes in parallel, each resumable via .done files. Run from ~/luca_calib.
set -uo pipefail
PY=~/mamba/envs/phylo/bin/python; P=~/luca_calib/pipeline; R=~/luca_calib/results/k3; mkdir -p "$R"
COMMON=(--set genome.initial_genome_size=200 --set genome.loss=1.0 --set genome.duplication=0.2 --set genome.transfer=0.4 --set genome.origination=40 --set sampling.n_per_domain=80 --set species_tree.total_lineages=400)
step() { local lane=$1 name=$2; shift 2; [ -f "$R/$name.done" ] && return 0
  echo "[$(date '+%F %T')] start $name" >> "$R/$lane.log"; local t0=$SECONDS
  nice -n 10 "$@" >> "$R/$lane.log" 2>&1; local rc=$?
  if [ $rc -eq 0 ] || { [ $rc -eq 3 ] && [[ $name == *ale* ]]; }; then
    echo -e "$name\t$((SECONDS-t0))\trc$rc" >> "$R/timings.tsv"; touch "$R/$name.done"
    echo "[$(date '+%F %T')] done $name $((SECONDS-t0))s rc$rc" >> "$R/$lane.log"
  else echo "[$(date '+%F %T')] FAILED $name rc$rc" >> "$R/$lane.log"; return 1; fi; }
inferred() { local lane=$1 tag=$2 d=$3 w=$4
  step $lane ${tag}_infer $PY $P/infer_trees.py $d --workers $w &&
  step $lane ${tag}_ale_inf $PY $P/run_ale.py $d --trees inferred --workers $w --no-nice &&
  step $lane ${tag}_score_inf $PY $P/score.py $d --run ale_inferred --out-dir $R/$tag/score --quiet; }
seed() { local s=$1 w=$2 d=$R/s$s/sim
  step s$s s${s}_simulate $PY $P/simulate.py $d $P/configs/v3_base.json --force --su-workers $w "${COMMON[@]}" --set seed=$s &&
  step s$s s${s}_ale_true $PY $P/run_ale.py $d --trees true --workers $w --no-nice &&
  step s$s s${s}_score_true $PY $P/score.py $d --run ale_true --out-dir $R/s$s/score --quiet &&
  inferred s$s s$s $d $w; }
bash $P/local/verify.sh > "$R/verify.log" 2>&1; echo "verify rc $?" >> "$R/verify.log"
inferred s1 s1 ~/luca_calib/results/k2/n80_t0.4/sim 12 &
seed 2 8 &
seed 3 8 &
inferred n40 n40 ~/luca_calib/results/k2/n40_t0.4/sim 4 &
wait; echo "[$(date '+%F %T')] K3 ALL DONE" >> "$R/main.log"
