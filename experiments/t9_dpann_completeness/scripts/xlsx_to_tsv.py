"""T9: convert chosen sheets of Huang et al. 2026 Supplementary Data (xlsx, untrusted) to TSV, stdlib only.

Usage:
  python3 -I xlsx_to_tsv.py <xlsx> <out dir>                  # write sheets.txt (names only)
  python3 -I xlsx_to_tsv.py <xlsx> <out dir> 1 10 20          # also write sheetN.tsv for those sheets

Reads workbook.xml, its rels, sharedStrings.xml and the chosen worksheet XML parts through zipfile.
Nothing is evaluated; formula cells are written as their cached value. Output goes to the gitignored
cache/ (third-party data).
"""
import sys, os, re, zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PNS = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
MAXPART = 80_000_000


def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def main(src, out, wanted):
    os.makedirs(out, exist_ok=True)
    z = zipfile.ZipFile(src)
    for info in z.infolist():
        if info.file_size > MAXPART:
            sys.exit("part too large: %s" % info.filename)
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels.iter(PNS)}
    sheets = []
    for s in wb.find("m:sheets", NS):
        t = target[s.get(RNS)].lstrip("/")
        if not t.startswith("xl/"):
            t = "xl/" + t
        sheets.append((s.get("name"), t))
    with open(os.path.join(out, "sheets.txt"), "w", encoding="utf-8") as f:
        for i, (nm, t) in enumerate(sheets, 1):
            f.write("sheet%d\t%s\t%s\n" % (i, nm, t))
    if not wanted:
        return
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    for i in wanted:
        nm, part = sheets[i - 1]
        root = ET.fromstring(z.read(part))
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
            if vals:
                rows.append([vals.get(k, "") for k in range(max(vals) + 1)])
        with open(os.path.join(out, "sheet%d.tsv" % i), "w", encoding="utf-8") as f:
            for row in rows:
                f.write("\t".join(row) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], [int(a) for a in sys.argv[3:]])
