import sys,re
import xml.etree.ElementTree as ET
t=ET.parse(sys.argv[1]).getroot()
body=t.find('.//body')
def walk(e,out):
    if e.tag in('sec',):
        tt=e.find('title')
        if tt is not None: out.append('\n## '+''.join(tt.itertext()))
        for c in e:
            if c.tag!='title': walk(c,out)
    elif e.tag in ('p','caption','title','label'):
        out.append(' '.join(''.join(e.itertext()).split()))
    else:
        for c in e: walk(c,out)
out=[]
ab=t.find('.//abstract')
if ab is not None: out.append('ABSTRACT: '+' '.join(''.join(ab.itertext()).split()))
walk(body if body is not None else t,out)
for bk in t.findall('.//back//sec'):
    walk(bk,out)
print('\n'.join(out))
