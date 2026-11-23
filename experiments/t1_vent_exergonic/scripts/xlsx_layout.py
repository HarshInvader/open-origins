"""Blind layout probe for an xlsx: sheet names, sizes and the first N rows with every
numeric-looking cell replaced by '<num>'. Used so result tables can be described
without their values being seen. Usage: python3 -I xlsx_layout.py file.xlsx [nrows]"""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_dump import read  # noqa: E402

NUM = re.compile(r'^\s*[-+−]?\d+([.,]\d+)?([eE][-+]?\d+)?\s*$')

def mask(v):
    return '<num>' if NUM.match(v or '') else v

def main():
    path = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    for name, rows in read(path):
        ncol = max((len(r) for r in rows), default=0)
        print(f'== sheet {name!r}: {len(rows)} rows x {ncol} cols')
        for r in rows[:n]:
            print('\t'.join(mask(c)[:60] for c in r))

if __name__ == '__main__':
    main()
