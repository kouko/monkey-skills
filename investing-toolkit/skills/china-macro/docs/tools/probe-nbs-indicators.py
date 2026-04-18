#!/usr/bin/env python3
"""
Walk all 3 tree MD files for leaf cids, call queryIndicatorsByCid for each,
cache per-cid JSON (resumable), and produce aggregate JSON+Markdown.

Output:
  /tmp/nbs-probe-cache/{cid}.json  — per-cid cache (resume-safe)
  /tmp/nbs-indicators-final.json   — aggregate map { cid: {...} }
  /tmp/nbs-indicators-final.md     — human-readable summary
"""
import json, re, sys, time, urllib.request, http.cookiejar
from pathlib import Path

DOCS = Path("/Users/kouko/GitHub/monkey-skills/investing-toolkit/skills/china-macro/docs")
CACHE = Path("/tmp/nbs-probe-cache")
CACHE.mkdir(exist_ok=True)

API = "https://data.stats.gov.cn/dg/website/publicrelease/web/external/new/queryIndicatorsByCid"
HOME = "https://data.stats.gov.cn/dg/website/page.html"
UA = "Mozilla/5.0 Chrome/147"

# Throttle. Default 1.5s between API calls. Adaptive on WAF.
BASE_DELAY = 0.5
WAF_INITIAL_BACKOFF = 60   # seconds after first WAF hit
WAF_MAX_BACKOFF = 600       # cap at 10 min

LEAF_RE = re.compile(r"^\|\s*📄\s*\|\s*\d+\s*\|\s*(.+?)\s*\|\s*`([0-9a-f]+)`\s*\|")

def session():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", UA), ("Accept", "application/json")]
    op.open(HOME, timeout=20).read()
    return op

def leaves_from(md_path, freq, category_label):
    """Parse the tree MD: return [(cid, path, freq)].

    Path = 'freq → top_category → ... → leaf name'. We walk the file
    linearly tracking the latest folder per depth.
    """
    rows = []
    folder_stack = [category_label]  # index = depth - 1
    current_top = None
    header_re = re.compile(r"^##\s+(.+)$")
    folder_re = re.compile(r"^\|\s*📁\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*`([0-9a-f]+)`\s*\|")
    leaf_re = re.compile(r"^\|\s*📄\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*`([0-9a-f]+)`\s*\|")

    for line in Path(md_path).read_text().splitlines():
        # Top-level section header
        m = header_re.match(line)
        if m and m.group(1) != "目錄":
            current_top = m.group(1)
            folder_stack = [freq, current_top]
            continue
        mf = folder_re.match(line)
        if mf:
            depth = int(mf.group(1))
            name = mf.group(2)
            folder_stack = folder_stack[: depth + 1]  # slice to parent path
            while len(folder_stack) < depth + 1:
                folder_stack.append("?")
            folder_stack.append(name)
            continue
        ml = leaf_re.match(line)
        if ml:
            depth = int(ml.group(1))
            name = ml.group(2)
            uid = ml.group(3)
            parent = folder_stack[: depth + 1]
            path = " → ".join(parent[: depth + 1] + [name])
            rows.append({"cid": uid, "path": path, "freq": freq, "name": name})
    return rows

def fetch_indicators(op, cid, retries=3):
    url = f"{API}?cid={cid}&dt=&name="
    last_err = None
    for attempt in range(retries):
        try:
            raw = op.open(url, timeout=25).read()
        except Exception as e:
            last_err = f"HTTP:{type(e).__name__}:{e}"
            time.sleep(2 + attempt * 2)
            continue
        text = raw.decode("utf-8", errors="replace")
        if text.strip().startswith("<"):
            return None, "WAF"
        try:
            d = json.loads(text)
        except Exception as e:
            return None, f"PARSE:{e}"
        if not d.get("success"):
            return None, f"API-FAIL:{d.get('message', '?')}"
        lst = d.get("data", {}).get("list") or []
        return lst, None
    return None, last_err or "HTTP:unknown"

def probe_all(leaves, op):
    total = len(leaves)
    done_at_start = sum(1 for lf in leaves if (CACHE / f"{lf['cid']}.json").exists())
    print(f"[probe] {total} leaves, {done_at_start} already cached, starting from {done_at_start + 1}", flush=True)
    backoff = 0
    probed = 0
    waf_hits = 0
    for i, lf in enumerate(leaves, 1):
        cf = CACHE / f"{lf['cid']}.json"
        if cf.exists():
            continue
        # Throttle
        time.sleep(BASE_DELAY + backoff)
        lst, err = fetch_indicators(op, lf["cid"])
        if err == "WAF":
            waf_hits += 1
            wait = min(WAF_INITIAL_BACKOFF * (2 ** (waf_hits - 1)), WAF_MAX_BACKOFF)
            print(f"[probe] WAF at {i}/{total} cid={lf['cid'][:8]}. Sleeping {wait}s then retry session.", flush=True)
            time.sleep(wait)
            op = session()
            lst, err = fetch_indicators(op, lf["cid"])
            if err == "WAF":
                print(f"[probe] WAF persists. Aborting — can resume later.", flush=True)
                return op, probed, waf_hits
        if err:
            cf.write_text(json.dumps({"cid": lf["cid"], "error": err, "path": lf["path"]}, ensure_ascii=False))
            print(f"[probe] ERROR {i}/{total} cid={lf['cid'][:8]}: {err}", flush=True)
            continue
        payload = {
            "cid": lf["cid"],
            "path": lf["path"],
            "freq": lf["freq"],
            "leaf_name": lf["name"],
            "indicators": [
                {
                    "_id": r.get("_id"),
                    "name": r.get("i_showname", r.get("_name", "?")).strip(),
                    "group": r.get("_name", "?").strip(),
                    "unit_code": r.get("du"),
                    "unit_name": r.get("du_name"),
                    "order": r.get("ds_order"),
                    "kj1_name": r.get("kj1_name"),
                }
                for r in lst
            ],
        }
        cf.write_text(json.dumps(payload, ensure_ascii=False))
        probed += 1
        if probed % 50 == 0:
            print(f"[probe] {i}/{total} cached ({probed} new this run, {waf_hits} WAF hits)", flush=True)
        if backoff > 0 and probed % 20 == 0:
            backoff = max(backoff - 0.1, 0)  # decay after good runs
    print(f"[probe] COMPLETE. {probed} newly cached. {waf_hits} WAF events.", flush=True)
    return op, probed, waf_hits

def aggregate():
    all_cids = {}
    for cf in CACHE.glob("*.json"):
        try:
            d = json.loads(cf.read_text())
            all_cids[d["cid"]] = d
        except Exception:
            pass
    return all_cids

def render_markdown(all_cids):
    # Group by freq + top category
    groups = {}
    for cid, d in all_cids.items():
        if "error" in d:
            continue
        freq = d.get("freq", "?")
        top = d["path"].split(" → ")[1] if " → " in d["path"] else "?"
        groups.setdefault((freq, top), []).append(d)

    lines = ["# NBS indicator UUID catalog (cid + indicator_ids)\n\n"]
    lines.append(f"**Captured**: {time.strftime('%Y-%m-%d')}\n")
    lines.append(f"**Total cids probed**: {len(all_cids)}\n")
    total_ind = sum(len(d.get('indicators', [])) for d in all_cids.values() if 'error' not in d)
    lines.append(f"**Total indicators**: {total_ind}\n\n")
    lines.append("Each cid section shows that leaf's `indicatorIds[]` values for `POST getEsDataByCidAndDt`.\n\n")
    for (freq, top), items in sorted(groups.items()):
        lines.append(f"\n## {freq} / {top}  ({len(items)} tables)\n")
        for d in sorted(items, key=lambda x: x["path"]):
            lines.append(f"\n### {d['leaf_name']}\n\n")
            lines.append(f"- **cid**: `{d['cid']}`\n")
            lines.append(f"- **Path**: {d['path']}\n")
            lines.append(f"- **Indicators**: {len(d['indicators'])}\n\n")
            if d["indicators"]:
                lines.append("| indicator_id | 名稱 | 單位 |\n|---|---|---|\n")
                for r in d["indicators"]:
                    name = (r["name"] or "?").replace("|", "\\|")
                    unit = r.get("unit_name") or ""
                    lines.append(f"| `{r['_id']}` | {name} | {unit} |\n")
    return "".join(lines)

def main():
    leaves_m = leaves_from(DOCS / "nbs-tree-monthly.md", "月度", "月度")
    leaves_q = leaves_from(DOCS / "nbs-tree-quarterly.md", "季度", "季度")
    leaves_y = leaves_from(DOCS / "nbs-tree-yearly.md", "年度", "年度")
    leaves = leaves_m + leaves_q + leaves_y
    print(f"[main] total leaves: {len(leaves)} = {len(leaves_m)} monthly + {len(leaves_q)} quarterly + {len(leaves_y)} yearly", flush=True)
    op = session()
    probe_all(leaves, op)

    all_cids = aggregate()
    Path("/tmp/nbs-indicators-final.json").write_text(json.dumps(all_cids, ensure_ascii=False, indent=2))
    Path("/tmp/nbs-indicators-final.md").write_text(render_markdown(all_cids))
    print(f"[main] DONE. JSON={len(all_cids)} cids → /tmp/nbs-indicators-final.json", flush=True)
    print(f"[main] MD → /tmp/nbs-indicators-final.md", flush=True)

if __name__ == "__main__":
    main()
