#!/usr/bin/env python3
"""Time one MCMCtree run without looking at its output values.

Launches mcmctree in a prepared run directory under `taskpolicy -b nice -n 20`,
polls every few seconds, and records: wall time, the process's CPU time, and the
number of NEWLINES in mcmc.txt (one per stored sample). It never parses node ages,
never prints stdout lines (MCMCtree's progress lines carry running means of
node ages), and kills the run at --max-wall seconds.

Usage: python3 -I time_run.py <run_dir> --max-wall 780 --out timing.json
"""
import argparse
import json
import pathlib
import subprocess
import time

HERE = pathlib.Path(__file__).resolve().parent.parent
MCMCTREE = HERE / "cache" / "paml" / "paml-4.10.7" / "src" / "mcmctree"


def cpu_seconds(pid):
    r = subprocess.run(["ps", "-o", "time=", "-p", str(pid)], capture_output=True, text=True)
    s = r.stdout.strip()
    if not s:
        return None
    parts = s.replace("-", ":").split(":")
    secs = 0.0
    for p in parts:
        secs = secs * 60 + float(p)
    return secs


def count_lines(p):
    try:
        with open(p, "rb") as f:
            return f.read().count(b"\n")
    except FileNotFoundError:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--max-wall", type=float, default=780)
    ap.add_argument("--poll", type=float, default=3)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rd = pathlib.Path(a.run_dir).resolve()
    for f in ("mcmc.txt", "out.txt", "run.log"):
        (rd / f).unlink(missing_ok=True)
    log = open(rd / "run.log", "wb")
    t0 = time.time()
    proc = subprocess.Popen(["taskpolicy", "-b", "nice", "-n", "20", str(MCMCTREE), "mcmctree.ctl"],
                            cwd=rd, stdout=log, stderr=subprocess.STDOUT)
    # the child of taskpolicy/nice is exec'd in place, so proc.pid is mcmctree
    events = []  # (wall, cpu, samples) at each change in sample count
    last = -1
    killed = False
    cpu = None
    while proc.poll() is None:
        time.sleep(a.poll)
        c = cpu_seconds(proc.pid)
        cpu = c if c is not None else cpu
        n = max(count_lines(rd / "mcmc.txt") - 1, 0)  # minus header line
        if n != last:
            events.append({"wall_s": round(time.time() - t0, 2), "cpu_s": cpu, "samples": n})
            last = n
        if time.time() - t0 > a.max_wall:
            proc.kill()
            killed = True
            proc.wait()
            break
    wall = time.time() - t0
    log.close()
    text = (rd / "run.log").read_bytes().decode(errors="replace")
    err = [ln for ln in text.replace("\r", "\n").split("\n")
           if ("error" in ln.lower().split() or "not binary" in ln or "cannot" in ln.lower()) and len(ln) < 300]
    rec = {"run_dir": rd.name, "returncode": proc.returncode, "killed_at_limit": killed,
           "wall_s": round(wall, 1), "cpu_s_last": cpu, "events": events,
           "error_lines": err[:5], "finished_line_seen": "Time used" in text}
    pathlib.Path(a.out).write_text(json.dumps(rec, indent=1))
    print(json.dumps({k: rec[k] for k in ("run_dir", "returncode", "killed_at_limit", "wall_s",
                                          "cpu_s_last", "error_lines", "finished_line_seen")}))
    print("events:", [(e["wall_s"], e["cpu_s"], e["samples"]) for e in events])


if __name__ == "__main__":
    main()
