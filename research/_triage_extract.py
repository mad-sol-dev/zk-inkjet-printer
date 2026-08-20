import re

path = "research/docs_rebuild/old_docs/reference/offset_catalog.md"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

rows = []
for l in lines:
    l = l.rstrip("\n")
    if not l.startswith("| `") and not l.startswith("| ZK") :
        continue
    parts = [p.strip() for p in l.strip("|").split("|")]
    if len(parts) < 4:
        continue
    rows.append(parts)

def find_va(text):
    m = re.search(r'0x[0-9A-Fa-f]{5,8}', text)
    return m.group(0) if m else None

out = []
for i, p in enumerate(rows, 1):
    filecol, offcol, desc, ev = p[0], p[1], p[2], p[3]
    # determine bin file
    if "BOOT.bin" in filecol:
        binf = "BOOT"
        va = find_va(offcol) or offcol
    elif "RES-HW" in filecol:
        binf = "RESHW"
        va = offcol
    else:
        binf = "APP"
        # va could be in filecol or offcol
        va = find_va(filecol) or find_va(offcol)
        if va is None:
            va = find_va(desc)
    out.append((i, binf, va, filecol[:40], offcol[:60], desc[:100]))

for row in out:
    print("%3d | %5s | %-12s | %s" % (row[0], row[1], row[2], row[5]))
