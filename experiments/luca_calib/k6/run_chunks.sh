#!/usr/bin/env bash
# OPS-4: the OPS-1 chunk wrapper as a committed script (it had been an inline loop on the old laptop).
# Runs the remaining 10-family chunks in order through the sealed k6/run_k6.sh, one chunk at a time, and
# starts a new chunk only while the elapsed time is under BUDGET (default 4200 s), so the harness's 2-hour
# limit never falls inside a chunk. A chunk is marked <chunk>.done only when every family in it has a
# uml_rec, so an interrupted chunk is simply re-run. Takes the lock once for the whole wrapper.
# Usage: bash k6/run_chunks.sh [budget seconds]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; EXP="$(cd "$HERE/.." && pwd)"
LOCK="$EXP/../../../open-citizen-science/.local/compute.lock.origins"
FULL="$EXP/results/k6/s65"; WORK="$EXP/results/k6/s65_run"; CH="$EXP/results/k6/chunks10"
BUDGET="${1:-4200}"; S=$SECONDS

if [ "${K6_HAVE_LOCK:-0}" != 1 ]; then
  mkdir "$LOCK" 2>/dev/null || { echo "compute.lock.origins is held: $(cat "$LOCK/owner" 2>/dev/null)" >&2; exit 3; }
  echo "origins luca_calib K6 chunks $(date -u +%FT%TZ)" > "$LOCK/owner"
  trap 'rm -rf "$LOCK"' EXIT
fi
export K6_HAVE_LOCK=1

for c in "$CH"/c[0-9][0-9][0-9]; do
  [ -f "$c.done" ] && continue
  left=$((BUDGET - (SECONDS - S)))
  [ $left -lt 600 ] && { echo "budget used; stop before $(basename "$c")"; break; }
  # skip a chunk that is already fully reconciled
  need=0
  while read -r f; do [ -z "$f" ] && continue
    [ -f "$WORK/ale_inferred/uml_rec/S.nwk_ale_fam_${f}.ale.uml_rec" ] || need=1
  done < "$c"
  if [ $need -eq 0 ]; then touch "$c.done"; echo "$(basename "$c") already complete"; continue; fi
  echo "[$(date -u +%FT%TZ)] chunk $(basename "$c") start (${left}s left in budget)"
  bash "$HERE/run_k6.sh" "$FULL" "$c" "$WORK" 10
  # mark done only if every family now has a uml_rec
  ok=1
  while read -r f; do [ -z "$f" ] && continue
    [ -f "$WORK/ale_inferred/uml_rec/S.nwk_ale_fam_${f}.ale.uml_rec" ] || ok=0
  done < "$c"
  if [ $ok -eq 1 ]; then touch "$c.done"; echo "[$(date -u +%FT%TZ)] $(basename "$c") done"
  else echo "[$(date -u +%FT%TZ)] $(basename "$c") incomplete; it will be re-run"; fi
done
echo "[$(date -u +%FT%TZ)] run_chunks done; uml_rec $(ls "$WORK/ale_inferred/uml_rec" | wc -l)"
