#!/usr/bin/env python3
"""Literature helper: JATS XML -> plain text, one paragraph per line. Usage: xml2txt.py in.xml out.txt"""
import re, sys, html
x = open(sys.argv[1], encoding='utf-8', errors='replace').read()
x = re.sub(r'<ref-list.*?</ref-list>', '', x, flags=re.S)
x = re.sub(r'</(p|title|td|th|tr|caption|sec|abstract|article-title)>', '\n', x)
x = re.sub(r'<[^>]+>', ' ', x)
x = html.unescape(x)
lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in x.split('\n')]
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(l for l in lines if l))
