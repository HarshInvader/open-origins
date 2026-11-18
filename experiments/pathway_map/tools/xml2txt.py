"""Strip tags from an untrusted XML/HTML file to plain text (no execution). Usage: xml2txt.py in out"""
import re, sys, html
s = open(sys.argv[1], encoding="utf-8", errors="replace").read()
s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
s = re.sub(r"</(p|title|sec|caption|tr|li|h\d|div)>", "\n", s)
s = re.sub(r"<[^>]+>", " ", s)
s = html.unescape(s)
s = re.sub(r"[ \t]+", " ", s)
s = re.sub(r"\n\s*\n+", "\n", s)
open(sys.argv[2], "w").write(s)
