"""Print the shape of each deposit pickle (keys, types, lengths). Prints no activity value."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_pickle as sp

def shape(o, d=0, maxd=3):
    t = type(o).__name__
    if isinstance(o, dict):
        s = 'dict(n=%d, keytypes=%s)' % (len(o), sorted({type(k).__name__ for k in o}))
        if d < maxd:
            for k in list(o)[:4]:
                s += '\n' + '  ' * (d + 1) + repr(k)[:70] + ': ' + shape(o[k], d + 1, maxd)
        return s
    if isinstance(o, (list, tuple)):
        s = '%s(n=%d, types=%s)' % (t, len(o), sorted({type(x).__name__ for x in o}))
        if o and d < maxd:
            s += '\n' + '  ' * (d + 1) + '[0]: ' + shape(o[0], d + 1, maxd)
        return s
    if isinstance(o, str):
        return 'str(len=%d)' % len(o)
    return t

for f in sys.argv[1:]:
    print('==', os.path.basename(f)); print(shape(sp.load(f)))
