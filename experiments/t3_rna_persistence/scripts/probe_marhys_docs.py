"""Print MARHYS's own documentation text (rows 2-8 of the sheet: title, note, column explanations). No data rows."""
import zipfile, re, sys
z = zipfile.ZipFile(sys.argv[1])
ss = z.read('xl/sharedStrings.xml').decode('utf-8', 'replace')
S = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', ss, flags=re.S)]
with z.open('xl/worksheets/sheet1.xml') as f: head = f.read(2_000_000).decode('utf-8', 'replace')
want = set(sys.argv[2:])
for rn, body in re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>', head, flags=re.S):
    if int(rn) > 8: break
    for c, a, v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(?:<f>.*?</f>)?(?:<v>(.*?)</v>)?</c>)', body, flags=re.S):
        if 't="s"' in a and v and S[int(v)].strip() and (not want or c in want or int(rn) < 8):
            print(f'[{c}{rn}]', re.sub(r'\s+', ' ', S[int(v)]).replace('&amp;','&'), '\n')
