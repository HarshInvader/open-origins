"""List the classes a pickle would import, without loading it (pickletools only; nothing is executed)."""
import sys, pickletools, collections
for p in sys.argv[1:]:
    data = open(p, "rb").read()
    head = data[:2]
    glob = collections.Counter()
    strs = []   # recent string pushes, to resolve STACK_GLOBAL
    ops = collections.Counter()
    try:
        for op, arg, pos in pickletools.genops(data):
            ops[op.name] += 1
            if op.name in ("SHORT_BINUNICODE", "BINUNICODE", "UNICODE", "BINUNICODE8"):
                strs.append(arg); strs = strs[-2:]
            elif op.name == "GLOBAL":
                glob[arg.replace(" ", ".")] += 1
            elif op.name == "STACK_GLOBAL":
                glob[".".join(strs[-2:])] += 1
            elif op.name == "STOP":
                break
    except Exception as e:
        print(p, "PARSE ERROR", repr(e)); continue
    print(p.split("/")[-1], "proto-byte", head.hex(), "globals:", dict(glob), "REDUCE", ops["REDUCE"], "BUILD", ops["BUILD"], "NEWOBJ", ops["NEWOBJ"])
