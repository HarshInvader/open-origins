#!/usr/bin/env python3
"""Prints four Methods subsections of Mojarro 2021 (conditions only) and the first column of Table 1.
No Results text, no rate cell. Run with python3 -I."""
import re, sys
x = open(sys.argv[1], encoding='utf-8').read()
strip = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()
for name in ('RNA‐containing oligomer', 'Mars prebiotic geochemical solutions', 'RNA degradation quantification', 'RNA degradation kinetics'):
    i = x.index('<title>' + name + '</title>')
    j = x.index('</sec>', i)
    print('##', name); print(strip(x[i:j])); print()
tw = re.findall(r'<table-wrap.*?</table-wrap>', x, re.S)[0]
print('TABLE 1 FIRST COLUMN:', [strip(re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.S)[0]) for tr in re.findall(r'<tr.*?</tr>', tw, re.S)[2:]])
