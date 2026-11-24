# Blind probe of MARHYS: prints text of the label rows only (rows before data), never numeric cells.
import zipfile,re,sys
z=zipfile.ZipFile(sys.argv[1])
ss=z.read('xl/sharedStrings.xml').decode('utf-8','replace')
S=[re.sub(r'<[^>]+>','',m) for m in re.findall(r'<si>(.*?)</si>',ss,flags=re.S)]
with z.open('xl/worksheets/sheet1.xml') as f: head=f.read(4_000_000).decode('utf-8','replace')
rows=re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>',head,flags=re.S)
for rn,body in rows[:40]:
    cells=re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(?:<f>.*?</f>)?(?:<v>(.*?)</v>)?</c>)',body,flags=re.S)
    strs=[(c,S[int(v)]) for c,a,v in cells if 't="s"' in a and v]
    nnum=sum(1 for c,a,v in cells if 't="s"' not in a and v)
    print('ROW',rn,'nstr',len(strs),'nnum',nnum)
    if nnum==0 and strs:
        print('   ',' | '.join(f'{c}:{s[:40]}' for c,s in strs))
