"""One-off: add the papers read for T8 (Ameta 2021 noise null), 2026-11-24."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text())
L = d["papers"]; by = {e["id"]: e for e in L}
TODAY = "2026-11-24"
def base(**k):
    e = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
         "added": TODAY, "date": TODAY, "relevance": "useful"}
    e.update(k); return e
new = [
  base(id="ameta-2021-darwinian-rna-networks",
       title="Darwinian properties and their trade-offs in autocatalytic RNA reaction networks",
       authors="Ameta S, Arsène S, Foulon S, Saudemont B, Clifton BE, Griffiths AD, Nghe P",
       year=2021, venue="Nature Communications 12:842", doi="10.1038/s41467-021-21000-1",
       url="https://doi.org/10.1038/s41467-021-21000-1", topic="RNA world", read_depth="full",
       question="Do networks of self-assembling Azoarcus ribozyme fragments show heritable, selectable properties, and do growth and variability trade off?",
       tried="Assemble many combinations of up to 16 ribozyme fragment species in microfluidic droplets, count each species by sequencing (UMIs), and compare networks that differ by one added species.",
       method_data="Droplet microfluidics with barcoded sequencing; yield per droplet from ribozyme UMIs scaled by reporter UMIs; perturbation = L1 distance between renormalised species fractions of G and G plus one species; Supplementary Data 2 (1,837 networks, 20,039 droplets); code on Zenodo/GitHub.",
       key_results="Networks show growth, variation and heritable composition. Adding a species can switch composition. The authors report that high-yield networks are less perturbable, a trade-off between growth and variation (Fisher test on 162 pairs, odds ratio < 0.1, p = 1.6e-3).",
       limits="Our T8 (sealed, 2026-11-24): the Fisher test reproduces exactly, but across 1,093 additions with at least 5 droplets per side the yield-perturbation correlation (-0.11) is no stronger than yield against each network's own split-half noise (-0.15); given noise it is -0.06 (-0.12 to 0.01). Low-yield droplets are noisier. In the paper's own subset (41 pairs with enough droplets) a strong effect remains, but that subset is small and selected.",
       ideas_for_us="Done as T8 (experiments/t8_ameta_noise/T8_RESULTS.md). The lesson: a composition change measured from counts needs a same-sample noise null before it is read against a count-derived quantity like yield.",
       touches=["#4"], source_opened="full text (PMC7870898, CC BY), Supplementary Data 2 and the authors' code"),
  base(id="matsubara-2022-darwinian-autocatalytic-compartments",
       title="Conditions for Darwinian evolution in compartmentalized autocatalytic reaction networks",
       authors="Matsubara YJ, Ameta S, Thutupalli S, Nghe P, Krishna S",
       year=2022, venue="arXiv:2211.03155", doi="", url="https://arxiv.org/abs/2211.03155",
       topic="RNA world", read_depth="abstract", relevance="background",
       question="Under what growth and division regimes can compartmentalised autocatalytic networks evolve?",
       tried="Theory and simulation of multistable autocatalytic networks in dividing compartments.",
       method_data="Mathematical models of reaction networks under growth-division cycles.",
       key_results="Abstract: multistable autocatalytic reaction networks can maintain heritable compositional states across a broad class of growth-division regimes.",
       limits="Read as abstract only. Theory; it does not reanalyse the 2021 droplet data.",
       ideas_for_us="Prior art for T8: the closest related work, not a reanalysis.",
       touches=["#4"], source_opened="arXiv abstract page"),
]
for e in new:
    if e["id"] in by: by[e["id"]].update(e)
    else: L.append(e)
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print(len(L))
