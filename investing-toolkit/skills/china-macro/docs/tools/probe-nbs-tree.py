#!/usr/bin/env python3
"""
probe-nbs-tree.py — walk NBS `queryIndexTreeAsync` for all three
frequencies (monthly, quarterly, yearly) and emit plain-text tree
listings to /tmp/nbs-tree-{monthly,quarterly,yearly}.txt.

Output format is `{indent}{📁|📄} {name}  [{uuid}]` — use
`tree-to-markdown-tables.py` downstream to convert to the
per-category sectioned-table markdown committed under docs/.

See tools/README.md for when to re-run (typically every ~5 years on
NBS base-period revisions). Not loaded at skill runtime.
"""
import json, time, urllib.request, http.cookiejar, sys

API = "https://data.stats.gov.cn/dg/website/publicrelease/web/external/new/queryIndexTreeAsync"
HOME = "https://data.stats.gov.cn/dg/website/page.html"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-Agent","Mozilla/5.0 Chrome/147"),("Accept","application/json")]
opener.open(HOME, timeout=20).read()

def kids(pid, code, tries=4):
    for i in range(tries):
        try:
            raw = opener.open(f"{API}?pid={pid}&code={code}", timeout=25).read()
            if not raw:
                time.sleep(5); continue
            text = raw.decode("utf-8", errors="replace")
            if text.strip().startswith("<"):
                # WAF challenge — back off
                wait = 30 + i*30
                print(f"    WAF on pid={pid[:8]}, backoff {wait}s", flush=True)
                time.sleep(wait); continue
            return json.loads(text)["data"] or []
        except Exception as e:
            print(f"    retry {i+1}/{tries}: {e}", flush=True)
            time.sleep(5)
    return []

roots = {1: ("fc982599aa684be7969d7b90b1bd0e84", "月度数据"),
         2: ("a94b8b7365a94874968cabbe392cf679", "季度数据"),
         3: ("884c062607104a91967b22742537f44f", "年度数据")}

def walk(pid, code, depth, max_depth, out, counter, delay):
    if depth > max_depth: return
    for n in kids(pid, code):
        leaf = n.get("isLeaf")
        nid = n.get("_id","?")
        name = n.get("name","").strip()
        marker = "📄" if leaf else "📁"
        out.write("  "*depth + f"{marker} {name}  [{nid}]\n")
        counter[0] += 1
        if not leaf and nid:
            time.sleep(delay)
            walk(nid, code, depth+1, max_depth, out, counter, delay)

for code, (root, label) in roots.items():
    path = f"/tmp/nbs-tree-{'monthly' if code==1 else 'quarterly' if code==2 else 'yearly'}.txt"
    counter = [0]
    delay = 0.35  # be polite
    with open(path, "w") as f:
        f.write(f"# NBS {label} (code={code}) — name + UUID\n")
        f.write(f"# Root: {root}\n")
        f.write(f"# Captured: 2026-04-18\n")
        f.write(f"# Use leaf _id as `cid` in POST getEsDataByCidAndDt\n\n")
        walk(root, code, 1, 5, f, counter, delay)
    print(f"{label}: {counter[0]} nodes → {path}", flush=True)
