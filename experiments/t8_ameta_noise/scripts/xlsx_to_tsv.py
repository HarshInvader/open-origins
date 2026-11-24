"""T8: convert Ameta et al. 2021 Supplementary Data 2 (xlsx, untrusted) to plain TSV, stdlib only.

Usage:  python3 -I xlsx_to_tsv.py <path to MOESM4_ESM.xlsx> <output dir>

Reads only the four worksheet XML parts and sharedStrings.xml through zipfile; no macros, no external
links, nothing evaluated.  Formula cells are written as their cached value.  Output: one TSV per sheet,
named sheet1.tsv ... sheet4.tsv, plus sheets.txt with the sheet names.  The output dir is gitignored
(experiments/*/cache/): this is third-party data.
"""
import sys, os, re, zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
MAXPART = 50_000_000  # refuse oversized parts (zip bombs)


def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def main(src, out):
    os.makedirs(out, exist_ok=True)
    z = zipfile.ZipFile(src)
    for info in z.infolist():
        if info.file_size > MAXPART:
            sys.exit("part too large: %s" % info.filename)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    names = [s.get("name") for s in wb.find("m:sheets", NS)]
    with open(os.path.join(out, "sheets.txt"), "w", encoding="utf-8") as f:
        for i, nm in enumerate(names, 1):
            f.write("sheet%d\t%s\n" % (i, nm))
    for i in range(1, len(names) + 1):
        root = ET.fromstring(z.read("xl/worksheets/sheet%d.xml" % i))
        rows = []
        for r in root.iter("{%s}row" % NS["m"]):
            vals = {}
            for c in r.findall("m:c", NS):
                t = c.get("t")
                v = c.find("m:v", NS)
                if t == "s" and v is not None:
                    val = shared[int(v.text)]
                elif t == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
                else:
                    val = v.text if v is not None else ""
                vals[col_index(c.get("r"))] = val.replace("\t", " ").replace("\n", " ")
            width = max(vals) + 1 if vals else 0
            rows.append([vals.get(k, "") for k in range(width)])
        with open(os.path.join(out, "sheet%d.tsv" % i), "w", encoding="utf-8") as f:
            for row in rows:
                f.write("\t".join(row) + "\n")
        print("sheet%d" % i, names[i - 1], "rows", len(rows))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
