import re, sys

path = "research/docs_rebuild/old_docs/reference/offset_catalog.md"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

rows = []
for i, l in enumerate(lines):
    l = l.rstrip("\n")
    if not l.startswith("|"):
        continue
    parts = [p.strip() for p in l.strip("|").split("|")]
    if len(parts) < 4:
        continue
    if parts[0].lower() in ("file",) or set(parts[1]) <= set("-: "):
        continue
    rows.append((i+1, parts))

print("TOTAL ROWS:", len(rows))
for ln, p in rows:
    print(ln, "||".join(p))
