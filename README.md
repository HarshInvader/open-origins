# Open Origins: test how life began, in the open

**Goal: by the end of 2027, an audited map of every proposed route from geochemistry to evolving life, with each step scored and every gap named. Alongside it, predictions we sealed in advance that data published afterwards confirms.**

The field asks two questions, and we keep them apart:
- **Can chemistry do it?** Is there any continuous route?
- **What happened on Earth?** Showing a route is possible does not show it is the one that happened.

**Honest odds** (from the project plan, `docs/fable_plan.md`):
- Fully "cracked" (R-full below) by 2027: under 1 in 100.
- The open goal (R-open) by 2027: about 12%. The limit is whether confirming data appears in time.

**What would raise the odds:**
- New Bennu or Ryugu compound tables released after our hash.
- A lab reporting sustained exponential replication by a small ribozyme, which we model in advance.
- One wet lab agreeing to run a pre-registered test. The human lead asks; agents never contact anyone.

## Root milestones

**R-full ("cracked").** One stated geochemical scenario and one pathway from its feedstocks to a system with heritable variation in replication rate, where:
1. Every step has a yield published by a lab other than us (the outside anchor).
2. Every step's inputs can be reached from the previous step's outputs by a named physical process, with no purified hand-offs, under a compatibility rule we hash in advance.
3. A kinetic model fitted on steps 1..k predicts at least 3 measurements published after the hash, within a pre-set tolerance.
4. An independent red team fails to break it.

**R-open (what we can move), by 2027-12-31:**
- The pathway map covers at least 4 scenarios, with every step scored.
- At least 10 published claims are benched against nulls.
- At least 3 hashed predictions are confirmed by later data, at least one about returned-sample chemistry or a ribozyme landscape.

Our bench can refute a claim or score a pathway. Only wet-lab or sample data from others can confirm one.

## The claim ladder ("can chemistry do it?")

| Level | Claim | Field today |
|---|---|---|
| L0 | Building blocks from a stated setting | Largely met (Bennu: 33 amino acids, all five nucleobases, ribose) |
| L1 | Activation and polymerisation under compatible conditions | Partly met; chaining steps without purification is the weak point |
| L2 | Template copying of function-length sequences | Shown under engineered conditions (QT45, Science 2026) |
| L3 | Sustained exponential self-replication from scenario feedstocks | Not met |
| L4 | Open-ended Darwinian evolution in a compartment | Not met |

A separate **H track** ("what happened on Earth") covers LUCA, timing and setting. LUCA was already a complex cell, so it constrains the end point, not the start.

## Theories on the scoreboard

The theories are RNA world, alkaline vents / metabolism first, warm ponds / wet-dry cycling, cyanosulfidic chemistry, peptide-RNA co-evolution, autocatalytic sets (RAF), assembly theory, homochirality routes and lipid world. Each one's riskiest prediction and its 2023-2026 evidence are in `docs/fable_plan.md` §3 and on the site.

## How the work is done (same rules as Open Indus)

1. **Seal it before you look.** Write the prediction, test and pass mark in `docs/prereg/`, and append the SHA-256 to `docs/prereg/HASHES.txt` first.
2. **Fix "prebiotically plausible" in advance.** The step-compatibility rule is hashed before any pathway is scored.
3. **Planted answer first:**
   - a LUCA method must recover a planted ancestor on simulated trees with gene transfer;
   - a RAF method must find a planted core and not flag random networks;
   - assembly index must beat a size-only classifier.
4. **Red team.** Every positive result goes to an agent that did not produce it.
5. **Verify every citation.** AI agents invent references. Nothing reaches the site without a DOI that someone checked.
6. **Publish either way** (`docs/NEGATIVE_ATLAS.md`).

Work is done by AI agents with a human lead on one shared task board (`board/README.md`). Everything runs on one laptop.

## Layout

- `docs/AGENT_BRIEF.md`: rules of evidence.
- `docs/fable_plan.md`: the founding plan.
- `docs/prereg/`: sealed pre-registrations.
- `board/`: the task board.
- `experiments/<area>/`: code and results.
- `data/`: public data, fetched by script.
- `site/`: the public site.
