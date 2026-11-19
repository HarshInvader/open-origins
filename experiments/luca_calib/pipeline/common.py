"""Shared paths and small helpers for the LUCA calibration pipeline."""
import os
import sys
import json
import time
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
ZOMBI_DIR = os.path.join(EXP, "ext", "zombi")
HOME = os.path.expanduser("~")
PHYLO_PY = os.environ.get("LUCA_PHYLO_PY", os.path.join(HOME, "mamba/envs/phylo/bin/python"))
IQTREE = os.environ.get("LUCA_IQTREE", os.path.join(HOME, "mamba/envs/phylo/bin/iqtree3"))
ALERAX = os.environ.get("LUCA_ALERAX", os.path.join(HOME, "mamba/envs/alerax/bin/alerax"))


def log(msg):
    print(time.strftime("[%H:%M:%S] ") + msg, flush=True)


def run(cmd, cwd=None, logfile=None):
    """Run a command; raise with the tail of its output on failure. Returns seconds taken."""
    t0 = time.time()
    if logfile:
        with open(logfile, "w") as fh:
            p = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
        if p.returncode != 0:
            tail = open(logfile).read()[-3000:]
            raise RuntimeError("command failed (%d): %s\n%s" % (p.returncode, " ".join(cmd), tail))
    else:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError("command failed (%d): %s\n%s\n%s" % (p.returncode, " ".join(cmd), p.stdout[-3000:], p.stderr[-3000:]))
    return time.time() - t0


def read_fasta(path):
    out, name, buf = [], None, []
    for line in open(path):
        line = line.rstrip("\n")
        if line.startswith(">"):
            if name is not None:
                out.append((name, "".join(buf)))
            name, buf = line[1:].strip(), []
        elif line:
            buf.append(line.strip())
    if name is not None:
        out.append((name, "".join(buf)))
    return out


def write_fasta(path, entries):
    with open(path, "w") as f:
        for n, s in entries:
            f.write(">%s\n%s\n" % (n, s))


def gene_species(gene):
    """Zombi gene names are <species>_<geneid>."""
    return gene.rsplit("_", 1)[0]


def read_tsv(path):
    rows = []
    with open(path) as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            if line.strip():
                rows.append(dict(zip(header, line.rstrip("\n").split("\t"))))
    return rows


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def update_timings(simdir, key, seconds):
    p = os.path.join(simdir, "timings.json")
    d = json.load(open(p)) if os.path.exists(p) else {}
    d[key] = round(seconds, 2)
    write_json(p, d)
