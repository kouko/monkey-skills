#!/usr/bin/env python3
"""
tree-to-markdown-tables.py — in-place rewrite of the three
docs/nbs-tree-{monthly,quarterly,yearly}.md files from nested-bullet
format to per-top-category sectioned tables with a TOC.

Idempotent: parses the bullet form OR the table form (only the former
yields useful results). Normally run once after `probe-nbs-tree.py`
emits the bullet form. Not loaded at skill runtime.
"""
import re

FREQS = {"monthly": ("月度", 1, "fc982599aa684be7969d7b90b1bd0e84"),
         "quarterly": ("季度", 2, "a94b8b7365a94874968cabbe392cf679"),
         "yearly": ("年度", 3, "884c062607104a91967b22742537f44f")}

BASE = "/Users/kouko/GitHub/monkey-skills/investing-toolkit/skills/china-macro/docs"

LINE_RE = re.compile(r"^(\s*)- (📁|📄) (.+?) `\[([0-9a-f]+)\]`\s*$")

def parse(src):
    """Yield (depth, marker, name, uid) in tree order."""
    for line in open(src):
        m = LINE_RE.match(line.rstrip("\n"))
        if not m:
            continue
        spaces, marker, name, uid = m.groups()
        depth = len(spaces) // 2 + 1  # bullets at 0sp → depth 1
        yield depth, marker, name.strip(), uid

def emit(freq_key):
    label, code, root = FREQS[freq_key]
    src = f"{BASE}/nbs-tree-{freq_key}.md"
    nodes = list(parse(src))

    # Group into per-top-category buckets
    categories = []  # list of {name, uid, rows}
    current = None
    for depth, marker, name, uid in nodes:
        if depth == 1:
            current = {"name": name, "uid": uid, "rows": []}
            categories.append(current)
        else:
            current["rows"].append((depth, marker, name, uid))

    # Count totals
    # Simpler recount:
    total_leaves = sum(sum(1 for d,m,n,u in c["rows"] if m=="📄") for c in categories)
    total_folders = sum(sum(1 for d,m,n,u in c["rows"] if m=="📁") for c in categories)

    out = [
        f"# NBS {label}数据 — indicator tree (UUID lookup)\n\n",
        f"- **Root `_id`**: `{root}`\n",
        f"- **Tree walker `code`**: `{code}` (query param for `queryIndexTreeAsync`)\n",
        f"- **Captured**: 2026-04-18\n",
        f"- **Totals**: {total_leaves} leaves 📄, {total_folders} sub-folders 📁 across {len(categories)} top-level categories\n\n",
        "Each 📄 leaf row's UUID doubles as the `cid` value for "
        "`POST getEsDataByCidAndDt`. 深度欄位 = 節點在樹中的層級（1 = top-level; "
        "leaf 通常在 2-5 層之間）。\n\n",
        "---\n\n",
        "## 目錄\n\n",
    ]
    for c in categories:
        leaves_in_cat = sum(1 for _,m,_,_ in c["rows"] if m=="📄")
        # Markdown anchor: strip special chars, replace spaces with hyphens
        anchor = c["name"].lower()
        anchor = re.sub(r"\s+", "-", anchor)
        anchor = re.sub(r"[()（）]", "", anchor)
        out.append(f"- [{c['name']}](#{anchor}) — {leaves_in_cat} leaves\n")
    out.append("\n---\n\n")

    # Each category as a section + table
    for c in categories:
        out.append(f"## {c['name']}\n\n")
        out.append(f"**Catalog `_id`**: `{c['uid']}`\n\n")
        if not c["rows"]:
            out.append("_(no sub-tree)_\n\n")
            continue
        out.append("| 📁/📄 | 深度 | 名稱 | UUID |\n")
        out.append("|---|---|---|---|\n")
        for depth, marker, name, uid in c["rows"]:
            # Escape `|` in name if any
            safe = name.replace("|", "\\|")
            out.append(f"| {marker} | {depth} | {safe} | `{uid}` |\n")
        out.append("\n")

    dst = f"{BASE}/nbs-tree-{freq_key}.md"
    open(dst, "w").write("".join(out))
    print(f"{freq_key}: {total_leaves} leaves + {total_folders} folders → {dst}")

for key in FREQS:
    emit(key)
