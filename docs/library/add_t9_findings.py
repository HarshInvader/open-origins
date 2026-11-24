"""One-off: record T9 on the Huang 2026 and Csűrös 2026 library entries (2026-11-24)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); by = {e["id"]: e for e in d["papers"]}
TODAY = "2026-11-24"
h = by["huang-2026-laca-methanogen-reconciliation"]
h["ideas_for_us"] = (h.get("ideas_for_us", "").rstrip() + " T9 (sealed, 2026-11-24, experiments/t9_dpann_completeness/T9_RESULTS.md): "
    "is DPANN's higher loss rate an artefact of incomplete genomes? On internal branches with at least 3 genomes, where one incomplete genome "
    "cannot create a loss, the DPANN loss fraction is 1.37 times the other archaea's (1.146 to 1.63); support needed a lower bound above 1.15, "
    "so the sealed verdict is inconclusive by a hair. Tip losses do rise with incompleteness, and the DPANN tip excess is explained by it; "
    "the deep-branch excess is not.").strip()
h["date"] = TODAY
c = by["csuros-2026-gld-ancient-genomes"]
c["ideas_for_us"] = (c.get("ideas_for_us", "").rstrip() + " Used as prior art for T9: it names the DPANN completeness confound and says copy numbers "
    "cannot separate it ('perfectly absorbed by increased loss'), which is why T9 tests deep branches only.").strip()
c["date"] = TODAY
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("ok")
