"""One-off: K7 pilot note on Moody 2024 (2026-11-25)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); by = {e["id"]: e for e in d["papers"]}
e = by["moody-2024-luca"]
e["ideas_for_us"] = (e.get("ideas_for_us", "").rstrip() + " K7 pilot (2026-11-25, experiments/k7_realism_bound, not sealed): "
    "Supplementary Data 5 gives transfers received per copy of 0.164 (archaeal stem) and 0.24 (bacterial stem) against a mean of 0.229 over "
    "all nodes, so at face value the stems look like background. But in our simulated worlds with 1-600x planted stem-to-stem transfer, ALE "
    "inferred almost no transfers leaving a stem (about 0.6 against 187 true crossings at 600x); the crossings showed up as extra root presence "
    "instead. A pilot only (families over 152 genes were skipped), but it suggests a stem ratio like this cannot rule out heavy stem exchange. "
    "Per-family reconciliations are public at data.bris (doi:10.5523/bris.405xnm7ei36d2cj65nrirg3ip).").strip()
d["updated"] = "2026-11-25"
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("ok")
