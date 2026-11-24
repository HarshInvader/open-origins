#!/usr/bin/env python3
"""Literature helper: print context windows around regex hits. Usage: kw.py file.txt 'regex' [before after maxhits]"""
import re, sys
t = open(sys.argv[1], encoding='utf-8').read().replace('\n', ' ¶ ')
b = int(sys.argv[3]) if len(sys.argv) > 3 else 250; a = int(sys.argv[4]) if len(sys.argv) > 4 else 350; mx = int(sys.argv[5]) if len(sys.argv) > 5 else 12
last = -10**9; n = 0
for m in re.finditer(sys.argv[2], t, flags=re.I):
    if m.start() < last: continue
    print(f'[{m.start()}] …' + t[max(0, m.start() - b): m.end() + a] + '…\n'); last = m.end() + a; n += 1
    if n >= mx: break
