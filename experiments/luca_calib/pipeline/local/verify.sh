#!/usr/bin/env bash
# Verify the sealed inputs before a run.
#
# Usage: verify.sh [logfile]     (appends to logfile if given; always prints)
#
#  1. sha256 of the four prereg files (v1-v4) must equal the hashes in docs/prereg/HASHES.txt.
#  2. sha256 of every file under pipeline/ (except MANIFEST.sha256, __pycache__, .DS_Store) must equal
#     pipeline/MANIFEST.sha256, and the manifest must list exactly those files. The coordinator writes
#     and seals the manifest, e.g.:
#       cd pipeline && find . -type f ! -name MANIFEST.sha256 ! -path '*__pycache__*' ! -name .DS_Store \
#           | LC_ALL=C sort | xargs shasum -a 256 > MANIFEST.sha256
# Exit 0 only if both pass. All hashes are written to the log.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPE="$(cd "$HERE/.." && pwd)"
EXP="$(cd "$PIPE/.." && pwd)"
REPO="$(cd "$EXP/../.." && pwd)"
LOG="${1:-/dev/null}"
out() { echo "$*" | tee -a "$LOG"; }
fail=0

out "== verify $(date '+%Y-%m-%d %H:%M:%S')"
out "-- prereg (against docs/prereg/HASHES.txt)"
for f in docs/prereg/luca_calibration.md docs/prereg/luca_calibration_v2.md docs/prereg/luca_calibration_v3.md docs/prereg/luca_calibration_v4.md; do
  have=$(shasum -a 256 "$REPO/$f" | awk '{print $1}')
  want=$(awk -v p="$f" '$2==p {print $1}' "$REPO/docs/prereg/HASHES.txt" | tail -1)
  if [ -n "$want" ] && [ "$have" = "$want" ]; then out "OK   $have  $f"; else out "FAIL $have  $f (HASHES.txt: ${want:-missing})"; fail=1; fi
done

out "-- pipeline (against pipeline/MANIFEST.sha256)"
cd "$PIPE"
current=$(find . -type f ! -name MANIFEST.sha256 ! -path '*__pycache__*' ! -name .DS_Store | LC_ALL=C sort | xargs shasum -a 256)
echo "$current" | tee -a "$LOG" >/dev/null
if [ ! -f MANIFEST.sha256 ]; then
  out "FAIL pipeline/MANIFEST.sha256 missing (the coordinator seals it)"; fail=1
else
  if diff <(echo "$current" | awk '{print $2, $1}' | LC_ALL=C sort) <(awk '{print $2, $1}' MANIFEST.sha256 | LC_ALL=C sort) >> "$LOG" 2>&1; then
    out "OK   pipeline matches MANIFEST.sha256 ($(echo "$current" | wc -l | tr -d ' ') files; manifest sha256 $(shasum -a 256 MANIFEST.sha256 | awk '{print $1}'))"
  else
    out "FAIL pipeline differs from MANIFEST.sha256:"
    diff <(echo "$current" | awk '{print $2, $1}' | LC_ALL=C sort) <(awk '{print $2, $1}' MANIFEST.sha256 | LC_ALL=C sort) | tee -a "$LOG" || true
    fail=1
  fi
fi
[ "$fail" = 0 ] && out "verify: PASS" || out "verify: FAIL"
exit "$fail"
