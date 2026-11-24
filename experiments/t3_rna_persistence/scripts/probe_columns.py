# Blind probe: prints column names and non-empty counts only. No values.
import csv,sys,zipfile,re
def csvprobe(p):
    with open(p,newline='',encoding='utf-8',errors='replace') as f:
        r=csv.reader(f); rows=list(r)
    # find header row = first row with >10 non-empty cells
    hi=next(i for i,row in enumerate(rows) if sum(1 for c in row if c.strip())>10)
    h=rows[hi]; body=rows[hi+1:]
    print(p.split('/')[-1],'header row',hi,'ncols',len(h),'nrows',len(body))
    for j,name in enumerate(h):
        n=sum(1 for row in body if j<len(row) and row[j].strip() not in('','--','NA','na','nd'))
        if re.search(r'(?i)temp|^pH|ph\b|\bMg|magnes|\bK\b|potass|\bNa\b|sodium|\bCa\b|calc|\bFe|type|feature|site|area|date|cond|lat|lon|SiO|Cl\b|SO4|alk',name) or j<12:
            print(f'  [{j}] {name!r}  nonempty={n}')
def xlsxprobe(p):
    z=zipfile.ZipFile(p)
    wb=z.read('xl/workbook.xml').decode('utf-8','replace')
    print('sheets:',re.findall(r'<sheet [^>]*name="([^"]+)"',wb))
    print('members:',[(i.filename,i.file_size) for i in z.infolist() if 'sheet' in i.filename])
for a in sys.argv[1:]:
    (xlsxprobe if a.endswith('.xlsx') else csvprobe)(a)
