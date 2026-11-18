"""Strip tags and print sentences matching a regex. Usage: txt.py FILE REGEX"""
import sys, re, html
t = html.unescape(re.sub(r"<[^>]+>", " ", open(sys.argv[1], encoding="utf-8", errors="ignore").read()))
t = re.sub(r"\s+", " ", t)
for s in re.split(r"(?<=[.!?])\s+", t):
    if re.search(sys.argv[2], s, re.I) and len(s) < 1200: print("-", s)
