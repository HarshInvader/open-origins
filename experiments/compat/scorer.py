"""Step-compatibility scorer implementing docs/prereg/compatibility_rule.md (rule v1).

Refuses to run unless the rule file's sha256 is listed in docs/prereg/HASHES.txt.
Parameters are read from the JSON block inside the rule file, not hard-coded here.

Pathway = dict(scenario=..., steps=[...], handoffs=[[process, ...], ...]); see planted.py for examples.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULE = ROOT / "docs/prereg/compatibility_rule.md"
HASHES = ROOT / "docs/prereg/HASHES.txt"


def load_rule():
    raw = RULE.read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    if h not in HASHES.read_text():
        raise SystemExit(f"rule sha256 {h} not in HASHES.txt; refusing to score")
    block = re.search(r"```json\n(.*?)\n```", raw.decode(), re.S).group(1)
    p = json.loads(block)
    p["sha256"] = h
    return p


P = load_rule()


class ProcErr(Exception):
    pass


def _between(x, a, b):
    return min(a, b) - 1e-9 <= x <= max(a, b) + 1e-9


def _state_from_step(step, prev_species):
    out = step["outputs"]
    sp = dict(prev_species)
    sp.update(out["species"])
    return dict(ph=out["ph"], t=out["t"], solvent=out["solvent"], redox=out["redox"],
                setting=step["setting"], species=sp, separated=set(), warn=set())


def apply_process(state, proc, scen):
    """Apply one process in place. Raise ProcErr for F7."""
    name = proc.get("process")
    if name not in P["processes"]:
        raise ProcErr(f"process {name!r} not on the closed list")
    t_lo, t_hi = scen["t_range"]
    cap = P["max_concentration_factor"]
    s = state

    def need(*keys):
        for k in keys:
            if k not in proc:
                raise ProcErr(f"{name}: missing parameter {k!r}")

    if name == "same_pot":
        return
    if name in ("mixing", "rehydration"):
        need("stream", "f")
        st = scen["streams"].get(proc["stream"])
        if st is None:
            raise ProcErr(f"{name}: stream {proc['stream']!r} not in scenario")
        f = proc["f"]
        if not 0 < f < 1:
            raise ProcErr(f"{name}: f={f} outside (0,1)")
        ph_new = proc.get("ph_after", (1 - f) * s["ph"] + f * st["ph"])
        t_new = proc.get("t_after", (1 - f) * s["t"] + f * st["t"])
        if not _between(ph_new, s["ph"], st["ph"]):
            raise ProcErr(f"{name}: pH {ph_new} not between {s['ph']} and {st['ph']}")
        if not _between(t_new, s["t"], st["t"]):
            raise ProcErr(f"{name}: T {t_new} not between {s['t']} and {st['t']}")
        sp = {k: v * (1 - f) for k, v in s["species"].items()}
        for k, v in st["species"].items():
            sp[k] = sp.get(k, 0.0) + v * f
        s["species"] = sp
        s["ph"], s["t"] = ph_new, t_new
        if name == "rehydration" or f >= 0.5 or s["solvent"] == "dry":
            s["solvent"] = st["solvent"]
        if f >= 0.5:
            s["redox"] = st["redox"]
        return
    if name == "evaporation":
        need("factor")
        k = proc["factor"]
        if not 1 <= k <= cap:
            raise ProcErr(f"evaporation factor {k} outside [1,{cap}]")
        ph_new = proc.get("ph_after", s["ph"])
        if abs(ph_new - s["ph"]) > P["evaporation_extra_ph_shift"] + 1e-9:
            raise ProcErr("evaporation pH shift too large")
        vol = set(scen.get("volatile", []))
        s["species"] = {a: c * k for a, c in s["species"].items() if a not in vol}
        s["ph"] = ph_new
        return
    if name == "drying":
        vol = set(scen.get("volatile", []))
        s["species"] = {a: c for a, c in s["species"].items() if a not in vol}
        s["solvent"] = "dry"
        return
    if name == "freezing_eutectic":
        need("t_after", "factor")
        lo, hi = P["freezing_t_range_c"]
        t_new, k = proc["t_after"], proc["factor"]
        if not (lo <= t_new <= hi and t_lo <= t_new <= t_hi):
            raise ProcErr(f"freezing T {t_new} outside allowed range")
        if not 1 <= k <= cap:
            raise ProcErr(f"freezing factor {k} outside [1,{cap}]")
        s["species"] = {a: c * k for a, c in s["species"].items()}
        s["t"] = t_new
        return
    if name in ("heating", "cooling"):
        need("t_after")
        t_new = proc["t_after"]
        if not t_lo <= t_new <= t_hi:
            raise ProcErr(f"{name}: T {t_new} outside scenario range")
        if (name == "heating" and t_new < s["t"]) or (name == "cooling" and t_new > s["t"]):
            raise ProcErr(f"{name}: wrong direction")
        s["t"] = t_new
        return
    if name == "uv_irradiation":
        if not scen.get("uv"):
            raise ProcErr("uv_irradiation in a scenario without UV")
        return
    if name == "thermophoresis":
        need("factor")
        if s["setting"] not in P["thermal_gradient_settings"]:
            raise ProcErr(f"thermophoresis in setting {s['setting']!r} without a thermal gradient")
        k = proc["factor"]
        if not 1 <= k <= cap:
            raise ProcErr(f"thermophoresis factor {k} outside [1,{cap}]")
        s["species"] = {a: c * k for a, c in s["species"].items()}
        return
    if name == "gas_exchange":
        ph_new = proc.get("ph_after", s["ph"])
        if abs(ph_new - s["ph"]) > P["gas_exchange_max_ph_shift"] + 1e-9:
            raise ProcErr("gas_exchange pH shift > limit")
        if "redox_after" in proc:
            if proc["redox_after"] != scen["redox"]:
                raise ProcErr("gas_exchange redox must become the scenario class")
            s["redox"] = proc["redox_after"]
        s["ph"] = ph_new
        return
    if name == "mineral_buffering":
        need("mineral", "ph_after")
        m = scen.get("minerals", {}).get(proc["mineral"])
        if m is None:
            raise ProcErr(f"mineral {proc['mineral']!r} not in scenario")
        if not m[0] <= proc["ph_after"] <= m[1]:
            raise ProcErr("mineral_buffering pH outside the mineral's range")
        s["ph"] = proc["ph_after"]
        return
    if name == "selective_separation":
        need("species", "property")
        if proc["property"] not in ("crystallisation", "adsorption", "volatility"):
            raise ProcErr("selective_separation: property must be crystallisation, adsorption or volatility")
        a = proc["species"]
        if a not in s["species"]:
            raise ProcErr(f"selective_separation: {a!r} not present")
        if proc.get("mode", "isolate") == "isolate":
            s["species"] = {a: s["species"][a]}
            s["separated"].add(a)
        else:
            s["species"].pop(a)
        if not proc.get("demonstrated_by"):
            s["warn"].add("W3")
        return
    if name == "transport":
        need("to_setting", "dilution")
        if proc["to_setting"] not in scen["settings"]:
            raise ProcErr("transport to a setting outside the scenario")
        d = proc["dilution"]
        if not 0 < d <= 1:
            raise ProcErr("transport dilution must be in (0,1]")
        s["species"] = {a: c * d for a, c in s["species"].items()}
        s["setting"] = proc["to_setting"]
        return
    raise ProcErr(f"unhandled process {name}")  # pragma: no cover


def check_inputs(state, step, scen, produced, flags, notes):
    feed = scen.get("feedstocks", {})
    stream_sp = {k for st in scen["streams"].values() for k in st["species"]}
    req = step["inputs"]
    for i, inp in enumerate(req):
        a, used = inp["species"], inp["conc"]
        if a not in produced and a not in feed and a not in stream_sp:
            flags.add("F4"); notes.append(f"F4 {a} not produced earlier nor a feedstock/stream species")
            continue
        avail = max(state["species"].get(a, 0.0) if state else 0.0, feed.get(a, 0.0))
        r = avail / used if used > 0 else float("inf")
        if r < P["conc_fail_ratio"]:
            flags.add("F5"); notes.append(f"F5 {a}: available {avail:.3g} M vs used {used:.3g} M")
        elif r < P["conc_warn_ratio"]:
            flags.add("W2"); notes.append(f"W2 {a}: available {avail:.3g} M vs used {used:.3g} M")
        if inp.get("purified") and (state is None or a not in state["separated"]):
            flags.add("F6"); notes.append(f"F6 {a} purified by the source, no selective_separation")
    if state is not None and req:
        main = req[0]["species"]
        mc = max(state["species"].get(main, 0.0), feed.get(main, 0.0))
        names = {x["species"] for x in req}
        tested = set(step.get("tested_with", []))
        for a, c in state["species"].items():
            if a not in names and a not in tested and c > P["interference_ratio"] * mc:
                flags.add("W1"); notes.append(f"W1 {a} at {c:.3g} M untested (main input {main} {mc:.3g} M)")


def score(pathway):
    scen, steps, hand = pathway["scenario"], pathway["steps"], pathway["handoffs"]
    assert len(hand) == len(steps) - 1, "need one hand-off list between each pair of steps"
    results = []
    # entry check for step 1 (F4/F5/F6/F9 against the scenario): applied as F4 says
    f0, n0 = set(), []
    if steps[0]["setting"] not in scen["settings"]:
        f0.add("F9"); n0.append("F9 step 1 setting not in scenario")
    check_inputs(None, steps[0], scen, set(), f0, n0)
    results.append(dict(handoff="entry->1", flags=sorted(f0), notes=n0))
    produced = set(steps[0]["outputs"]["species"])
    state = _state_from_step(steps[0], {})
    for k in range(1, len(steps)):
        nxt = steps[k]
        flags, notes = set(), []
        s = copy.deepcopy(state)
        for proc in hand[k - 1]:
            try:
                apply_process(s, proc, scen)
            except ProcErr as e:
                flags.add("F7"); notes.append(f"F7 {e}")
        flags |= s["warn"]
        c = nxt["conditions"]
        if abs(s["ph"] - c["ph"]) > P["ph_tolerance"] + 1e-9:
            flags.add("F1"); notes.append(f"F1 pH {s['ph']:g} after hand-off, step needs {c['ph']:g}")
        t_lo, t_hi = scen["t_range"]
        if abs(s["t"] - c["t"]) > P["t_tolerance_c"] + 1e-9 or not t_lo <= c["t"] <= t_hi:
            flags.add("F2"); notes.append(f"F2 T {s['t']:g} after hand-off, step needs {c['t']:g}")
        if s["solvent"] != c["solvent"]:
            flags.add("F3"); notes.append(f"F3 solvent {s['solvent']} vs {c['solvent']}")
        if s["redox"] != c["redox"]:
            flags.add("F8"); notes.append(f"F8 redox {s['redox']} vs {c['redox']}")
        if nxt["setting"] not in scen["settings"] or s["setting"] != nxt["setting"]:
            flags.add("F9"); notes.append(f"F9 setting {s['setting']} vs {nxt['setting']}")
        check_inputs(s, nxt, scen, produced, flags, notes)
        results.append(dict(handoff=f"{k}->{k+1}", flags=sorted(flags), notes=notes))
        produced |= set(nxt["outputs"]["species"])
        state = _state_from_step(nxt, s["species"])
    hard = set(P["hard_fails"])
    n_fail = sum(1 for r in results if hard & set(r["flags"]))
    n_warn = sum(len(set(r["flags"]) - hard) for r in results)
    labels = [st.get("yield_label", "missing") for st in steps]
    return dict(rule_sha256=P["sha256"], handoffs=results, n_handoffs=len(steps) - 1,
                n_hard_fail_handoffs=n_fail, n_warnings=n_warn,
                n_purified_steps=labels.count("demonstrated_purified"),
                n_missing_steps=labels.count("missing"),
                continuous=(n_fail == 0 and labels.count("missing") == 0))
