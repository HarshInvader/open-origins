"""One-off: record the T5 and T6 results on the Moody 2024 and Wehbi 2024 library entries (2026-11-24)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text())
by = {e["id"]: e for e in d["papers"]}
TODAY = "2026-11-24"
m = by["moody-2024-luca"]
m["ideas_for_us"] = (m.get("ideas_for_us", "").rstrip() + " T6 (sealed, 2026-11-24, experiments/t6_moody_ko_cog/T6_RESULTS.md): their COG analysis, "
    "run to recover LUCA families split across KEGG families, rescues 23 of 433 eligible merged COGs, no more than a plain re-run does "
    "(ratio 0.66, 95% interval 0.40 to 1.08). Merging more often drops a family a member KO placed in LUCA (46% against 15%). "
    "Re-running alone changes the LUCA call at 0.5 for 11.2% of single-KO families.").strip()
m["date"] = TODAY
w = by["wehbi-2024-genetic-code-order"]
w["ideas_for_us"] = w["ideas_for_us"].rstrip() + (" T5 (sealed, 2026-11-24, experiments/t5_wehbi_moody/T5_RESULTS.md): their '88.6% agreement with Moody' "
    "is mostly a base rate. Post-LUCA Pfams matched on how many COGs they map to agree 80.6% of the time; the gap is 8.1 points (5.6 to 10.5).")
w["date"] = TODAY
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print("ok")
