"""Parse central-directory entries from the tail of a zip fetched by HTTP range request.

Usage: python3 -I parse_zip_cd.py <tailfile>
Prints: name, compressed size, uncompressed size for each central-directory record found.
Treats the input as untrusted bytes: no extraction, no execution, names printed with repr-safe escaping.
"""
import struct
import sys

SIG = b"PK\x01\x02"


def main(path):
    data = open(path, "rb").read()
    off = 0
    n = 0
    total_u = 0
    while True:
        i = data.find(SIG, off)
        if i < 0:
            break
        off = i + 4
        if i + 46 > len(data):
            break
        (csize, usize, nlen, elen, clen) = struct.unpack_from("<II", data, i + 20) + struct.unpack_from("<HHH", data, i + 28)
        name = data[i + 46 : i + 46 + nlen]
        if len(name) < nlen:
            break
        n += 1
        total_u += usize
        print("%12d %12d  %s" % (csize, usize, name.decode("utf-8", "replace").encode("unicode_escape").decode()))
    print("# records found: %d, total uncompressed: %d" % (n, total_u))


if __name__ == "__main__":
    main(sys.argv[1])
