import json, csv, sys, time, urllib.request, urllib.parse
UA={"User-Agent":"open-research-site/1.0"}
name=sys.argv[1]; N=int(sys.argv[2])
rows=list(csv.DictReader(open(f"frame_{name}.csv")))[:N]
out={}
for i in range(0,len(rows),20):
    ids=" OR ".join(f'PMCID:{r["pmcid"]}' for r in rows[i:i+20])
    u="https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urllib.parse.urlencode({"query":ids,"format":"json","pageSize":100,"resultType":"core"})
    for k in range(8):
        try: r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90)); break
        except Exception: time.sleep(5*(k+1))
    for x in r["resultList"]["result"]:
        out[x.get("pmcid")]={"abs":x.get("abstractText",""),"pt":x.get("pubTypeList",{}).get("pubType",[])}
json.dump(out,open(f"abs_{name}.json","w"))
import re
for r in rows:
    a=out.get(r["pmcid"],{}).get("abs","")
    a=re.sub("<[^>]+>","",a)
    print(r["rank"],r["pmcid"],r["year"],"|",r["title"][:110],"||",a[:260].replace("\n"," "))
