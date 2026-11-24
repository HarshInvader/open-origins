# Europe PMC helpers. User-Agent open-research-site/1.0. No personal data in requests.
UA="open-research-site/1.0"
q() { curl -s --max-time 40 -A "$UA" --get "https://www.ebi.ac.uk/europepmc/webservices/rest/search" --data-urlencode "query=$1" --data-urlencode "format=json" --data-urlencode "pageSize=${2:-8}" --data-urlencode "resultType=lite" | python3 -I -c "
import sys,json
try: d=json.load(sys.stdin)
except Exception as e: print('ERR',e); sys.exit()
print('HITS',d.get('hitCount'))
for r in d['resultList']['result']:
    print(' ',r.get('pubYear'),'|',r.get('authorString','')[:40],'|',r.get('title','')[:150],'|',r.get('doi'),'|',r.get('pmcid'),'| OA',r.get('isOpenAccess'),'| c',r.get('citedByCount'))
"; }
ft() { curl -s --max-time 60 -A "$UA" -o "$2/$1.xml" -w "$1 %{http_code} %{size_download}\n" "https://www.ebi.ac.uk/europepmc/webservices/rest/$1/fullTextXML"; }
