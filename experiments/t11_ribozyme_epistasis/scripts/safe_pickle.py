"""Restricted unpickler for the mut_12 deposit (untrusted pickles).

The deposit's pickles hold only builtin containers (checked opcode by opcode with pickletools: no GLOBAL,
STACK_GLOBAL, REDUCE, BUILD or NEWOBJ).  So find_class allows nothing at all: any attempt to import a class or
call a function raises.  Never use plain pickle.load on these files.
"""
import pickle, io

ALLOWED = frozenset()          # no class or function may be resolved


class Restricted(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in ALLOWED:
            return super().find_class(module, name)
        raise pickle.UnpicklingError("refused global %s.%s" % (module, name))

    def persistent_load(self, pid):
        raise pickle.UnpicklingError("refused persistent id")


def load(path):
    with open(path, "rb") as f:
        return Restricted(io.BytesIO(f.read())).load()
