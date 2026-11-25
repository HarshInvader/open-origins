"""Flatten a JATS full-text XML (Europe PMC) to plain text, one paragraph per line. Stdlib only.
Usage: python -I xml2txt.py in.xml out.txt"""
import sys
import xml.etree.ElementTree as ET

BLOCK = {"p", "title", "label", "caption", "td", "th", "article-title", "abstract", "ref"}


def text(el):
    return " ".join("".join(el.itertext()).split())


def main(src, dst):
    root = ET.parse(src).getroot()
    out = []
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag in ("p", "title", "article-title", "td", "th", "mixed-citation", "element-citation"):
            t = text(el)
            if t:
                out.append(("## " if tag == "title" else "") + t)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
