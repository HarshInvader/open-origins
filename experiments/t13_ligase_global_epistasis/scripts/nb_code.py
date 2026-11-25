"""Print only the source of code cells of a Jupyter notebook (never its outputs). Stdlib only.
Usage: python3 -I nb_code.py notebook.ipynb"""
import json, sys
nb = json.load(open(sys.argv[1], encoding="utf-8"))
for i, c in enumerate(nb.get("cells", [])):
    if c.get("cell_type") == "code":
        src = "".join(c.get("source", []))
        if src.strip():
            print("# --- cell %d" % i)
            print(src)
