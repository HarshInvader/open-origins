"""Download Europe PMC full-text XML and supplementary files; write plain text. Usage: fetch_ft.py PMCID..."""
import sys, os, re, time, zipfile, io, subprocess, urllib.request
UA = {"User-Agent": "open-research-site/1.0"}
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "texts")
def get(url, binary=False):
    for i in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(4 * (i + 1))
        except Exception:
            time.sleep(4 * (i + 1))
    return None
def xml2txt(x):
    x = re.sub(r"<ref-list.*?</ref-list>", "", x, flags=re.S)
    x = re.sub(r"<title>(.*?)</title>", r"\n\n## \1\n", x, flags=re.S)
    x = re.sub(r"</p>|<break/>", "\n", x)
    x = re.sub(r"<[^>]+>", "", x)
    import html; x = html.unescape(x)
    return re.sub(r"\n{3,}", "\n\n", x)
for pmc in sys.argv[1:]:
    od = os.path.join(D, pmc); os.makedirs(od, exist_ok=True)
    if not os.path.exists(os.path.join(od, "main.txt")):
        x = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML")
        if x is None:
            x = get(f"https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:{pmc[3:]}&metadataPrefix=pmc")
        open(os.path.join(od, "main.txt"), "w").write(xml2txt(x.decode("utf8", "ignore")) if x else "FULLTEXT_UNAVAILABLE\n")
    if not os.path.exists(os.path.join(od, "si_status.txt")):
        z = get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/supplementaryFiles")
        st = "none"
        if z:
            try:
                zf = zipfile.ZipFile(io.BytesIO(z)); sd = os.path.join(od, "si"); os.makedirs(sd, exist_ok=True)
                for n in zf.namelist():
                    b = os.path.basename(n)
                    if not b: continue
                    if b.lower().endswith(".pdf"):
                        p = os.path.join(sd, b); open(p, "wb").write(zf.read(n))
                        subprocess.run(["pdftotext", "-layout", p, p[:-4] + ".txt"], capture_output=True); os.remove(p)
                    elif b.lower().endswith((".docx", ".doc", ".rtf")):
                        p = os.path.join(sd, b); open(p, "wb").write(zf.read(n))
                        subprocess.run(["textutil", "-convert", "txt", p, "-output", os.path.splitext(p)[0] + ".txt"], capture_output=True); os.remove(p)
                    elif b.lower().endswith((".txt", ".csv", ".xml")):
                        open(os.path.join(sd, b), "wb").write(zf.read(n))
                st = "open:" + ",".join(sorted(os.listdir(sd)))[:500]
            except zipfile.BadZipFile:
                st = "bad_zip"
        open(os.path.join(od, "si_status.txt"), "w").write(st + "\n")
    print(pmc, os.path.getsize(os.path.join(od, "main.txt")), open(os.path.join(od, "si_status.txt")).read().strip()[:80])
