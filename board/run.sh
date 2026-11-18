#!/bin/bash
# Team compute gate: one compute job at a time, background priority, first come first served.
# Usage (from repo root): board/run.sh <command...>     e.g. board/run.sh .venv/bin/python -I experiments/x/run.py
# Takes a ticket, waits until it is the oldest live ticket and the lock is free, runs the command on efficiency
# cores at lowest priority, then releases the lock.
TEAM="${TEAM_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"  # folder holding every project (override with TEAM_DIR)
LOCK="$TEAM/.team-compute.lock"    # shared by all projects: one compute job at a time on this laptop
QUEUE="$TEAM/.team-compute.queue"  # one ticket file per waiting job, named <epoch>-<pid>
mkdir -p "$QUEUE"
TICKET="$QUEUE/$(printf '%012d-%08d' "$(date +%s)" $$)"
echo "$*" > "$TICKET"
trap 'rm -f "$TICKET"' EXIT
trap 'exit 130' INT TERM
while true; do
  for t in "$QUEUE"/*; do                                   # drop tickets whose job has died
    [ -e "$t" ] || continue
    p=$((10#${t##*-})); kill -0 "$p" 2>/dev/null || rm -f "$t"
  done
  head=$(ls "$QUEUE" | sort | head -1)
  if [ "$QUEUE/$head" = "$TICKET" ]; then
    pid=$(cat "$LOCK/pid" 2>/dev/null)
    if [ -d "$LOCK" ] && [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then rm -rf "$LOCK"; fi
    mkdir "$LOCK" 2>/dev/null && break
    echo "first in queue; compute lock held by pid ${pid:-?}: $(cat "$LOCK/cmd" 2>/dev/null); waiting 20s" >&2
  else
    n=$(ls "$QUEUE" | sort | awk -v me="${TICKET##*/}" '$0==me{print NR-1}')
    echo "queued behind $n job(s); next up: $(cat "$QUEUE/$head" 2>/dev/null); waiting 20s" >&2
  fi
  /bin/sleep 20
done
echo $$ > "$LOCK/pid"; echo "$*" > "$LOCK/cmd"
rm -f "$TICKET"
trap 'rm -rf "$LOCK"; rm -f "$TICKET"' EXIT
taskpolicy -b nice -n 20 "$@"
