#!/usr/bin/env bash
# K4 (prereg v5d) on AWS. Run from ~/luca_calib after k3/setup_remote.sh. Lanes in parallel, resumable via .done.
set -uo pipefail
PY=~/mamba/envs/phylo/bin/python; P=~/luca_calib/pipeline; R=~/luca_calib/results/k4; mkdir -p "$R"
BASE=(--set genome.initial_genome_size=200 --set genome.loss=1.0 --set genome.duplication=0.2 --set genome.origination=40 --set seed=1)
step() { local lane=$1 name=$2; shift 2; [ -f "$R/$name.done" ] && return 0
  echo "[$(date '+%F %T')] start $name" >> "$R/$lane.log"; local t0=$SECONDS
  nice -n 10 "$@" >> "$R/$lane.log" 2>&1; local rc=$?
  if [ $rc -eq 0 ] || { [ $rc -eq 3 ] && [[ $name == *ale* ]]; }; then
    echo -e "$name\t$((SECONDS-t0))\trc$rc" >> "$R/timings.tsv"; touch "$R/$name.done"
    echo "[$(date '+%F %T')] done $name $((SECONDS-t0))s rc$rc" >> "$R/$lane.log"
  else echo "[$(date '+%F %T')] FAILED $name rc$rc" >> "$R/$lane.log"; return 1; fi; }
truecell() { local tag=$1 n=$2 t=$3 w=$4; local d=$R/$tag/sim
  step $tag ${tag}_simulate $PY $P/simulate.py $d $P/configs/v3_base.json --force --su-workers $w "${BASE[@]}" \
    --set genome.transfer=$t --set sampling.n_per_domain=$n --set species_tree.total_lineages=$((5*n)) &&
  step $tag ${tag}_ale_true $PY $P/run_ale.py $d --trees true --workers $w --no-nice &&
  step $tag ${tag}_score_true $PY $P/score.py $d --run ale_true --out-dir $R/$tag/score --quiet; }
LANES="${LANES:-n160 n320 w80}"
for l in $LANES; do case $l in
  n160) truecell n160 160 0.4 4 & ;;
  n320) truecell n320 320 0.4 4 & ;;
  w80) { truecell w80 80 0.8 8 &&
         step w80 w80_infer $PY $P/infer_trees.py $R/w80/sim --workers 8 &&
         step w80 w80_ale_inf $PY $P/run_ale.py $R/w80/sim --trees inferred --workers 8 --no-nice &&
         step w80 w80_score_inf $PY $P/score.py $R/w80/sim --run ale_inferred --out-dir $R/w80/score --quiet; } & ;;
esac; done
wait; echo "[$(date '+%F %T')] K4 ALL DONE" >> "$R/main.log"
