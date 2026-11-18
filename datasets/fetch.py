"""Get the public datasets this project uses, on your own machine. Everything lands in datasets/local/, which git ignores.

    python3 -I datasets/fetch.py list                 # the catalogue, by tier
    python3 -I datasets/fetch.py fetch <id>           # one dataset we use, as the subset our results need
    python3 -I datasets/fetch.py index <id>           # file list only (Zenodo, figshare, Dryad, zip directory): no data
    python3 -I datasets/fetch.py meta <id>            # request-tier and reference-only sets: what it is and how to ask

Budget: the whole project may download 1.5 GB. Several sources are far larger (Marshall 2021's zip is 1.28 GB, the QT45
Dryad deposit 140 GB), so `fetch` reads only the members it needs from inside remote zips with HTTP range requests.
It refuses to download more than the budget left. One request per second. Nothing fetched here is republished.
"""
import csv, json, struct, sys, time, urllib.parse, urllib.request, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "datasets"
LOCAL = HERE / "local"
UA = {"User-Agent": "open-origins-dataset-fetch (+https://github.com/HarshInvader/open-origins)"}
BUDGET = 1.5e9

# id -> how to get the subset our results use.
#   ("file", url, name)                              one small file
#   ("zip", url, [member prefixes])                  only these members of a remote zip, by range reads
#   ("figshare", article_id, version, file name)     one file of a figshare article
#   ("zenodo", record_id, [file names])              chosen files of a Zenodo record
#   ("git", url)                                     shallow clone
#   ("manual", url, instructions)                    too large or nested to fetch within budget: printed, not run
RECIPES = {
    "rhea": ("file", "https://ftp.expasy.org/databases/rhea/tsv/rhea-chebi-smiles.tsv", "rhea-chebi-smiles.tsv"),
    "xavier2020_s4": ("figshare", 11872260, 2, "rspb20192377_si_005.txt"),
    # The deposit is a 1.28 GB zip holding three PDFs and one deflated 1.27 GB inner zip, so range reads cannot reach the
    # folders inside it. Fetching it costs most of the budget: do it by hand, keep the two folders, delete the zip.
    "marshall2021": ("manual", "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-021-23258-x/MediaObjects/41467_2021_23258_MOESM2_ESM.zip",
                     "Download the zip (1.28 GB). Unzip the inner 287799_0_data_set_*.zip and keep only README.md, "
                     "'Figure_2- MA in Chemical Space' and 'Figure_4 - Mixtures' (about 9 MB) in datasets/local/marshall2021/. Delete both zips."),
    "daymude_at": ("git", "https://github.com/DaymudeLab/assembly-theory.git"),
    "qt45_zenodo": ("zenodo", 13891380, ["quasispecies.zip"]),
}


def catalog():
    return list(csv.DictReader(open(HERE / "catalog.csv", encoding="utf-8")))


def row(i):
    r = {x["id"]: x for x in catalog()}.get(i)
    if not r:
        sys.exit(f"no catalogue id {i!r}; see `fetch.py list`")
    return r


def req(url, rng=None):
    time.sleep(1.0)
    h = dict(UA)
    if rng:
        h["Range"] = f"bytes={rng[0]}-{rng[1]}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120)


def get(url, rng=None):
    return req(url, rng).read()


def get_json(url):
    return json.loads(get(url))


def used_bytes():
    return sum(p.stat().st_size for p in LOCAL.rglob("*") if p.is_file()) if LOCAL.exists() else 0


def spend(n, what):
    left = BUDGET - used_bytes()
    if n > left:
        sys.exit(f"{what}: {n / 1e6:.0f} MB would exceed the 1.5 GB budget ({left / 1e6:.0f} MB left in datasets/local/)")


def size_of(url):
    r = req(url, (0, 0))
    cr = r.headers.get("Content-Range", "")
    return int(cr.split("/")[-1]) if "/" in cr else int(r.headers.get("Content-Length", 0))


# ---- remote zip, read by range
def zip_directory(url):
    """Central directory of a remote zip, read with two or three range requests. Returns [(name, offset, csize, method)]."""
    total = size_of(url)
    tail = get(url, (max(0, total - 66000), total - 1))
    i = tail.rfind(b"PK\x05\x06")
    cd_size, cd_off = struct.unpack("<II", tail[i + 12:i + 20])
    if cd_off == 0xFFFFFFFF:  # zip64
        j = tail.rfind(b"PK\x06\x06")
        cd_size, cd_off = struct.unpack("<QQ", tail[j + 40:j + 56])
    cd = get(url, (cd_off, cd_off + cd_size - 1))
    out, p = [], 0
    while p < len(cd) and cd[p:p + 4] == b"PK\x01\x02":
        method, = struct.unpack("<H", cd[p + 10:p + 12])
        csize, usize, nlen, xlen, clen = struct.unpack("<IIHHH", cd[p + 20:p + 34])
        off, = struct.unpack("<I", cd[p + 42:p + 46])
        name = cd[p + 46:p + 46 + nlen].decode("utf-8", "replace")
        extra = cd[p + 46 + nlen:p + 46 + nlen + xlen]
        if 0xFFFFFFFF in (csize, usize, off):  # zip64 extra field
            q, vals = 0, []
            while q < len(extra):
                hid, ln = struct.unpack("<HH", extra[q:q + 4])
                if hid == 1:
                    vals = list(struct.unpack("<" + "Q" * (ln // 8), extra[q + 4:q + 4 + ln - ln % 8]))
                q += 4 + ln
            if usize == 0xFFFFFFFF and vals: usize = vals.pop(0)
            if csize == 0xFFFFFFFF and vals: csize = vals.pop(0)
            if off == 0xFFFFFFFF and vals: off = vals.pop(0)
        out.append((name, off, csize, method, usize))
        p += 46 + nlen + xlen + clen
    return total, out


def zip_member(url, off, csize, method):
    head = get(url, (off, off + 29))
    nlen, xlen = struct.unpack("<HH", head[26:30])
    start = off + 30 + nlen + xlen
    data = get(url, (start, start + csize - 1)) if csize else b""
    return zlib.decompress(data, -15) if method == 8 else data


# ---- commands
def cmd_list():
    rows = catalog()
    for tier, label in (("included", "In this repository (datasets/open/)"), ("fetch", "Public: fetch a subset or follow the link"),
                        ("request", "On request: metadata only here"), ("reference-only", "Not reusable as data, or web-only")):
        sel = [r for r in rows if r["tier"] == tier]
        print(f"\n{label}: {len(sel)}")
        for r in sel:
            flag = ("*" if r["used_by_us"] == "yes" else " ") + ("" if r["verified"] == "yes" else " (unverified)")
            print(f"  {r['id'][:24]:24}{flag[:1]} {r['title'][:92]}{flag[1:]}")
    print("\n* = used by our results.  `fetch <id>` works for:", ", ".join(sorted(RECIPES)))


def cmd_meta(i):
    r = row(i)
    for k in ("title", "tier", "origin", "terms", "size", "n", "labels", "serves_tasks", "notes"):
        if r[k]:
            print(f"{k:13} {r[k]}")
    if r["tier"] == "request":
        print("\nThis set is on request. Agents never apply or write to anyone: the human lead decides and asks (docs/HUMAN_LEADS.md).")


def cmd_index(i):
    """File list only. Writes datasets/local/<id>/INDEX.json; downloads no data."""
    r = row(i)
    o, files = r["origin"], []
    if "zenodo" in o:
        rec = o.rstrip("/").split("zenodo.")[-1]
        j = get_json(f"https://zenodo.org/api/records/{rec}")
        files = [dict(name=f["key"], size=f["size"], url=f["links"]["self"]) for f in j.get("files", [])]
    elif "figshare" in o and i in RECIPES and RECIPES[i][0] == "figshare":
        _, art, ver, _ = RECIPES[i]
        files = [dict(name=f["name"], size=f["size"], url=f["download_url"]) for f in get_json(f"https://api.figshare.com/v2/articles/{art}/versions/{ver}")["files"]]
    elif "dryad" in o or "10.25349" in o:
        doi = o.split("doi.org/")[-1]
        j = get_json("https://datadryad.org/api/v2/datasets/" + urllib.parse.quote("doi:" + doi, safe=""))
        v = get_json("https://datadryad.org" + j["_links"]["stash:version"]["href"] + "/files")
        files = [dict(name=f["path"], size=f["size"]) for f in v["_embedded"]["stash:files"]]
    elif i in RECIPES and RECIPES[i][0] in ("zip", "manual") and RECIPES[i][1].endswith(".zip"):
        total, d = zip_directory(RECIPES[i][1])
        files = [dict(name=n, size=u, compressed=c) for n, _, c, _, u in d]
        print(f"remote zip: {total / 1e6:.0f} MB, {len(files)} members")
    else:
        sys.exit(f"{i}: no machine-readable index; open {o}")
    out = LOCAL / i; out.mkdir(parents=True, exist_ok=True)
    json.dump(dict(id=i, origin=o, files=files), open(out / "INDEX.json", "w"), indent=1)
    print(f"{len(files)} files, {sum(f.get('size', 0) for f in files) / 1e6:.1f} MB listed -> {out / 'INDEX.json'}")


def cmd_fetch(i):
    r = row(i)
    if r["tier"] in ("request", "reference-only"):
        return cmd_meta(i)
    if i not in RECIPES:
        sys.exit(f"{i}: no fetch recipe (not used by our results yet). `index {i}` lists its files; origin: {r['origin']}")
    out = LOCAL / i; out.mkdir(parents=True, exist_ok=True)
    kind, *a = RECIPES[i]
    if kind == "manual":
        out.rmdir() if not any(out.iterdir()) else None
        return print(f"{i}: not fetched automatically.\n  {a[1]}\n  Source: {a[0]}\n  Terms: {r['terms']}")
    if kind == "file":
        url, name = a
        spend(size_of(url), i)
        (out / name).write_bytes(get(url))
    elif kind == "figshare":
        art, ver, name = a
        f = next(f for f in get_json(f"https://api.figshare.com/v2/articles/{art}/versions/{ver}")["files"] if f["name"] == name)
        spend(f["size"], i)
        (out / name).write_bytes(get(f["download_url"]))
    elif kind == "zenodo":
        rec, names = a
        for f in get_json(f"https://zenodo.org/api/records/{rec}")["files"]:
            if f["key"] in names:
                spend(f["size"], i)
                (out / f["key"]).write_bytes(get(f["links"]["self"]))
    elif kind == "zip":
        url, prefixes = a
        _, d = zip_directory(url)
        want = [m for m in d if any(m[0].split("/", 1)[-1].startswith(p) or m[0].startswith(p) for p in prefixes) and not m[0].endswith("/")]
        spend(sum(m[2] for m in want), i)
        for name, off, csize, method, _ in want:
            p = out / name; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(zip_member(url, off, csize, method))
        print(f"{len(want)} of {len(d)} zip members read by range")
    elif kind == "git":
        import subprocess
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", a[0], str(out / "repo")], check=True)
    json.dump(dict(id=i, origin=r["origin"], terms=r["terms"], recipe=RECIPES[i], fetched=time.strftime("%Y-%m-%d")), open(out / "SOURCE.json", "w"), indent=1)
    print(f"{i}: done -> datasets/local/{i}/  ({used_bytes() / 1e6:.0f} MB of the 1.5 GB budget used)")


if __name__ == "__main__":
    a = sys.argv[1:] or ["list"]
    if a[0] == "list":
        cmd_list()
    elif a[0] in ("fetch", "index", "meta") and len(a) > 1:
        {"fetch": cmd_fetch, "index": cmd_index, "meta": cmd_meta}[a[0]](a[1])
    else:
        print(__doc__)
