"""One-off: record T16 (not decidable) on the Attwater 2025 library entry (2026-11-25)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); by = {e["id"]: e for e in d["papers"]}
e = by["attwater-2025-rna-world"]
e["ideas_for_us"] = (e.get("ideas_for_us", "").rstrip() + " T16 (not decidable, 2026-11-25, experiments/t16_attwater_exponential/README.md): "
    "is the Fig. 3e growth exponential rather than parabolic or linear? With 3 reactions over cycles 0-4, and scatter that is mostly a constant "
    "per-reaction offset, the plan's AICc test reaches support under 1% of the time even if growth is exponential, and would call it 'not exponential' "
    "45-100% of the time, so it was stopped before sealing. Two reporting points, no test needed: the caption's e^0.38x and e^0.20x are 1.46- and "
    "1.22-fold per cycle, while the text says '1.2- and 1.38-fold'; and the deposited 'Mean' row is not the arithmetic mean, geometric mean or median "
    "of the three datasets.").strip()
e["date"] = "2026-11-25"; d["updated"] = "2026-11-25"
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("ok")
