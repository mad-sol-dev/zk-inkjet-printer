#!/usr/bin/env python3
"""SD card layout and update path of the ZK-Inkjet printer as one HTML page, read-only.

    python3 tools/scripts/card_map.py              writes build/card_map.html
    python3 tools/scripts/card_map.py --check      only checks the cited register rows
    python3 tools/scripts/card_map.py --out _site/card_map.html --register-url index.html

Why it exists: the card holds the printer's own structures between a lot of
residue from earlier use, and the register states each piece in a separate
row. The maintainer asked on 2026-10-18 for one lasting picture of what lies
where, who writes it and who reads it, limited to what is established.

What it is not: a second status. The tables REGIONS and FLOW below restate
register rows in a few words, and every entry names the rows it rests on.
The page is written only if each cited row is decided, not superseded, not
refuted or a hypothesis, not O1, and has confidence >= 0.9. Otherwise the
script names the rows, writes nothing and exits 1 -- then the table has to
follow the register, not the other way round. Same input gives a byte-equal
file; the header names the commit instead of a time stamp.

Built after every commit by .githooks/post-commit (into build/, gitignored)
and on every push to master by .github/workflows/register-ansicht.yml, next
to the register view on GitHub Pages.
"""
import argparse
import csv
import html
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRUTH = os.path.join(ROOT, "research", "TRUTH.csv")
OUT = os.path.join(ROOT, "build", "card_map.html")
MIN_CONFIDENCE = 0.9

# Card regions from offset 0 to the end of the 4 GB card, top to bottom.
# kind: used    = in sdcard.minimal.img, which boots (CL-BOOT-REC-105)
#       foreign = firmware built for another SoC (CL-BOOT-REC-124)
#       residue = other leftovers, not needed to boot
REGIONS = [
    ("0x0000_0200", "Boot header + BOOT.bin (NANO)", "boot ROM reads, update writes", "used",
     ["CL-BOOT-REC-003", "CL-BOOT-REC-121", "CL-BOOT-REC-123"]),
    ("0x0010_0000", "Firmware ZK-INKJET, Aug 2023", "other SoC, residue", "foreign",
     ["CL-BOOT-REC-124", "CL-BOOT-REC-120"]),
    ("0x0050_0000", "UI data of ZK-INKJET", "other SoC, residue", "foreign",
     ["CL-BOOT-REC-124"]),
    ("0x0080_0000", "Target of .spiflash font updates", "not needed to boot", "residue",
     ["CL-BOOT-REC-123", "CL-BOOT-REC-105"]),
    ("0x0240_0000", "Firmware TIJSPS 800x480 + UI", "other SoC, residue", "foreign",
     ["CL-BOOT-REC-124"]),
    ("0x0300_0000", "APP.bin (NANO), Dec 2022", "BOOT reads, update writes", "used",
     ["CL-BOOT-REC-118", "CL-BOOT-REC-123", "CL-BOOT-REC-115"]),
    ("0x0380_0000", "Start logo frames (UI-QVGA)", "BOOT and APP read, update writes", "used",
     ["CL-DISPLAY-REC-121", "CL-DISPLAY-REC-102"]),
    ("0x03C0_0000", "Firmware CUTE, Aug 2023", "other SoC, residue", "foreign",
     ["CL-BOOT-REC-124"]),
    ("0x0400_0000", "Drive 0: fonts and resources", "APP reads", "used",
     ["CL-STORAGE-REC-006", "CL-STORAGE-REC-103"]),
    ("0x1890_0000", "ext4 remnants, Linux 2015", "in free space, residue", "residue",
     ["CL-STORAGE-REC-138"]),
    ("0x2400_0000", "Old USB volume USER", "deleted NANO bundle, Jan 2024", "residue",
     ["CL-STORAGE-REC-140", "CL-DISPLAY-REC-122"]),
    ("0x2800_0000", "Settings", "APP reads and writes", "used",
     ["CL-STORAGE-REC-111"]),
    ("0x2880_0000", "Document store, 100 slots", "APP reads and writes", "used",
     ["CL-STORAGE-REC-117", "CL-STORAGE-REC-111"]),
    ("0x2A61_4000", "Drive 3: MINI (USB)", "PC puts update files here", "used",
     ["CL-USB-REC-105", "CL-STORAGE-REC-131", "CL-STORAGE-REC-103"]),
    ("0x2E61_4000", "Rest of the card", "not used, not needed to boot", "residue",
     ["CL-STORAGE-REC-111", "CL-BOOT-REC-105"]),
]

KIND_LABEL = {
    "used": "used by the printer (in sdcard.minimal.img, which boots)",
    "foreign": "firmware built for another SoC",
    "residue": "other residue, not needed to boot",
}
KIND_CLAIMS = {"used": ["CL-BOOT-REC-105"], "foreign": ["CL-BOOT-REC-124"], "residue": ["CL-BOOT-REC-105"]}

# Update path (write) and boot chain (read): (key, title, subtitle, claims).
FLOW = [
    ("pc", "PC copies update files", "onto MINI, drive 3:", ["CL-STORAGE-REC-103", "CL-USB-REC-105"]),
    ("upd", "Update routine of APP", "print key at boot, or menu", ["CL-BOOT-REC-123"]),
    ("boot", "BOOT → 0x200", "fixed header in front", ["CL-BOOT-REC-123"]),
    ("app", "APP → 0x0300_0000", "only if BOOT succeeded", ["CL-BOOT-REC-123"]),
    ("ui", "UI → 0x0380_0000", "separate call", ["CL-BOOT-REC-123", "CL-DISPLAY-REC-121"]),
    ("del", "File is deleted", "after APP: watchdog reset", ["CL-BOOT-REC-123"]),
    ("rom", "Boot ROM", "reads header at 0x200", ["CL-BOOT-REC-121", "CL-BOOT-REC-003"]),
    ("bootbin", "BOOT.bin", "shows logo, loads APP", ["CL-BOOT-REC-118"]),
    ("appbin", "APP.bin", "runs at 0x0005_8000", ["CL-BOOT-REC-113", "CL-BOOT-REC-119"]),
]

# Facts the two pictures rest on, one line each.
FACTS = [
    ("BOOT.bin reads exactly 0x280000 bytes from card 0x0300_0000 into RAM 0x0005_8000, twice, "
     "compares the copies and jumps there; it never loads anything beyond those 0x280000 bytes.",
     ["CL-BOOT-REC-118", "CL-BOOT-REC-119"]),
    ("The update puts a fixed 32-byte boot header in front of BOOT.bin; its size field is always "
     "0x3100, whatever the file size.", ["CL-BOOT-REC-123"]),
    ("The update writes APP only after BOOT was written, deletes each file afterwards and resets "
     "through the watchdog after APP; MINI must hold both NANO files.", ["CL-BOOT-REC-123"]),
    ("There is no checksum, signature or decryption step; only the UI files are XORed with 0x4949.",
     ["CL-BOOT-REC-012"]),
    ("Only 0x200 is a live boot header; the five other copies of the template sit inside "
     "firmware copies.", ["CL-BOOT-REC-125"]),
]


def read_register(path=TRUTH):
    with open(path, encoding="utf-8", newline="") as fh:
        return {r["Claim_ID"]: r for r in csv.DictReader(fh)}


def cited():
    ids = []
    for _, _, _, _, claims in REGIONS:
        ids += claims
    for _, _, _, claims in FLOW:
        ids += claims
    for _, claims in FACTS:
        ids += claims
    for claims in KIND_CLAIMS.values():
        ids += claims
    return sorted(set(ids))


def problems(rows, ids):
    """Return one line per cited row that is not an established fact."""
    out = []
    for cid in ids:
        r = rows.get(cid)
        if r is None:
            out.append("%s: not in the register" % cid)
            continue
        why = []
        if (r.get("Superseded_By") or "").strip():
            why.append("superseded by %s" % r["Superseded_By"].strip())
        if (r.get("Decided") or "").strip().lower() != "yes":
            why.append("not decided")
        if (r.get("Status") or "").strip().lower() in ("refuted", "hypothesis", "open"):
            why.append("status %s" % r["Status"].strip())
        if (r.get("Oracle") or "").strip() == "O1":
            why.append("oracle O1 (derived only)")
        try:
            if float(r.get("Confidence") or 0) < MIN_CONFIDENCE:
                why.append("confidence %s < %.2f" % (r.get("Confidence"), MIN_CONFIDENCE))
        except ValueError:
            why.append("confidence %r unreadable" % r.get("Confidence"))
        if why:
            out.append("%s: %s" % (cid, ", ".join(why)))
    return out


def commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def esc(s):
    return html.escape(s, quote=True)


def links(claims, rows, reg):
    return " ".join('<a class="cid" href="%s#%s" title="%s">%s</a>'
                    % (esc(reg), esc(c), esc(rows[c].get("Topic", "")), esc(c)) for c in claims)


def map_html(rows, reg):
    lines = []
    for addr, title, role, kind, claims in REGIONS:
        lines.append('<div class="row %s"><code class="addr">%s</code><div class="box"><b>%s</b><span>%s</span>'
                     '</div><div class="cl">%s</div></div>'
                     % (kind, esc(addr), esc(title), esc(role), links(claims, rows, reg)))
    legend = "".join('<li class="%s"><span class="sw"></span>%s <span class="lc">%s</span></li>'
                     % (k, esc(v), links(KIND_CLAIMS[k], rows, reg)) for k, v in KIND_LABEL.items())
    return '<ul class="legend">%s</ul>\n<div class="map">\n%s\n</div>' % (legend, "\n".join(lines))


def flow_svg(reg):
    f = {k: (t, s, c) for k, t, s, c in FLOW}
    # (key, x, y, w, kind)
    boxes = [("pc", 200, 30, 280, "n"), ("upd", 200, 114, 280, "n"),
             ("boot", 40, 206, 180, "w"), ("app", 250, 206, 180, "w"), ("ui", 460, 206, 180, "w"),
             ("del", 200, 298, 280, "n"),
             ("rom", 40, 418, 180, "r"), ("bootbin", 250, 418, 180, "r"), ("appbin", 460, 418, 180, "r")]
    arrows = [(340, 86, 340, 112), (300, 170, 132, 204), (340, 170, 340, 204), (380, 170, 548, 204),
              (130, 262, 288, 296), (340, 262, 340, 296), (550, 262, 392, 296),
              (220, 446, 248, 446), (430, 446, 458, 446)]
    p = ['<svg class="flow" viewBox="0 0 680 500" role="img" aria-labelledby="flow-t">'
         '<title id="flow-t">Update path (write) and boot chain (read)</title>'
         '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" '
         'orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" '
         'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>']
    for x1, y1, x2, y2 in arrows:
        p.append('<line class="ar" x1="%d" y1="%d" x2="%d" y2="%d" marker-end="url(#ah)"/>' % (x1, y1, x2, y2))
    p.append('<path class="ar" d="M340 354 L340 386 L130 386 L130 416" fill="none" marker-end="url(#ah)"/>')
    for key, x, y, w, kind in boxes:
        t, s, c = f[key]
        p.append('<a href="%s#%s"><g class="fb %s"><rect x="%d" y="%d" width="%d" height="56" rx="8"/>'
                 '<text class="ft" x="%d" y="%d">%s</text><text class="fs" x="%d" y="%d">%s</text></g></a>'
                 % (esc(reg), esc(c[0]), kind, x, y, w, x + w // 2, y + 19, esc(t), x + w // 2, y + 38, esc(s)))
    p.append("</svg>")
    return "".join(p)


CSS = """
:root{--bg:#fbfaf7;--tx:#1f2328;--tx2:#5b6169;--rand:#e1ddd3;--akz:#2456b8;
--used:#e1f5ee;--used-r:#0f6e56;--used-t:#085041;--for:#faece7;--for-r:#993c1d;--for-t:#712b13;
--res:#f1efe8;--res-r:#5f5e5a;--res-t:#444441;--wr:#e1f5ee;--rd:#eeedfe;--rd-r:#534ab7;--rd-t:#3c3489}
@media (prefers-color-scheme:dark){:root{--bg:#15171a;--tx:#e6e3dc;--tx2:#a2a8b0;--rand:#33383e;--akz:#7fa7ff;
--used:#085041;--used-r:#5dcaa5;--used-t:#e1f5ee;--for:#712b13;--for-r:#f0997b;--for-t:#faece7;
--res:#444441;--res-r:#b4b2a9;--res-t:#f1efe8;--rd:#3c3489;--rd-r:#afa9ec;--rd-t:#eeedfe}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:16px}
h1{font-size:1.35rem;font-weight:600;margin:.4rem 0}h2{font-size:1.1rem;font-weight:600;margin:1.6rem 0 .5rem}
p.kopf{color:var(--tx2);margin:.2rem 0 1rem}a{color:var(--akz)}
code,.cid{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.82rem}
.legend{list-style:none;padding:0;margin:0 0 .8rem;display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.88rem;color:var(--tx2)}
.legend li{display:flex;align-items:center;gap:6px}.sw{display:inline-block;width:14px;height:14px;border-radius:3px}
.legend .used .sw{background:var(--used);border:1px solid var(--used-r)}
.legend .foreign .sw{background:var(--for);border:1px dashed var(--for-r)}
.legend .residue .sw{background:var(--res);border:1px dashed var(--res-r)}
.map{display:grid;gap:6px}
.row{display:grid;grid-template-columns:7.2rem 1fr 15rem;gap:10px;align-items:center}
.addr{color:var(--tx2)}
.box{display:flex;justify-content:space-between;gap:12px;padding:8px 14px;border-radius:5px;min-height:40px;align-items:center}
.box span{font-size:.85rem}
.used .box{background:var(--used);border:1px solid var(--used-r);color:var(--used-t)}
.foreign .box{background:var(--for);border:1px dashed var(--for-r);color:var(--for-t)}
.residue .box{background:var(--res);border:1px dashed var(--res-r);color:var(--res-t)}
.cl{display:flex;flex-wrap:wrap;gap:2px 8px}
@media (max-width:760px){.row{grid-template-columns:1fr}.cl{padding-left:2px}}
svg.flow{width:100%;max-width:680px;height:auto;display:block}
.fb rect{stroke-width:.8}.fb.n rect{fill:var(--res);stroke:var(--res-r)}.fb.n text{fill:var(--res-t)}
.fb.w rect{fill:var(--used);stroke:var(--used-r)}.fb.w text{fill:var(--used-t)}
.fb.r rect{fill:var(--rd);stroke:var(--rd-r)}.fb.r text{fill:var(--rd-t)}
.ft{font-size:14px;font-weight:600;text-anchor:middle;dominant-baseline:central}
.fs{font-size:12px;text-anchor:middle;dominant-baseline:central}
.ar{stroke:var(--tx2);stroke-width:1.3}
ul.steps,ul.facts{padding-left:1.1rem}ul.steps li,ul.facts li{margin:.2rem 0}
"""


def page(rows, reg, rev):
    steps = "".join("<li><b>%s</b> (%s): %s</li>" % (esc(t), esc(s), links(c, rows, reg)) for _, t, s, c in FLOW)
    facts = "".join("<li>%s %s</li>" % (esc(t), links(c, rows, reg)) for t, c in FACTS)
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZK-Inkjet: SD card layout and update path</title><style>%s</style></head>
<body><main>
<h1>ZK-Inkjet: SD card layout and update path</h1>
<p class="kopf">Derived from <code>research/TRUTH.csv</code> at commit <code>%s</code> by
<code>tools/scripts/card_map.py</code>. Each entry links to the register rows it rests on; only decided rows
with confidence &ge; %.2f and no O1 rating are cited. Card offsets top to bottom, not to scale.
<a href="%s">Register view</a></p>
<h2>What lies where on the 4 GB card</h2>
%s
<h2>Update path (write) and boot chain (read)</h2>
%s
<ul class="steps">%s</ul>
<h2>Facts behind the two pictures</h2>
<ul class="facts">%s</ul>
</main></body></html>
""" % (CSS, esc(rev), MIN_CONFIDENCE, esc(reg), map_html(rows, reg), flow_svg(reg), steps, facts)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SD card layout and update path as HTML, from TRUTH.csv")
    ap.add_argument("--out", default=OUT, help="output file (default build/card_map.html)")
    ap.add_argument("--register-url", default="truth_ansicht.html",
                    help="link target of the register view; claim IDs are appended as #anchor")
    ap.add_argument("--check", action="store_true", help="only check the cited rows, write nothing")
    ap.add_argument("--leise", action="store_true", help="print nothing on success (for hooks)")
    a = ap.parse_args(argv)
    rows = read_register()
    bad = problems(rows, cited())
    if bad:
        print("card_map: not written -- cited rows are not established facts any more:", file=sys.stderr)
        for line in bad:
            print("  " + line, file=sys.stderr)
        print("Update REGIONS/FLOW/FACTS in tools/scripts/card_map.py to the register.", file=sys.stderr)
        return 1
    if a.check:
        if not a.leise:
            print("card_map: %d cited rows, all established." % len(cited()))
        return 0
    text = page(rows, a.register_url, commit())
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    tmp = a.out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, a.out)
    if not a.leise:
        print("card_map: %s written (%d cited rows)." % (os.path.relpath(a.out, ROOT), len(cited())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
