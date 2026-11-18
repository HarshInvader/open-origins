"""Europe PMC abstract by DOI. Usage: epmc.py DOI..."""
import sys, json, urllib.request, urllib.parse, re, time
for d in sys.argv[1:]:
    time.sleep(0.5)
    u = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?resultType=core&format=json&query=" + urllib.parse.quote(f'DOI:"{d}"')
    r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "citation-checker/0.1"}), timeout=30))
    res = r["resultList"]["result"]
    if not res: print(d, "NOT IN EPMC\n"); continue
    m = res[0]
    print(d, "|", m.get("authorString", "")[:200], "|", m.get("journalInfo", {}).get("printPublicationDate"), m.get("firstPublicationDate"))
    print("  ", m.get("title"))
    print("   ABS:", re.sub("<[^>]+>", "", m.get("abstractText", "(none)")))
    print()
