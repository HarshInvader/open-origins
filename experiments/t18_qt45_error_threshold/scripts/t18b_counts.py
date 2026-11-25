"""T18b: per-replicate read counts for QT45's HD<=3 variants, streamed from the Zenodo deposit (nothing large on disk).

Source: Zenodo 10.5281/zenodo.13891380, optimized_fitness_landscape_zenodo.zip, QT45/collapsed_reads/
{in_nodel, out_nodel_A, out_nodel_B, out_nodel_C}.fasta (headers '>id-count'; the authors reverse-complement each
44-nt read, see their fitness_landscape_analysis.ipynb, read_fasta_files_into_dictionary).

Each member is fetched with an HTTP range request and inflated on the fly; only counts are kept.
Outputs (in <outdir>, gitignored raw/):
  counts_hd012_<lib>.tsv  lib, genotype (WT orientation, 'pos:base,...' with pos = QT45 position 2..45), count
  counts_hd3_<lib>.tsv    same for HD = 3  (BLIND: not read by any T18b planted or calibration code)
  totals.json       total length-44 reads per library (the authors' counts_total), member sizes

Usage (from experiments/): python -I t18_qt45_error_threshold/scripts/t18b_counts.py <tail_file> <outdir> [lib,lib,...]
The tail file is the last 2 MB of the zip (holds the central directory).
"""
import json
import os
import struct
import sys
import urllib.request
import zlib

import numpy as np

URL = "https://zenodo.org/api/records/13891380/files/optimized_fitness_landscape_zenodo.zip/content"
TOTAL = 864422795
UA = "open-research-site/1.0"
LIBS = ["out_nodel_A", "out_nodel_B", "out_nodel_C", "in_nodel"]
WT_SEQ = "GCAGGGCAGCGCAGTCGGACATTGATAACGGAATCGAGCCCGCC"
COMP = bytes.maketrans(b"ACGT", b"TGCA")
RCWT = np.frombuffer(WT_SEQ.encode().translate(COMP)[::-1], dtype=np.uint8)
L = 44


def central_dir(tail):
    buf = open(tail, "rb").read()
    base = TOTAL - len(buf)
    eocd = buf.rfind(b"PK\x05\x06")
    n = struct.unpack("<H", buf[eocd + 10:eocd + 12])[0]
    cd_size, cd_off = struct.unpack("<II", buf[eocd + 12:eocd + 20])
    p = cd_off - base
    out = {}
    for _ in range(n):
        csz, usz = struct.unpack("<II", buf[p + 20:p + 28])
        ln, le, lc = struct.unpack("<HHH", buf[p + 28:p + 34])
        off = struct.unpack("<I", buf[p + 42:p + 46])[0]
        name = buf[p + 46:p + 46 + ln].decode()
        out[name] = (csz, usz, off)
        p += 46 + ln + le + lc
    return out


def stream_member(csz, off):
    # local header: 30 bytes + name + extra
    req = urllib.request.Request(URL, headers={"User-Agent": UA, "Range": f"bytes={off}-{off + 29}"})
    h = urllib.request.urlopen(req, timeout=120).read()
    ln, le = struct.unpack("<HH", h[26:30])
    start = off + 30 + ln + le
    end = start + csz - 1
    pos = start
    d = zlib.decompressobj(-15)
    tries = 0
    # range requests in 64 MB pieces; a short or failed read resumes from the last byte received
    while pos <= end:
        stop = min(pos + (64 << 20) - 1, end)
        try:
            req = urllib.request.Request(URL, headers={"User-Agent": UA, "Range": f"bytes={pos}-{stop}"})
            r = urllib.request.urlopen(req, timeout=300)
            while True:
                chunk = r.read(1 << 22)
                if not chunk:
                    break
                pos += len(chunk)
                yield d.decompress(chunk)
        except Exception as exc:  # noqa: BLE001
            tries += 1
            print(f"  resume at {pos} after {exc!r}", flush=True)
            if tries > 20:
                raise
    if pos != end + 1:
        raise RuntimeError(f"short member: got {pos - start} of {csz} bytes")
    yield d.flush()
    if not d.eof:
        raise RuntimeError("deflate stream did not end")


def label(seq_rc_arr, diff_idx):
    # seq in file orientation; genotype in WT orientation: position k in WT = L-1-k in file
    lab = []
    for k in sorted(L - 1 - int(i) for i in diff_idx):
        b = chr(COMP[seq_rc_arr[L - 1 - k]])
        lab.append(f"{k + 2}:{b}")
    return ",".join(lab)


def process(lib, gen, f012, f3):
    total = 0
    nrec = 0
    rest = b""
    heads, seqs = [], []

    def flush():
        nonlocal heads, seqs
        if not seqs:
            return
        arr = np.frombuffer(b"".join(seqs), dtype=np.uint8).reshape(-1, L)
        hd = (arr != RCWT).sum(1)
        for r in np.nonzero(hd <= 3)[0]:
            lab = label(arr[r], np.nonzero(arr[r] != RCWT)[0]) or "WT"
            (f012 if hd[r] <= 2 else f3).write(f"{lib}\t{lab}\t{heads[r]}\n")
        heads, seqs = [], []

    for block in gen:
        data = rest + block
        lines = data.split(b"\n")
        rest = lines.pop()
        # records are header/sequence pairs; keep an odd trailing header for the next block
        i = 0
        while i + 1 < len(lines):
            hline, s = lines[i], lines[i + 1].rstrip(b"\r")
            if not hline.startswith(b">"):
                i += 1
                continue
            nrec += 1
            if len(s) == L:
                c = int(hline.rsplit(b"-", 1)[1])
                total += c
                heads.append(c)
                seqs.append(s)
            i += 2
        if i < len(lines):
            rest = b"\n".join(lines[i:]) + b"\n" + rest
        if len(seqs) > 500000:
            flush()
    flush()
    return total, nrec


def main():
    tail, outdir = sys.argv[1], sys.argv[2]
    libs = sys.argv[3].split(",") if len(sys.argv) > 3 else LIBS
    os.makedirs(outdir, exist_ok=True)
    cd = central_dir(tail)
    tp = os.path.join(outdir, "totals.json")
    totals = json.load(open(tp)) if os.path.exists(tp) else {}
    for lib in libs:
        with open(os.path.join(outdir, f"counts_hd012_{lib}.tsv"), "w") as f012, \
                open(os.path.join(outdir, f"counts_hd3_{lib}.tsv"), "w") as f3:
            name = f"optimized_fitness_landscape_zenodo/QT45/collapsed_reads/{lib}.fasta"
            csz, usz, off = cd[name]
            tot, nrec = process(lib, stream_member(csz, off), f012, f3)
            totals[lib] = dict(total_len44_reads=tot, n_records=nrec, compressed=csz, uncompressed=usz)
            print(lib, totals[lib], flush=True)
        with open(tp, "w") as fh:
            json.dump(totals, fh, indent=1)


if __name__ == "__main__":
    main()
