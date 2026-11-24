#!/usr/bin/env python3
"""Blind layout probe for Mojarro 2021 (PMC8248371). Prints section titles, the Methods text,
figure/table captions, table headers, and table bodies with every digit masked as '#'.
Prints no measured value. Run with python3 -I."""
import re, sys
x = open(sys.argv[1], encoding='utf-8').read()
strip = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()
print('TITLE:', strip(re.search(r'<article-title>(.*?)</article-title>', x, re.S).group(1)))
print('LICENSE:', strip(' '.join(re.findall(r'<license.*?</license>', x, re.S)))[:300])
body = x[x.index('<body'):]
print('\nSECTION TITLES:')
for t in re.findall(r'<title>(.*?)</title>', body, re.S): print('  -', strip(t)[:120])
print('\nMETHODS TEXT:')
for sec in re.findall(r'<sec[^>]*>\s*<title>(.*?)</title>(.*?)</sec>', body, re.S):
    if re.search(r'method|material|experimental', sec[0], re.I):
        print('##', strip(sec[0])); print(strip(sec[1])[:9000])
print('\nTABLES:')
for tw in re.findall(r'<table-wrap.*?</table-wrap>', x, re.S):
    print('LABEL:', strip(''.join(re.findall(r'<label>(.*?)</label>', tw, re.S))), '| CAPTION:', re.sub(r'\d', '#', strip(''.join(re.findall(r'<caption>(.*?)</caption>', tw, re.S))))[:600])
    for tr in re.findall(r'<tr.*?</tr>', tw, re.S):
        cells = [strip(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.S)]
        head = '<th' in tr
        print('  ', 'H' if head else 'B', ' | '.join(c if head else re.sub(r'\d', '#', c) for c in cells))
    print('  FOOT:', re.sub(r'\d', '#', strip(''.join(re.findall(r'<table-wrap-foot>(.*?)</table-wrap-foot>', tw, re.S))))[:500])
print('\nFIGURE CAPTIONS (digits masked):')
for f in re.findall(r'<fig .*?</fig>', x, re.S):
    print(' ', strip(''.join(re.findall(r'<label>(.*?)</label>', f, re.S))), ':', re.sub(r'\d', '#', strip(''.join(re.findall(r'<caption>(.*?)</caption>', f, re.S))))[:500])
print('\nSUPPLEMENTARY:', [strip(s)[:200] for s in re.findall(r'<supplementary-material.*?</supplementary-material>', x, re.S)])
