"""One-off: correct the T16 'Mean row' statement on the Attwater 2025 entry (2026-11-25 recheck)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); by = {e["id"]: e for e in d["papers"]}
e = by["attwater-2025-rna-world"]
old = ("and the deposited 'Mean' row is not the arithmetic mean, geometric mean or median "
       "of the three datasets.")
new = ("and (corrected after a fresh recheck) the deposited 'Mean' rows are geometric means of three datasets, "
       "but the two Dataset 2 rows are swapped between the FITC and Cy5 blocks of SD_Fig3e.xlsx. "
       "The text's folds equal 1 + k rather than e^k.")
assert old in e["ideas_for_us"]
e["ideas_for_us"] = e["ideas_for_us"].replace(old, new)
d["updated"] = "2026-11-25"
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("ok")
