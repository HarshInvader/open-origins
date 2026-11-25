"""List the central directory of a remote zip from a downloaded tail (no full download).

Usage: python -I t18b_zipdir.py <tail_file> <total_size>
Prints name, compressed size, uncompressed size, local header offset, method for each member.
"""
import struct
import sys

tail_path, total = sys.argv[1], int(sys.argv[2])
buf = open(tail_path, "rb").read()
base = total - len(buf)
eocd = buf.rfind(b"PK\x05\x06")
n = struct.unpack("<H", buf[eocd + 10:eocd + 12])[0]
cd_size, cd_off = struct.unpack("<II", buf[eocd + 12:eocd + 20])
z64 = buf.rfind(b"PK\x06\x06")
if z64 >= 0:
    n, cd_size, cd_off = struct.unpack("<QQQ", buf[z64 + 32:z64 + 56])
p = cd_off - base
if p < 0:
    sys.exit(f"central directory starts before the tail (need {-p} more bytes)")
for _ in range(n):
    assert buf[p:p + 4] == b"PK\x01\x02"
    method = struct.unpack("<H", buf[p + 10:p + 12])[0]
    csz, usz = struct.unpack("<II", buf[p + 20:p + 28])
    ln, le, lc = struct.unpack("<HHH", buf[p + 28:p + 34])
    off = struct.unpack("<I", buf[p + 42:p + 46])[0]
    name = buf[p + 46:p + 46 + ln].decode("utf-8", "replace")
    extra = buf[p + 46 + ln:p + 46 + ln + le]
    q = 0
    while q + 4 <= len(extra):
        hid, hl = struct.unpack("<HH", extra[q:q + 4])
        if hid == 1:
            vals = list(struct.unpack("<" + "Q" * (hl // 8), extra[q + 4:q + 4 + 8 * (hl // 8)]))
            if usz == 0xFFFFFFFF:
                usz = vals.pop(0)
            if csz == 0xFFFFFFFF:
                csz = vals.pop(0)
            if off == 0xFFFFFFFF:
                off = vals.pop(0)
        q += 4 + hl
    print(f"{name}\t{csz}\t{usz}\t{off}\t{method}")
    p += 46 + ln + le + lc
