# Origin-of-life routes: riskiest open-data claim per route, ranked tests (2026-11-23)

This plan comes from a planning agent that read the repo and opened the papers named below; the coordinator reviewed it. No outcome statistic has been computed for any test, so each can still be sealed blind. "Opened" means the agent read the full text; "named" means the source was cited but not read, and must be read before sealing.

## Routes, ranked by how cheap and decisive the test is

| Rank | Route | Riskiest checkable claim | Test | Data |
|---|---|---|---|---|
| 1 | Alkaline vents / metabolism-first (Martin, Lane, Russell) | 95–97% of LUCA's core biosynthetic reactions are exergonic under vent conditions, with the maximum near pH 9 and 80 °C (Wimmer et al. 2021) | T1: specificity null (reversed reactions, matched non-core reactions, ΔG-uncertainty Monte Carlo over pH × T) | Wimmer SI Tables 1, 3 and 8; eQuilibrator; Rhea; Xavier S4 (in repo) |
| 2 | Peptide / code co-evolution, with meteoritic delivery | Amino acids entered the code in order of prebiotic availability | T2: do Bennu and Ryugu abundances predict the Wehbi 2024 order beyond molecular size? | Wehbi 2024; Glavin 2025 tables; Astromat |
| 3 | RNA world, in each setting | RNA lasts long enough to be copied where the route puts it | T3: persistence budget, using hydrolysis kinetics over field (T, pH, Mg) distributions | MARHYS 4.0; USGS Yellowstone; Levy & Miller 1998; Larralde 1995 |
| 4 | Hot springs / wet-dry ponds | Real spring water supports both vesicles and polymerisation | Share of real analyses inside the lab windows; Flory–Schulz null on oligomer lengths | USGS; Caimi 2025; Simonis 2026 |
| 5 | Cyanosulfidic | One UV-lit pool supplies cyanide, sulfite and phosphate at lab concentrations | Monte Carlo ratio of required to supplied concentration | Toner & Catling 2020; Anslow 2026 |
| 6 | Lipid / compartment-first | Fatty-acid vesicles coexist with the Mg²⁺ that RNA needs | Joint window over real fluids | MARHYS, USGS |
| 7 | Iron-sulfur world | LUCA-era families are enriched in FeS and metal cofactors | Rank enrichment against root PP, matched on family breadth | Moody features; UniProt |
| 8 | Autocatalytic sets | Minerals expand reachable metabolism | Size-matched random-reaction null, only if the network is deposited | Plan 2 said stop network nulls |
| 9 | Heat-flow concentration | About 1000× accumulation at natural gradients | Scaling argument | Not a clean kill |
| 10 | Impacts / reducing atmosphere | Impact HCN reaches pond levels | Mostly done by Anslow 2026 | — |

## T1, the first kill test (draft prereg bullets)

- **Claim.** Wimmer, Xavier, … Martin 2021, Front. Microbiol., doi:10.3389/fmicb.2021.793664 (opened, PMC8710812).
  - 402 core reactions, hand-polarised toward synthesis; 351–353 scored.
  - About 77% exergonic at 1 mM; 95–98% with products 100× below reactants.
  - Maximum "around pH 9, 80 °C", read as matching Lost City.
- **Weak points named in the paper itself.**
  - The component contribution method has no temperature term, so temperature enters only through RT·ln Q. With Q < 1, hotter is always more exergonic.
  - Modern metabolism is also generally exergonic.
- **Gate.** Our ΔG at pH 7, 25 °C, 1 mM must correlate r ≥ 0.98 with their Table 3, and the exergonic share must be within 2 points of theirs.
- **Planted control.** Symmetric ΔG′° gives about 50%; a −15 kJ/mol shift is detected as specific.
- **K-direction.** Reverse every core reaction and apply the same gradient.
  - Kill: ≥ 50% exergonic.
  - Support: ≤ 30%.
- **K-specificity.** Core minus a matched null (EC class, substrate and product counts, ATP use) at pH 9, 80 °C; bootstrap by KEGG module.
  - Kill: the gap is < 5 points and the CI excludes 10.
  - Support: the gap is ≥ 15 points and the CI excludes 5.
- **K-setting.** (Vent − pond) for the core, minus the same contrast for the null, over 1,000 ΔG draws.
  - Kill: the CI includes 0, or the maximum lies in pH 8–10 and T ≥ 70 °C in < 50% of draws.
  - Support: the CI excludes 0 and the maximum is in that window in ≥ 90% of draws.
- **Verdict.**
  - Two or more kills: uninformative.
  - All three supported: supported.
  - Otherwise: per arm.
- **Seal before any ΔG.**
  - Two direction rules for the null; they must agree.
  - The matching variables and the seed.
  - How H₂, H₂O and H⁺ enter Q, copied from the paper's Methods.
- **Before sealing.**
  - The 1.3 GB eQuilibrator cache (doi:10.5281/zenodo.4128543, CC BY) does not fit on the laptop disk now. Check whether `equilibrator-api` can run on a smaller compound subset, or run it on AWS after 1 Dec.
  - Check that Rhea or UniProt direction annotations cover enough non-core reactions for the null.

## T2 and T3

- **T2.**
  - Kendall partial τ between log abundance and the Wehbi LUCA enrichment, controlling for molecular weight; 10⁵ permutations. Fit on Murchison; score on Bennu and Ryugu.
  - Support: τ ≥ 0.4 and p < 0.01 in both.
  - Kill: τ ≤ 0.1 in both, with the upper 95% bound < 0.4.
  - Sources: Wehbi 2024 doi:10.1073/pnas.2410311121 (opened); Glavin 2025 doi:10.1038/s41550-024-02472-9 (opened); Higgs & Pudritz 2009 (named only).
  - Chance of a decisive result is about 40% (n ≤ 20).
- **T3.**
  - L* = sqrt(ln 2 · k_ext / (2 k_cl)) per field sample and copying system, plus the Eigen limit.
  - A setting fails if ≥ 95% of samples give L* < 45 nt for every system.
  - Li & Breaker 1999 is paywalled, so its rate law must be confirmed from a legal copy first.

## Backup list (from the LUCA design agent; still valid)

1. Does the acetogen/lifestyle call survive w, and 65 vs 700 genomes?
2. Does the root-weight dependence generalise to Huang 2026?
3. A K5 realism bound using K6 transfer counts.
4. Red-team the RAF negative (#24) and the assembly-index positive (#22).
5. Seal the purine:pyrimidine vs ammonia prediction (#19).
