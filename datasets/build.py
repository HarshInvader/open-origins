"""Build datasets/open/ (this project's own tables) and check datasets/catalog.csv.

    python3 -I datasets/build.py

Rules:
- open/ holds only tables this project made, copied from experiments/ and docs/ (CC BY 4.0). Nothing third-party in bulk:
  the SMILES column of the assembly molecule table is dropped, because half its rows come from GDB, which states no licence.
  Re-join by id after `datasets/fetch.py fetch daymude_at`.
- catalog.csv is written by hand. It lists every open or requestable dataset relevant to the project, used or not.
  This script checks its columns and values, refuses emails and local paths, and checks that every open/ file has an
  `included` row.
"""
import csv, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "datasets"
OPEN = HERE / "open"
EXP = ROOT / "experiments"
COLS = "id,title,kind,tier,origin,terms,size,n,labels,serves_tasks,used_by_us,verified,notes".split(",")
TIERS = ("included", "fetch", "request", "reference-only")
DROP = {"assembly_molecules.csv": {"smiles"}}
BAD = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|/Users/|/home/")

# (source, published name, description)
OPEN_TABLES = [
    ("docs/PAPERS.csv", "papers_ledger.csv", "Every cited paper, resolved by DOI, with the claim and what it was checked against"),
    ("experiments/*/ledger_rows.csv", "bench_ledger.csv", "One row per test from every experiment, with an `experiment` column"),
    ("experiments/pathway_map/map.json", "pathway_map.json", "Four routes as step tables, hand-offs, verdicts and ranked gaps"),
    ("experiments/pathway_map/handoffs.csv", "pathway_handoffs.csv", "Every hand-off with its verdict and flags"),
    ("experiments/compat/planted_cases.csv", "compat_planted_cases.csv", "Planted cases for the step-compatibility rule"),
    ("experiments/qt45_numbers/results_calc.json", "qt45_growth_calc.json", "QT45 net replication per cycle: inputs and growth factors"),
    ("experiments/raf/results.json", "raf_planted_results.json", "Planted autocatalytic cores: recovery and null false-positive rates"),
    ("experiments/raf_null/observed.json", "raf_null_observed.json", "Xavier 2020 network as reproduced, and its observed maxRAF"),
    ("experiments/raf_null/null_sizes.jsonl", "raf_null_sizes.jsonl", "maxRAF size of every null replicate"),
    ("experiments/luca_planted/grid_summary.csv", "luca_planted_grid.csv", "Planted LUCA recovery: precision and recall per rule and grid cell"),
    ("experiments/assembly_null/out/molecules.csv", "assembly_molecules.csv", "Assembly index, mass, heavy atoms, compression length: Rhea vs GDB molecules"),
    ("experiments/assembly_null/out/mixtures.json", "assembly_mixtures.json", "Marshall 2021 mixtures as we read them: peak counts, m/z, labels"),
    ("experiments/assembly_null/results.json", "assembly_results.json", "Assembly-index test results: AUCs, deltas and CIs"),
]


def rows_of(text_rows):
    return list(csv.DictReader(text_rows))


def copy_table(src, name):
    """Copy one table into open/. Returns (rows, columns, dropped)."""
    out = OPEN / name
    if "*" in src:  # concatenate ledgers
        parts = sorted(ROOT.glob(src))
        rows, cols = [], ["experiment"]
        for p in parts:
            for r in rows_of(open(p, newline="", encoding="utf-8")):
                r = {"experiment": p.parent.name, **r}
                cols += [c for c in r if c not in cols]
                rows.append(r)
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
        return len(rows), len(cols), ""
    p = ROOT / src
    if p.suffix == ".csv":
        rows = rows_of(open(p, newline="", encoding="utf-8"))
        cols = list(rows[0].keys()) if rows else []
        drop = DROP.get(name, set())
        keep = [c for c in cols if c not in drop]
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keep, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
        return len(rows), len(keep), ";".join(sorted(drop & set(cols)))
    shutil.copy2(p, out)
    if p.suffix == ".jsonl":
        return sum(1 for _ in open(p, encoding="utf-8")), "", ""
    j = json.load(open(p, encoding="utf-8"))
    return (len(j) if isinstance(j, list) else ""), (len(j) if isinstance(j, dict) else ""), ""


def build_open():
    if OPEN.exists():
        shutil.rmtree(OPEN)
    OPEN.mkdir(parents=True)
    man = []
    for src, name, desc in OPEN_TABLES:
        if "*" not in src and not (ROOT / src).exists():
            print("missing", src); continue
        n, cols, dropped = copy_table(src, name)
        text = (OPEN / name).read_text(encoding="utf-8")
        if BAD.search(text):
            sys.exit(f"{name}: contains an email address or a local path; fix the source before publishing")
        man.append(dict(file=name, rows=n, columns=cols, description=desc, made_by=src, columns_removed=dropped))
    with open(OPEN / "MANIFEST.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0].keys())); w.writeheader(); w.writerows(man)
    return man


def check_catalog(man):
    p = HERE / "catalog.csv"
    rows = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
    head = next(csv.reader(open(p, newline="", encoding="utf-8")))
    errs = []
    if head != COLS:
        errs.append(f"columns are {head}, want {COLS}")
    ids = [r["id"] for r in rows]
    errs += [f"duplicate id {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for r in rows:
        if r["tier"] not in TIERS:
            errs.append(f"{r['id']}: tier {r['tier']!r}")
        if r["used_by_us"] not in ("yes", "no") or r["verified"] not in ("yes", "no"):
            errs.append(f"{r['id']}: used_by_us/verified must be yes or no")
        if not r["origin"] or not r["terms"]:
            errs.append(f"{r['id']}: origin and terms are required")
        if r["verified"] == "yes" and "checked 20" not in r["notes"] and r["tier"] != "included":
            errs.append(f"{r['id']}: verified rows say how they were checked")
        if any(BAD.search(v or "") for v in r.values()):
            errs.append(f"{r['id']}: email address or local path")
    included = {r["origin"].split("/")[-1] for r in rows if r["tier"] == "included"}
    errs += [f"open/{m['file']} has no included row" for m in man if m["file"] not in included]
    errs += [f"included row for {f} has no file in open/" for f in included if not (OPEN / f).exists()]
    if errs:
        sys.exit("catalog.csv:\n  " + "\n  ".join(errs))
    by = {t: sum(r["tier"] == t for r in rows) for t in TIERS}
    ver = sum(r["verified"] == "yes" for r in rows)
    used = sum(r["used_by_us"] == "yes" for r in rows)
    print(f"catalog.csv: {len(rows)} rows; " + ", ".join(f"{v} {k}" for k, v in by.items()) + f"; {ver} verified, {len(rows) - ver} not; {used} used by us")


if __name__ == "__main__":
    man = build_open()
    print(f"open/: {len(man)} tables written, MANIFEST.csv updated")
    check_catalog(man)
