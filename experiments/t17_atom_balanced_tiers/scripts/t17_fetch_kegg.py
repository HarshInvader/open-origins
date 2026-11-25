"""T17: fetch KEGG COMPOUND entries for every species of the T14 biochemical network (S2 Table).

Usage:  python -I t17_fetch_kegg.py <experiments/t17_atom_balanced_tiers dir>

Polite: 10 ids per call (the KEGG REST maximum), at least 0.5 s between calls, a generic User-Agent, no
personal details.  Each response is saved untouched as raw/kegg/batch_NNN.txt (gitignored; KEGG REST is free
for academic use but not ours to republish).  Batches already on disk are skipped, so a re-run resumes.
The responses are treated as untrusted text: they are only ever parsed by t17_analysis.py (run with -I).
"""
import importlib.util
import os
import sys
import time
import urllib.request

D = os.path.abspath(sys.argv[1])
T14 = os.path.join(os.path.dirname(D), "t14_autocatalytic_tiers")
sys.argv = [sys.argv[0], T14, "lib"]
spec = importlib.util.spec_from_file_location("t14", os.path.join(T14, "scripts", "t14_analysis.py"))
t14 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t14)

net, _, _ = t14.load_db("bio")
ids = sorted(net.names)
assert all(len(x) == 6 and x[0] == "C" and x[1:].isdigit() for x in ids)
out = os.path.join(D, "raw", "kegg")
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "ids.txt"), "w") as f:
    f.write("\n".join(ids) + "\n")
UA = "open-research-site/1.0"
batches = [ids[i:i + 10] for i in range(0, len(ids), 10)]
last = 0.0
for b, chunk in enumerate(batches):
    fn = os.path.join(out, "batch_%03d.txt" % b)
    if os.path.exists(fn) and os.path.getsize(fn) > 0:
        continue
    url = "https://rest.kegg.jp/get/" + "+".join("cpd:" + x for x in chunk)
    for attempt in range(4):
        wait = 0.6 - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        last = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read(5_000_000)
            break
        except Exception as e:  # back off and retry
            print("batch", b, "attempt", attempt, "error", type(e).__name__, flush=True)
            time.sleep(5 * (attempt + 1))
    else:
        sys.exit("giving up at batch %d" % b)
    with open(fn, "wb") as f:
        f.write(body)
    if b % 50 == 0:
        print("batch", b, "of", len(batches), flush=True)
print("done", len(batches), "batches")
