"""T12: convert the Janzen et al. 2022 Source Data workbook (xlsx, untrusted) to plain TSV, stdlib only.

Usage:  python3 -I xlsx_to_tsv.py <path to MOESM3_ESM.xlsx> <output dir>

Reads only the worksheet XML parts, the workbook relationship map and sharedStrings.xml through zipfile;
no macros, no external links, nothing evaluated.  Formula cells are written as their cached value.  Sheets
are matched to their parts through xl/_rels/workbook.xml.rels.  Output: sheetN.tsv for N = 1..6 in workbook
order, plus sheets.txt with the names.  The output dir (experiments/*/cache/) is gitignored: third-party data.
Adapted from experiments/t8_ameta_noise/scripts/xlsx_to_tsv.py (streaming parse; larger part limit).
"""
import sys, os, re, zipfile
import xml.etree.ElementTree as ET

M = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
MAXPART = 80_000_000  # refuse oversized parts (zip bombs); the largest real part is 52.7 MB


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
        for si in root.findall("{%s}si" % M):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % M)))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            .findall("{%s}Relationship" % PR)}
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    sheets = [(s.get("name"), rels[s.get("{%s}id" % R)]) for s in wb.find("{%s}sheets" % M)]
    with open(os.path.join(out, "sheets.txt"), "w", encoding="utf-8") as f:
        for i, (nm, tgt) in enumerate(sheets, 1):
            f.write("sheet%d\t%s\t%s\n" % (i, nm, tgt))
    for i, (nm, tgt) in enumerate(sheets, 1):
        part = "xl/" + tgt.lstrip("/").replace("xl/", "", 1) if not tgt.startswith("xl/") else tgt
        nrow = 0
        with z.open(part) as fh, open(os.path.join(out, "sheet%d.tsv" % i), "w", encoding="utf-8") as fo:
            for ev, el in ET.iterparse(fh, events=("end",)):
                if el.tag != "{%s}row" % M:
                    continue
                vals = {}
                for c in el.findall("{%s}c" % M):
                    t = c.get("t")
                    v = c.find("{%s}v" % M)
                    if t == "s" and v is not None:
                        val = shared[int(v.text)]
                    elif t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter("{%s}t" % M))
                    else:
                        val = v.text if (v is not None and v.text is not None) else ""
                    vals[col_index(c.get("r"))] = val.replace("\t", " ").replace("\n", " ").replace("\r", " ")
                width = max(vals) + 1 if vals else 0
                fo.write("\t".join(vals.get(k, "") for k in range(width)) + "\n")
                nrow += 1
                el.clear()
        print("sheet%d" % i, nm, "rows", nrow)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
