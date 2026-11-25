"""List a remote zip's central directory by HTTP range request, and pull single members.

No part of the archive is downloaded except the directory and the members asked for.
Stdlib only.  User-Agent is a generic client name; no personal details are sent.

Usage:
  python3 -I zip_fetch.py list <url> <out_dir>                   # writes <out_dir>/zip_listing.tsv
  python3 -I zip_fetch.py get  <url> <out_dir> <member> [<member> ...]

Members are written under <out_dir> with their basename only (no directory traversal).
Each written file's sha256 and byte size are printed and appended to <out_dir>/sha256.tsv.
"""
import hashlib
import os
import struct
import sys
import urllib.request
import zlib

UA = {"User-Agent": "open-research-site/1.0"}


def fetch(url, start, end):
    """bytes [start, end] inclusive."""
    req = urllib.request.Request(url, headers=dict(UA, Range="bytes=%d-%d" % (start, end)))
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def total_size(url):
    req = urllib.request.Request(url, headers=dict(UA, Range="bytes=0-0"))
    with urllib.request.urlopen(req, timeout=120) as r:
        cr = r.headers["Content-Range"]
    return int(cr.split("/")[1])


def central_dir(url):
    n = total_size(url)
    tail = fetch(url, max(0, n - 65557), n - 1)
    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        raise SystemExit("no end-of-central-directory record found")
    cd_size, cd_off = struct.unpack("<II", tail[i + 12:i + 20])
    if cd_off == 0xFFFFFFFF or cd_size == 0xFFFFFFFF:
        raise SystemExit("zip64 central directory; not handled")
    cd = fetch(url, cd_off, cd_off + cd_size - 1)
    out, p = [], 0
    while p + 46 <= len(cd) and cd[p:p + 4] == b"PK\x01\x02":
        (method, _t, _d, crc, csize, usize, nlen, elen, clen,
         _disk, _ia, _ea, lho) = struct.unpack("<HHHIIIHHHHHII", cd[p + 10:p + 46])
        name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
        out.append({"name": name, "method": method, "crc": crc, "csize": csize,
                    "usize": usize, "lho": lho})
        p += 46 + nlen + elen + clen
    return n, out


def member_bytes(url, e):
    head = fetch(url, e["lho"], e["lho"] + 29)
    if head[:4] != b"PK\x03\x04":
        raise SystemExit("bad local header for " + e["name"])
    nlen, elen = struct.unpack("<HH", head[26:30])
    start = e["lho"] + 30 + nlen + elen
    raw = fetch(url, start, start + e["csize"] - 1)
    if e["method"] == 0:
        data = raw
    elif e["method"] == 8:
        data = zlib.decompressobj(-15).decompress(raw)
    else:
        raise SystemExit("compression method %d not handled" % e["method"])
    if len(data) != e["usize"] or (zlib.crc32(data) & 0xFFFFFFFF) != e["crc"]:
        raise SystemExit("size or crc mismatch for " + e["name"])
    return data


def main():
    mode, url, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)
    n, entries = central_dir(url)
    if mode == "list":
        p = os.path.join(out_dir, "zip_listing.tsv")
        with open(p, "w", encoding="utf-8") as f:
            f.write("zip_bytes\t%d\tentries\t%d\n" % (n, len(entries)))
            f.write("name\tcompressed\tuncompressed\tmethod\n")
            for e in sorted(entries, key=lambda x: x["name"]):
                f.write("%s\t%d\t%d\t%d\n" % (e["name"], e["csize"], e["usize"], e["method"]))
        print("zip bytes %d, %d entries -> %s" % (n, len(entries), p))
        return
    if mode != "get":
        raise SystemExit("unknown mode")
    index = {e["name"]: e for e in entries}
    for want in sys.argv[4:]:
        e = index.get(want)
        if e is None:
            raise SystemExit("member not in archive: " + want)
        data = member_bytes(url, e)
        base = os.path.basename(want)
        if not base or base.startswith("."):
            raise SystemExit("refusing name " + want)
        dst = os.path.join(out_dir, base)
        with open(dst, "wb") as f:
            f.write(data)
        h = hashlib.sha256(data).hexdigest()
        with open(os.path.join(out_dir, "sha256.tsv"), "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%d\t%s\n" % (h, base, len(data), want))
        print("%s  %s  %d bytes" % (h, base, len(data)))


if __name__ == "__main__":
    main()
