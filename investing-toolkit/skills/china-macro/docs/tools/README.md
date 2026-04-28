# china-macro / docs / tools

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

One-shot admin scripts used to capture the NBS indicator catalog under
`docs/`. These are NOT part of the runtime skill — only run when NBS
publishes a new base-period segment (every ~5 years) or when the
`queryIndicatorsByCid` response schema changes.

## Scripts

| Script | Purpose | Typical runtime |
|---|---|---|
| `probe-nbs-tree.py` | Walk `queryIndexTreeAsync` recursively for all 3 frequencies; write `nbs-tree-{monthly,quarterly,yearly}.md` (folder+leaf UUID catalog) | ~15-20 min |
| `probe-nbs-indicators.py` | For every leaf cid in the three trees, call `queryIndicatorsByCid`; cache per-cid JSON; emit aggregated `nbs-indicators-{frequency}.{json,md}` | ~60-90 min |
| `tree-to-markdown-tables.py` | Convert nested-bullet tree output to per-category sectioned tables (used once to migrate format) | seconds |

## When to re-run

### Every ~5 years (base-period revision)
NBS publishes methodology revisions on a 5-year cadence. In 2031 the
current `(2026-)` CPI/PPI series will almost certainly freeze into
`(2026-2030)` and a new `(2031-)` series will appear with fresh UUIDs.
Re-run both `probe-nbs-tree.py` and `probe-nbs-indicators.py` to pick up
the new leaves.

### After confirmed upstream change
If a skill user reports `nbs_client.py` returning stale/empty data,
verify by running one `queryIndicatorsByCid` call manually. If schema
drifted, re-run the probe scripts.

### Ad-hoc: when adding a new preset
Just grep the existing `docs/nbs-indicators-*.md` for the concept you
want — indicator UUIDs are already captured. No re-run needed unless
the indicator is genuinely new to NBS.

## Prerequisites

- Python 3.9+ (stdlib only — no external deps)
- Outbound HTTPS to `data.stats.gov.cn`
- **NordVPN or similar**: verified reachable from Taiwan/Anthropic
  infrastructure via VPN. WAF trips on bulk traversal but the scripts
  handle exponential backoff + session rotation.

## Usage

```bash
# Tree structure (captures folder/leaf hierarchy + catalog IDs)
python3 probe-nbs-tree.py
# → writes /tmp/nbs-tree-{monthly,quarterly,yearly}.txt
# → manually copy + apply tree-to-markdown-tables.py to produce
#   docs/nbs-tree-*.md

# Indicator UUIDs for every leaf (takes 60-90 min)
python3 probe-nbs-indicators.py
# → writes /tmp/nbs-probe-cache/{cid}.json (resumable)
# → aggregates to /tmp/nbs-indicators-final.{json,md}
# → manually split by frequency + copy to docs/
```

## WAF / rate-limit notes

`probe-nbs-indicators.py` was tuned during the 2026-04-18 capture:

- Base throttle: 0.5s between requests when running via NordVPN (IP in
  the `194.233.x.x` / M247 range observed working). On a residential
  non-VPN IP the safer setting is 1.5s.
- Session priming: always GET the homepage first to establish a
  `JSESSIONID` cookie; all subsequent API calls reuse it.
- WAF detection: response body starting with `<` means WZWS JS
  challenge triggered. The script backs off exponentially (60s, 120s,
  240s, ..., max 10 min) and rotates the session before retrying.
- HTTP `RemoteDisconnected` / transient `URLError`: retry 3 times with
  linear backoff (2s, 4s, 6s).
- One full-catalog run during 2026-04-18 completed with 0 WAF events
  and 1 transient network error (the error was retried manually for
  completeness).

## Output schema (for consumers)

```json
{
  "<cid-uuid>": {
    "cid": "<cid-uuid>",
    "path": "月度 → 价格指数 → ... → 全国居民消费价格分类指数 (2026-)",
    "freq": "月度",
    "leaf_name": "全国居民消费价格分类指数 (2026-)",
    "indicators": [
      {
        "_id": "<indicator-uuid>",
        "name": "居民消费价格指数 (上年同月=100)",
        "group": "居民消费价格指数",
        "unit_code": "<unit-uuid>",
        "unit_name": "%",
        "order": 1,
        "kj1_name": "上年同月=100"
      }
    ]
  }
}
```

Error entries have `{"cid": "...", "error": "...", "path": "..."}`
instead of the normal shape.
