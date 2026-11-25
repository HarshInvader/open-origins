"""K7 measure: stem transfer intensity read from ALEml_undated output (.uml_rec), the same way for
simulated worlds and for Moody et al. 2024's deposited reconciliations (prereg k7_realism_bound.md).

Only reconciliation output is used, never simulation truth.

Per .uml_rec file (one gene family) this returns a compact record:
  - the species tree from the "S:" line, with ALE's internal branch ids; the root is the branch with
    the largest id (checked: it is the node with no parent); its two children are the two "stems"
    (in our simulations the branches above the two domain crowns; in Moody et al. the branches
    above LACA and LBCA when the root splits Archaea from Bacteria).
  - from the 100 sampled reconciled gene trees, every transfer token "T@<donor>-><recipient>",
    divided by the number of samples, so each count is a posterior expectation.
  - from the per-branch table: Transfers (received; ALE's branch_counts["Ts"]), copies and presence.

Family-level quantities (all posterior expectations):
  x_stem_out   inter-domain transfers whose donor is a stem (recipient in the other stem's clade)
  x_int_out    inter-domain transfers whose donor is an internal, non-stem, non-root branch
  pres_stem    presence summed over the two stems
  pres_int     presence summed over internal non-stem non-root branches
  t_in_stem    Transfers received on the two stems;     cop_stem: copies on the two stems
  t_in_all     Transfers received on all non-root branches; cop_all: copies on all non-root branches
  node_ratio_* per-stem T/copies (for the Moody Supp. Data 5 reproduction check)

World-level measures (pooled over families; prereg section "Measures"):
  M1 = (sum x_stem_out / sum pres_stem) / (sum x_int_out / sum pres_int)     donor-based, primary
  M2 = (sum t_in_stem / sum cop_stem) / (sum t_in_all / sum cop_all)         received, SD5-style

Usage:
  python3 -I k7_measure.py parse <uml_rec>...        print one JSON record per file
"""
import json
import re
import sys

TOK = re.compile(r"T@([^\s:,();>]+)->([^\s:,();.]+)")


def parse_newick_ids(s):
    """Minimal newick parser for ALE's S: line. Returns parent map and children map keyed by label
    (leaf names; internal ALE ids as strings)."""
    parent, children = {}, {}
    i, n = 0, len(s)
    node_stack = [[]]
    while i < n:
        c = s[i]
        if c == "(":
            node_stack.append([])
            i += 1
        elif c == "," or c == ";":
            i += 1
        elif c == ")":
            kids = node_stack.pop()
            i += 1
            j = i
            while j < n and s[j] not in ":,);":
                j += 1
            label = s[i:j]
            i = j
            if i < n and s[i] == ":":
                j = i + 1
                while j < n and s[j] not in ",);":
                    j += 1
                i = j
            if not label:
                label = "__root__"
            children[label] = kids
            for k in kids:
                parent[k] = label
            node_stack[-1].append(label)
        else:
            j = i
            while j < n and s[j] not in ":,);":
                j += 1
            label = s[i:j]
            i = j
            if i < n and s[i] == ":":
                j = i + 1
                while j < n and s[j] not in ",);":
                    j += 1
                i = j
            node_stack[-1].append(label)
    return parent, children


def clade(children, x):
    out, st = set(), [x]
    while st:
        y = st.pop()
        out.add(y)
        st.extend(children.get(y, ()))
    return out


def parse_uml_rec(path):
    S_line, rows, toks, samples = None, {}, [], None
    max_internal = -1
    with open(path) as f:
        for line in f:
            if line.startswith("S:\t"):
                S_line = line[3:].strip()
            elif line.startswith("S_terminal_branch") or line.startswith("S_internal_branch"):
                p = line.rstrip("\n").split("\t")
                name = p[1]
                if p[0] == "S_terminal_branch":
                    name = name.rsplit("(", 1)[0]
                else:
                    max_internal = max(max_internal, int(name))
                rows[name] = (float(p[3]), float(p[6]), float(p[9]))   # Transfers(received), copies, presence
            elif line.endswith("reconciled G-s:\n"):
                samples = int(line.split()[0])
            elif "T@" in line and samples is not None:
                toks.extend(TOK.findall(line))
    if S_line is None or samples is None:
        raise ValueError("not a complete uml_rec: %s" % path)
    parent, children = parse_newick_ids(S_line)
    # ALE writes the root without a label in S:; its id is the largest internal id in the table
    root = str(max_internal)
    if "__root__" in children:
        children[root] = children.pop("__root__")
        for k in children[root]:
            parent[k] = root
    roots = [x for x in children if x not in parent]
    if roots != [root]:
        raise ValueError("root mismatch in %s: %s vs %s" % (path, roots, root))
    stems = children[root]
    if len(stems) != 2:
        raise ValueError("root is not binary")
    cl = [clade(children, s) for s in stems]
    side = {}
    for i, c in enumerate(cl):
        for x in c:
            side[x] = i
    internal = set(children) - {root}
    return {"stems": stems, "clades": cl, "side": side, "internal": internal, "root": root,
            "rows": rows, "toks": toks, "samples": samples}


def family_record(path, leaf_domain=None):
    r = parse_uml_rec(path)
    stems, side, internal, rows, ns = r["stems"], r["side"], r["internal"], r["rows"], float(r["samples"])
    sset = set(stems)
    x_stem_out = x_int_out = x_term_out = x_stem_in = x_root_tok = 0.0
    n_tok = 0
    for d, g in r["toks"]:
        n_tok += 1
        if d == r["root"] or g == r["root"]:
            x_root_tok += 1                            # donor or recipient is the root branch itself
            continue
        if d not in side or g not in side:
            raise ValueError("unknown branch in token %s->%s (%s)" % (d, g, path))
        if side[d] == side[g]:
            continue                                   # within one domain
        if d in sset:
            x_stem_out += 1
        elif d in internal:
            x_int_out += 1
        else:
            x_term_out += 1
        if g in sset:
            x_stem_in += 1
    nonroot = [b for b in rows if b != r["root"]]
    rec = {
        "x_stem_out": x_stem_out / ns, "x_int_out": x_int_out / ns, "x_term_out": x_term_out / ns,
        "x_stem_in": x_stem_in / ns, "x_root_tok": x_root_tok / ns, "t_tokens": n_tok / ns,
        "pres_stem": sum(rows[s][2] for s in stems),
        "pres_int": sum(rows[b][2] for b in internal if b not in sset),
        "pres_term": sum(rows[b][2] for b in nonroot if b not in internal),
        "t_in_stem": sum(rows[s][0] for s in stems), "cop_stem": sum(rows[s][1] for s in stems),
        "t_in_all": sum(rows[b][0] for b in nonroot), "cop_all": sum(rows[b][1] for b in nonroot),
        "pres_root": rows[r["root"]][2],
        "t_in_stem_each": [rows[s][0] for s in stems], "cop_stem_each": [rows[s][1] for s in stems],
        "n_branches": len(rows),
    }
    if leaf_domain is not None:   # which domain each stem leads to (majority of its leaves)
        doms = []
        for c in r["clades"]:
            leaves = [x for x in c if x not in internal and x in leaf_domain]
            vals = [leaf_domain[x] for x in leaves]
            doms.append(max(set(vals), key=vals.count) if vals else "?")
            doms.append(round(vals.count(doms[-1]) / max(1, len(vals)), 4))
        rec["stem_domains"] = doms
    return rec


def world_measures(recs):
    def tot(k):
        return sum(r[k] for r in recs)
    i_stem = tot("x_stem_out") / tot("pres_stem") if tot("pres_stem") > 0 else float("nan")
    i_int = tot("x_int_out") / tot("pres_int") if tot("pres_int") > 0 else float("nan")
    r_stem = tot("t_in_stem") / tot("cop_stem") if tot("cop_stem") > 0 else float("nan")
    r_all = tot("t_in_all") / tot("cop_all") if tot("cop_all") > 0 else float("nan")
    return {"M1": i_stem / i_int if i_int > 0 else float("nan"), "I_stem": i_stem, "I_int": i_int,
            "M2": r_stem / r_all if r_all > 0 else float("nan"), "R_stem": r_stem, "R_all": r_all,
            "n_families": len(recs)}


if __name__ == "__main__":
    if sys.argv[1] == "parse":
        for p in sys.argv[2:]:
            print(json.dumps(family_record(p)))
