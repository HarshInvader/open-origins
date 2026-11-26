"""T19: fetch elemental formulas for the KEGG compounds in the Xavier 2020 dataset S4.

Prereg: docs/prereg/t19_raf_atom_balanced.md ("Data"). Terms fixed there and obeyed here:
at least 0.5 s between calls, User-Agent "open-research-site/1.0", no personal details sent,
10 ids per call, responses treated as untrusted text and parsed by a strict regex over the
ENTRY and FORMULA lines only. Resumable: already-cached ids are not re-fetched.

Run from the repo root:  python3 -I experiments/raf_null/scripts/t19_fetch_formulas.py
Writes experiments/raf_null/formulas.tsv (id, formula) sorted by id, and prints its sha256.
"""
import hashlib
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
SRC = EXP / "raw" / "rspb20192377supp5.txt"
OUT = EXP / "formulas.tsv"
UA = "open-research-site/1.0"
PAUSE = 0.5
BATCH = 10

ID_RE = re.compile(r"^C\d{5}$")
# KEGG flat file: "ENTRY       C00001            Compound" / "FORMULA     H2O"
ENTRY_RE = re.compile(r"^ENTRY\s+(C\d{5})\b")
FORMULA_RE = re.compile(r"^FORMULA\s+(\S+)\s*$")


def network_ids():
    """The distinct KEGG compound ids in the <molecules> section, in file order."""
    ids, sec, seen = [], None, set()
    with open(SRC, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            t = line.strip()
            if t.startswith("<") and t.endswith(">"):
                sec = t
                continue
            if sec != "<molecules>" or not t:
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) > 1:
                cid = parts[1].strip()
                if ID_RE.fullmatch(cid) and cid not in seen:
                    seen.add(cid)
                    ids.append(cid)
    return ids


def parse(text):
    """Pull {id: formula} out of an untrusted KEGG flat-file response.

    Only ENTRY and FORMULA lines are read. An entry with no FORMULA line, or with a generic
    group in it, is left out: the prereg treats those molecules as formula-less, and that
    decision belongs to the analysis, not here.
    """
    out, cur = {}, None
    for line in text.splitlines():
        m = ENTRY_RE.match(line)
        if m:
            cur = m.group(1)
            continue
        if line.startswith("///"):
            cur = None
            continue
        m = FORMULA_RE.match(line)
        if m and cur:
            out[cur] = m.group(1)
            cur = None
    return out


def load_cache():
    if not OUT.exists():
        return {}
    cache = {}
    for line in OUT.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) == 2 and ID_RE.fullmatch(parts[0]):
            cache[parts[0]] = parts[1]
    return cache


def save(cache):
    body = "".join("%s\t%s\n" % (k, cache[k]) for k in sorted(cache))
    OUT.write_text(body)
    return hashlib.sha256(body.encode()).hexdigest()


def main():
    ids = network_ids()
    cache = load_cache()
    # ids we have never resolved; an id KEGG answered without a FORMULA stays unresolved and
    # is re-asked on a later run, which is harmless and keeps the no-formula set explicit.
    todo = [i for i in ids if i not in cache]
    print("network ids %d, cached %d, to fetch %d" % (len(ids), len(cache), len(todo)), flush=True)
    fetched = failed = 0
    for n in range(0, len(todo), BATCH):
        chunk = todo[n : n + BATCH]
        url = "https://rest.kegg.jp/get/" + "+".join(chunk)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                text = r.read().decode("utf-8", "replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print("batch %d failed: %s" % (n // BATCH, e), flush=True)
            failed += 1
            time.sleep(5.0)
            continue
        got = parse(text)
        bad = set(got) - set(chunk)
        if bad:  # a response naming ids we did not ask for is not trusted
            print("batch %d returned unrequested ids %s; skipped" % (n // BATCH, sorted(bad)[:5]), flush=True)
            failed += 1
            time.sleep(PAUSE)
            continue
        cache.update(got)
        fetched += len(got)
        if (n // BATCH) % 25 == 0:
            save(cache)
            print("  %d/%d ids, %d formulas" % (n + len(chunk), len(todo), len(cache)), flush=True)
        time.sleep(PAUSE)
    h = save(cache)
    noformula = [i for i in ids if i not in cache]
    print("formulas %d of %d network ids; %d with no FORMULA line; %d batch failures"
          % (len(cache), len(ids), len(noformula), failed), flush=True)
    print("generic (R/X/n group): %d" % sum(1 for v in cache.values() if re.search(r"[RXn]", v)), flush=True)
    print("%s  %s" % (h, OUT.relative_to(EXP.parent.parent)), flush=True)
    return 0 if fetched or not todo else 1


if __name__ == "__main__":
    sys.exit(main())
